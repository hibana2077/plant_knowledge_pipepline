'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-03-08 12:27:47
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-03-12 16:15:13
FilePath: \plant_knowledge_pipepline\src\data_transform_node\lab.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from typing import List, Dict, Any, Optional
from langchain_community.graphs.graph_document import (
    Node as BaseNode,
    Relationship as BaseRelationship,
    GraphDocument,
)
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from pprint import pprint
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from time import time

#mistralai/Mistral-7B-Instruct-v0.2

hf_model = HuggingFacePipeline.from_model_id(
    model_id="mistralai/Mistral-7B-Instruct-v0.2",
    task="text-generation",
    device=0,  # replace with device_map="auto" to use the accelerate library.
    pipeline_kwargs={"max_new_tokens": 2000}
)

# Define your desired data structure.
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

# And a query intented to prompt a language model to populate the data structure.
query = "Harry was a chubby brown beagle who loved chicken."

# Set up a parser + inject instructions into the prompt template.
parser = JsonOutputParser(pydantic_object=KnowledgeGraph)

prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain3 = prompt | hf_model | parser

print(f"{hf_model.model_id} output:")
s = time()
pprint(chain3.invoke({"query": query}))
print(f"Time taken: {time() - s} seconds.")