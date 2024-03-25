'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-03-07 19:42:28
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-03-25 18:18:35
FilePath: \plant_knowledge_pipepline\src\data_transform_node\main.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from langchain_groq import ChatGroq
from langchain_community.document_loaders import ArxivLoader
from langchain.text_splitter import TokenTextSplitter
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

GROQ_API_KEY = os.getenv("GROQ_API_KEY","") # allow multiple keys -> key1,key2,key3 -> split(",") -> ["key1", "key2", "key3"]
GROQ_API_KEY_LIST = GROQ_API_KEY.split(",") if GROQ_API_KEY else []
NEO4J_URL = os.getenv("NEO4J_URL", "bolt://localhost:7687")
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
    for p in props:
        properties[format_property_key(p.key)] = p.value
    return properties

def map_to_base_node(node: Node) -> BaseNode:
    """Map the KnowledgeGraph Node to the base Node."""
    properties = props_to_dict(node.properties) if node.properties else {}
    # Add name property for better Cypher statement generation
    properties["name"] = node.id.title()
    return BaseNode(
        id=node.id.title(), type=node.type.capitalize(), properties=properties
    )

def map_to_base_relationship(rel: Relationship) -> BaseRelationship:
    """Map the KnowledgeGraph Relationship to the base Relationship."""
    source = map_to_base_node(rel.source)
    target = map_to_base_node(rel.target)
    properties = props_to_dict(rel.properties) if rel.properties else {}
    return BaseRelationship(
        source=source, target=target, type=rel.type, properties=properties
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
    ## 6. Format Instructions
    - **Format**: The output should be in JSON format.(No need to use ```json``` in the output)
    """
    parser = JsonOutputParser(pydantic_object=KnowledgeGraph)
    prompt = PromptTemplate(
        template=RULE + "Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | llm | parser
    return chain

def extract_and_store_graph(
    document: Document,
    nodes:Optional[List[str]] = None,
    rels:Optional[List[str]]=None) -> None:
    extract_chain = get_extraction_chain(nodes, rels)
    print("invoke extract_chain")
    data = extract_chain.invoke({"query": document.page_content})
    # # Construct a graph document
    graph_document = GraphDocument(
      nodes = [map_to_base_node(node) for node in data.nodes],
      relationships = [map_to_base_relationship(rel) for rel in data.rels],
      source = document
    )
    # graph.add_graph_documents([graph_document])
    return graph_document

# Read the wikipedia article
raw_documents = ArxivLoader(query="2403.03410", load_max_docs=2).load()
# Define chunking strategy
text_splitter = TokenTextSplitter(chunk_size=2048, chunk_overlap=24)
# Only take the first the raw_documents
documents:list[Document] = text_splitter.split_documents(raw_documents[:3])
# print(documents[0].page_content)
for i, d in enumerate(documents):
    print(f"Processing document {i+1}/{len(documents)}")
    extract_and_store_graph(d)