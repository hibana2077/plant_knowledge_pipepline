from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
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
import time

ssl._create_default_https_context = ssl._create_unverified_context

GROQ_API_KEY = os.getenv("GROQ_API_KEY","") # allow multiple keys -> key1,key2,key3 -> split(",") -> ["key1", "key2", "key3"]
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","") # allow multiple keys -> key1,key2,key3 -> split(",") -> ["key1", "key2", "key3"]
GROQ_API_KEY_LIST = GROQ_API_KEY.split(",") if GROQ_API_KEY == "" else []
OPENAI_API_KEY_LIST = OPENAI_API_KEY.split(",") if OPENAI_API_KEY == "" else []
NEO4J_URL = os.getenv("NEO4J_URL", "bolt://localhost:7687") #note: use bolt protocol
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "plant_knowledge")

if not GROQ_API_KEY_LIST:raise ValueError("GROQ_API_KEY is required")
if not OPENAI_API_KEY_LIST:raise ValueError("OPENAI_API_KEY is required")
llm = ChatGroq(temperature=0, api_key=GROQ_API_KEY_LIST[0],model_name="mixtral-8x7b-32768")
openai_llm = ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY_LIST[0], model_name="gpt-4-0125-preview")

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
    print(f"Node{type(node)}: {node} \t\n")
    properties = props_to_dict(node['properties']) if type(node) == dict and 'properties' in node.keys() else props_to_dict(node.properties) if type(node) != str and type(node) != dict else {}
    # Add name property for better Cypher statement generation
    properties["name"] = node['id'].title() if type(node) == dict and node['id'] else node.id.title() if type(node) != str and type(node) != dict else node.title()
    try:
        if type(node) == dict:
            return BaseNode(
                id=node['id'].title(), type=node["type"].capitalize(), properties=properties
            )
        elif type(node) == str:
            return BaseNode(
                id=node.title(), type="Node", properties=properties
            )
        else:
            return BaseNode(
                id=node.id.title(), type=node.type.capitalize(), properties=properties
            )
    except AttributeError:
        return BaseNode(
            id=node, type="Node", properties=properties
        )
    except TypeError:
        return BaseNode(
            id=node, type="Node", properties=properties
        )

def map_to_base_relationship(rel: Relationship,base_nodes:List[BaseNode]) -> BaseRelationship:
    """Map the KnowledgeGraph Relationship to the base Relationship."""
    print("map to base rel:",rel, type(rel), "\t\n")
    # print(f"Rel.type: {rel['type']}")
    source_node = next((node for node in base_nodes if node.id == rel["source"]), rel["source"])
    target_node = next((node for node in base_nodes if node.id == rel["target"]), rel["target"])
    source = map_to_base_node(source_node)
    target = map_to_base_node(target_node)
    properties = props_to_dict(rel["properties"]) if "properties" in rel.keys() else {}
    if rel["type"] == None:rel["type"] = "Relationship"
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

## Overview

You are a top-tier algorithm designed to extract information in structured formats to build a knowledge graph, where:
- **Nodes** represent entities and concepts, similar to Wikipedia entries.
- The goal is to create a knowledge graph that is simple and clear, making it accessible to a wide audience.

## Labeling Nodes

- **Consistency**: Use basic or elementary types for node labels. For instance, label an entity representing a person as **"person"** rather than using more specific terms like "mathematician" or "scientist".
- **Node IDs**: Use names or human-readable identifiers for node IDs, avoiding integers.

## Handling Numerical Data and Dates

- Integrate numerical data, such as age, as attributes of the nodes.
- **No Separate Nodes for Dates/Numbers**: Attach dates or numerical values as attributes of nodes, not as separate nodes.
- **Property Format**: Present properties in a key-value format, using camelCase for property keys (e.g., `birthDate`).
- **Quotation Marks**: Do not use escaped quotes within property values.

## Coreference Resolution

- **Maintain Entity Consistency**: Ensure consistency in entity references. Use the most complete identifier for an entity mentioned multiple times in the text, even if referred to by different names or pronouns. For example, always use "John Doe" instead of variations like "Joe" or "he".

## Strict Compliance

Strict adherence to these rules is mandatory. Non-compliance will lead to termination.

## Forbidden Formats

- **No HTML**: Exclude HTML tags from nodes or relationships.
- **No Markdown**: Avoid markdown syntax in nodes or relationships.
- **No Skip**: Extract all relevant information without skipping any part of the text.
- **Invalid JSON Output**: Ensure JSON output is valid.

## Additional Guidelines

- **Start Formatting**: Begin with "{" and conclude with "}".
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
        # use openai llm to make data structure more clear
        new_prompt = PromptTemplate(
            template="Organize the input text into the correct json format. \n{data}\n",
            input_variables=["data"],
        )
        new_chain = new_prompt | openai_llm
        data:AIMessage = new_chain.invoke({"data": data})
        data:str = data.content
        data = parser.parse(data)
    print("\n\n")
    # Construct a graph document
    nodes = [map_to_base_node(node) for node in data['nodes']]
    relationships = [map_to_base_relationship(rel,nodes) for rel in data['rels']]
    graph_document = GraphDocument(
      nodes = nodes,
      relationships = relationships,
      source = document
    )
    graph.add_graph_documents([graph_document])
    return graph_document

# Read the wikipedia article
raw_documents = WebBaseLoader("https://iastate.pressbooks.pub/cropimprovement/chapter/basic-principles-of-plant-breeding/")
raw_documents.requests_kwargs = {"verify":False}
raw_documents = raw_documents.load()
# Define chunking strategy
text_splitter = TokenTextSplitter(chunk_size=2048, chunk_overlap=24)
# Only take the first the raw_documents
documents:list[Document] = text_splitter.split_documents(raw_documents[:10])
for i, d in enumerate(documents):
    s = time.time()
    print(f"Processing document {i+1}/{len(documents)}")
    extract_and_store_graph(d)
    print(f"Time taken: {time.time()-s:.2f} seconds")