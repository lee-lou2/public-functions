import pandas as pd
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv


load_dotenv()


df = pd.read_csv("req.csv")

cnt = 0
docs = []
for pk, question in zip(df["req_seq"], df["question"]):
    cnt += 1
    if cnt > 1000:
        break
    docs.append(question)

# doc_list_1 = [
#     "I like apples",
#     "I like oranges",
#     "Apples and oranges are fruits",
# ]

bm25_retriever = BM25Retriever.from_texts(docs, metadatas=[{"source": 1}] * len(docs))
bm25_retriever.k = 2

# doc_list_2 = [
#     "You like apples",
#     "You like oranges",
# ]

embedding = OpenAIEmbeddings(model="text-embedding-3-small")
faiss_vectorstore = FAISS.from_texts(
    docs, embedding, metadatas=[{"source": 2}] * len(docs)
)
faiss_retriever = faiss_vectorstore.as_retriever(search_kwargs={"k": 2})

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, faiss_retriever], weights=[0.5, 0.5]
)

answer = ensemble_retriever.invoke("감성 돋는 도서 추천")
print(answer)
