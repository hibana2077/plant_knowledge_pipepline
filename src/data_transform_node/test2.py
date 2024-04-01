from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs.neo4j_graph import Neo4jGraph
from langchain.prompts.prompt import PromptTemplate
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY","") # allow multiple keys -> key1,key2,key3 -> split(",") -> ["key1", "key2", "key3"]
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","") # allow multiple keys -> key1,key2,key3 -> split(",") -> ["key1", "key2", "key3"]
GROQ_API_KEY_LIST = GROQ_API_KEY.split(",") if GROQ_API_KEY else []
OPENAI_API_KEY_LIST = OPENAI_API_KEY.split(",") if OPENAI_API_KEY else []
NEO4J_URL = os.getenv("NEO4J_URL", "bolt://localhost:7687") #note: use bolt protocol
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "plant_knowledge")

graph = Neo4jGraph(
    url=NEO4J_URL,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
)

graph.refresh_schema()

llm = ChatGroq(temperature=0, api_key=GROQ_API_KEY_LIST[0],model_name="mixtral-8x7b-32768")
llm2 = ChatGroq(temperature=0, api_key=GROQ_API_KEY_LIST[0],model_name="llama2-70b-4096")
llm3 = ChatGroq(temperature=0, api_key=GROQ_API_KEY_LIST[0],model_name="gemma-7b-it")

CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Do not use properties that are not needed for the query.
You can try to use id insted of name in the query if needed.

Example 1:
What's Breeding_Efforts?
Query:
MATCH (n)
WHERE n.name = 'Breeding_Efforts' OR n.id = 'Breeding_Efforts'
RETURN n

Example 2:
What's the connection between Plantbreeding and Plantvariety?
Query:
MATCH (n)-[r]->(m)
WHERE n.name = 'Plantbreeding' OR n.id = 'Plantbreeding' AND m.id = 'Plantvariety'
RETURN n, r, m

The question is:
{question}"""

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
)

cypher_chain = GraphCypherQAChain.from_llm(
    graph=graph,
    cypher_llm=ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY_LIST[0], model="gpt-4-0125-preview"),
    qa_llm=llm,
    validate_cypher=True, # Validate relationship directions
    verbose=True,
    return_intermediate_steps=True,
    cypher_prompt=CYPHER_GENERATION_PROMPT,
)

result = cypher_chain.invoke({"query": "What's the connection between Plantbreeding and Plantvariety?"})
print(f"Intermediate steps: {result['intermediate_steps']}")
print(f"Final answer: {result['result']}")