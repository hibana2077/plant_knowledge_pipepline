from langchain_groq import ChatGroq
from langchain_community.document_loaders import WikipediaLoader
from langchain.text_splitter import TokenTextSplitter
from langchain_core.messages.ai import AIMessage
from langchain_community.graphs.graph_document import (
    Node as BaseNode,
    Relationship as BaseRelationship,
    GraphDocument,
)
import os
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from typing import List, Dict, Any, Optional
from langchain.pydantic_v1 import Field, BaseModel
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.graphs.neo4j_graph import Neo4jGraph
from langchain_core.exceptions import OutputParserException
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

GROQ_API_KEY = os.getenv("GROQ_API_KEY","") # allow multiple keys -> key1,key2,key3 -> split(",") -> ["key1", "key2", "key3"]
GROQ_API_KEY_LIST = GROQ_API_KEY.split(",") if GROQ_API_KEY else []
NEO4J_URL = os.getenv("NEO4J_URL", "bolt://210.240.160.212:7687") #note: use bolt protocol
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "plant_knowledge")

if not GROQ_API_KEY_LIST:raise ValueError("GROQ_API_KEY is required")
os.environ["GROQ_API_KEY"] = GROQ_API_KEY_LIST[0]
llm = ChatGroq(temperature=0, api_key=GROQ_API_KEY_LIST[0],model_name="mixtral-8x7b-32768")

graph = Neo4jGraph(
    url=NEO4J_URL,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
)

# Define KnowledgeGraph data structure

class Property(BaseModel):
  """A single property consisting of key and value"""
  key: str = Field(..., description="key")
  value: str = Field(..., description="value")

class Node(BaseNode):
    properties: Optional[List[Property]] = Field(
        None, description="List of node properties")

class Relationship(BaseRelationship):
    properties: Optional[List[Property]] = Field(
        None, description="List of relationship properties"
    )

class KnowledgeGraph(BaseModel):
    """Generate a knowledge graph with entities and relationships."""
    nodes: List[Node] = Field(
        ..., description="List of nodes in the knowledge graph")
    rels: List[Relationship] = Field(
        ..., description="List of relationships in the knowledge graph"
    )

# Define the function to map the KnowledgeGraph data structure to the graph document data structure

def format_property_key(s: str) -> str:
    words = s.split()
    if not words:
        return s
    first_word = words[0].lower()
    capitalized_words = [word.capitalize() for word in words[1:]]
    return "".join([first_word] + capitalized_words)

def props_to_dict(props) -> dict:
    """Convert properties to a dictionary."""
    properties = {}
    if not props:
      return properties
    if type(props) == dict and props:
        for k, v in props.items():
            properties[format_property_key(k)] = v
        return properties
    for p in props:
        properties[format_property_key(p['key'])] = p['value']
    return properties

def map_to_base_node(node: Node) -> BaseNode:
    """Map the KnowledgeGraph Node to the base Node."""
    print(f"Node: {node} \t\n")
    properties = props_to_dict(node['properties']) if type(node) == dict and 'properties' in node.keys() else {}
    # Add name property for better Cypher statement generation
    properties["name"] = node['id'].title() if type(node) == dict and node['id'] else ""
    try:
        return BaseNode(
            id=node['id'].title(), type=node["type"].capitalize(), properties=properties
        )
    except AttributeError:
        return BaseNode(
            id=node, type="Node", properties=properties
        )
    except TypeError:
        return BaseNode(
            id=node, type="Node", properties=properties
        )

def map_to_base_relationship(rel: Relationship) -> BaseRelationship:
    """Map the KnowledgeGraph Relationship to the base Relationship."""
    print("map to base rel:",rel, type(rel), "\t\n")
    # print(f"Rel.type: {rel['type']}")
    source = map_to_base_node(rel["source"])
    target = map_to_base_node(rel["target"])
    properties = props_to_dict(rel["properties"]) if "properties" in rel.keys() else {}
    try:
        return BaseRelationship(
            source=source, target=target, type=rel.type, properties=properties
        )
    except AttributeError:
        return BaseRelationship(
            source=source, target=target, type=rel["type"], properties=properties
        )

