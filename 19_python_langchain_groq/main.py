from dotenv import load_dotenv


load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


# chat = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")
# system = "You are a helpful assistant."
# human = "{text}"
# prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
#
# chain = prompt | chat
# chain.invoke({"text": "Explain the importance of low latency LLMs."})

chat = ChatGroq(temperature=0, model_name="gemma-7b-it")
prompt = ChatPromptTemplate.from_messages([("human", "Write a haiku about {topic}")])
chain = prompt | chat
for chunk in chain.stream({"topic": "The Moon"}):
    print(chunk.content, end="", flush=True)
