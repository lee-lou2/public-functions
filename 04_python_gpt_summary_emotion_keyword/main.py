import os
import requests
import streamlit as st
import google.generativeai as genai
from openai import OpenAI
from skllm.config import SKLLMConfig
from skllm.models.gpt.classification.zero_shot import ZeroShotGPTClassifier
from skllm.models.gpt.text2text.summarization import GPTSummarizer
from dotenv import load_dotenv


load_dotenv()


SKLLMConfig.set_openai_key(os.environ.get("OPENAI_API_KEY"))
SKLLMConfig.set_openai_org(os.environ.get("OPENAI_API_ORGANIZATION"))

st.title("텍스트 분석 도구")

# 탭 설정
tab1, tab2, tab3 = st.tabs(["요약", "감정 추출", "키워드 추출"])


def get_deepl_result(text):
    url = "https://api-free.deepl.com/v2/translate"
    service_key = "9bf1be73-ed7a-b2ba-10b2-764d88449380:fx"
    headers = {
        "Authorization": f"DeepL-Auth-Key {service_key}",
        "Content-Type": "application/json",
    }
    data = {
        "text": [text],
        "target_lang": "ko",
    }
    resp = requests.post(url=url, headers=headers, json=data)
    if resp.status_code != 200:
        return None
    return resp.json()["translations"][0]["text"]


# 요약 탭
with tab1:
    st.subheader("요약")
    text_to_summarize = st.text_area("내용 입력")
    text_length = st.text_input("옵션 선택", key="text_length_option", value="15")
    if st.button("분석하기"):
        summarizer = GPTSummarizer(model="gpt-3.5-turbo", max_words=int(text_length))
        X_summarized = summarizer.fit_transform([text_to_summarize])
        results = get_deepl_result(X_summarized[0])
        st.write(results)

# 감정 추출 탭
with tab2:
    st.subheader("감정 추출")
    text_to_analyze = st.text_area("내용 입력", key="emotion_text")
    option = st.text_input(
        "옵션 선택",
        key="emotion_option",
        value="기쁨, 놀람, 무서움, 감동, 화남, 유쾌, 행복, 즐거움",
    )
    if st.button("분석하기", key="emotion_button"):
        clf = ZeroShotGPTClassifier(model="gpt-3.5-turbo")
        clf.fit(None, option.split(","))
        labels = clf.predict([text_to_analyze])
        st.write(labels)

# 키워드 추출 탭
with tab3:
    st.subheader("키워드 추출")
    option = st.selectbox("옵션 선택", ["Google Gemini", "OpenAI GPT3.5"])
    text_to_extract = st.text_area("내용 입력", key="keyword_text")
    if st.button("요약하기", key="keyword_button"):
        system_message = (
            "위 내용에서 핵심되는 키워드를 5~10개 추출해줘."
            "하나의 키워드는 10자 미만, 단어 형태로 추출해줘."
            "답변의 형태는 '키워드1, 키워드2, 키워드3' 으로 대답해줘."
        )
        if option == "Google Gemini":
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content([system_message, text_to_extract])
            keywords = response.text
        else:
            client = OpenAI()
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": str(text_to_extract)},
                ],
            )
            keywords = completion.choices[0].message.content
        st.write(keywords)