def get_extraction_chain(
    allowed_nodes: Optional[List[str]] = None,
    allowed_rels: Optional[List[str]] = None
    ):
    # Rule
    RULE = f"""# Knowledge Graph Instructions for Language Model
    ## 1. Overview
    You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph.
    - **Nodes** represent entities and concepts. They're akin to Wikipedia nodes.
    - The aim is to achieve simplicity and clarity in the knowledge graph, making it accessible for a vast audience.
    ## 2. Labeling Nodes
    - **Consistency**: Ensure you use basic or elementary types for node labels.
    - For example, when you identify an entity representing a person, always label it as **"person"**. Avoid using more specific terms like "mathematician" or "scientist".
    - **Node IDs**: Never utilize integers as node IDs. Node IDs should be names or human-readable identifiers found in the text.
    ## 3. Handling Numerical Data and Dates
    - Numerical data, like age or other related information, should be incorporated as attributes or properties of the respective nodes.
    - **No Separate Nodes for Dates/Numbers**: Do not create separate nodes for dates or numerical values. Always attach them as attributes or properties of nodes.
    - **Property Format**: Properties must be in a key-value format.
    - **Quotation Marks**: Never use escaped single or double quotes within property values.
    - **Naming Convention**: Use camelCase for property keys, e.g., `birthDate`.
    ## 4. Coreference Resolution
    - **Maintain Entity Consistency**: When extracting entities, it's vital to ensure consistency.
    If an entity, such as "John Doe", is mentioned multiple times in the text but is referred to by different names or pronouns (e.g., "Joe", "he"),
    always use the most complete identifier for that entity throughout the knowledge graph. In this example, use "John Doe" as the entity ID.
    Remember, the knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial.
    ## 5. Strict Compliance
    Adhere to the rules strictly. Non-compliance will result in termination.
    ## 6. Forbidden Formats
    - **No HTML**: Do not include HTML tags in the nodes or relationships.
    - **No Markdown**: Do not include markdown syntax in the nodes or relationships.
    - **No Skip**: Do not skip any part of the text. Extract all relevant information.
    - **Invalid json output**: Do not provide invalid json output.
    ## 7. Additional Guidelines
    - **Start Formatting**: Start with "{", end with "}".
    """
    parser = JsonOutputParser(pydantic_object=KnowledgeGraph)
    prompt = PromptTemplate(
        template=RULE + "Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | llm
    return chain, parser

def extract_and_store_graph(
    document: Document,
    nodes:Optional[List[str]] = None,
    rels:Optional[List[str]]=None) -> None:
    extract_chain,parser = get_extraction_chain(nodes, rels)
    print("invoke extract_chain")
    data:AIMessage = extract_chain.invoke({"query": document.page_content})
    data:str = data.content
    try:
        data = parser.parse(data)
    except OutputParserException:
        # use llm to make data structure more clear
        new_prompt = PromptTemplate(
            template="Organize the input text into the correct json format. \n{data}\n",
            input_variables=["data"],
        )
        new_chain = new_prompt | llm | parser
        data:AIMessage = new_chain.invoke({"data": data})
        data:str = data.content
        data = parser.parse(data)
    print("\n\n")
    # Construct a graph document
    graph_document = GraphDocument(
      nodes = [map_to_base_node(node) for node in data['nodes']],
      relationships = [map_to_base_relationship(rel) for rel in data['rels']],
      source = document
    )
    # graph.add_graph_documents([graph_document])
    return graph_document

# Read the wikipedia article
raw_documents = WikipediaLoader(query="Apple inc").load()
# Define chunking strategy
text_splitter = TokenTextSplitter(chunk_size=2048, chunk_overlap=24)
# Only take the first the raw_documents
documents:list[Document] = text_splitter.split_documents(raw_documents[:3])
import time
for i, d in enumerate(documents):
    s = time.time()
    print(f"Processing document {i+1}/{len(documents)}")
    extract_and_store_graph(d)
    print(f"Time taken: {time.time()-s:.2f} seconds")