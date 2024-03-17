from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from elasticsearch import Elasticsearch
from pydantic import BaseModel


# Keyword 모델 정의
class Keyword(BaseModel):
    keyword: str
    keyword_type: str


app = FastAPI()

# Elasticsearch 클라이언트 생성
client = Elasticsearch("http://es:9200")

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory=".")


# 루트 경로에 HTML 랜더링
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 검색어 등록
@app.post("/keywords/", response_model=dict)
def create_keyword_handler(keyword_data: Keyword):
    """검색어 등록"""
    data = {"keyword": keyword_data.keyword, "keyword_type": keyword_data.keyword_type}
    client.index(index="search1", body=data)
    return {"message": "OK"}


# 검색어 조회
@app.get("/keywords/", response_model=list)
def get_keywords_handler(q: str):
    """키워드 추천"""
    query = {"query": {"wildcard": {"keyword": f"*{q}*"}}}
    results = client.search(index="search1", body=query)
    return results["hits"]["hits"]
