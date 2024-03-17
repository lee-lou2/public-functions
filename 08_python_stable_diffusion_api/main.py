import base64
import io
import os

import requests
import streamlit as st
from PIL import Image


# API 설정 및 호출 함수
def call_api(api_key, url, body, headers, files=None):
    headers["Authorization"] = f"Bearer {api_key}"
    if files:
        response = requests.post(url, headers=headers, files=files, data=body)
    else:
        response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))
    return response.json()


# 이미지 저장 및 표시 함수
def save_and_display_image(data, prefix):
    if not os.path.exists("./out"):
        os.makedirs("./out")
    for i, image in enumerate(data["artifacts"]):
        filepath = f'./out/{prefix}_{image["seed"]}.png'
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(image["base64"]))
        st.image(filepath, caption=f"Image {i + 1}")


# 스트림릿 UI 구성
st.title("Stability AI API Caller")
api_key = st.text_input("API Key", type="password")
engine_id = st.selectbox(
    "Engine ID",
    ["stable-diffusion-xl-1024-v1-0", "stable-diffusion-v1-6"],
    index=0,
    format_func=lambda x: x.replace("-", " ").title(),
)

# 공통 변수
st.header("Settings")
steps = st.number_input("Steps", min_value=1, value=30)
width = st.number_input("Width", min_value=1, value=1024)
height = st.number_input("Height", min_value=1, value=1024)
seed = st.number_input("Seed", min_value=0, value=0)
cfg_scale = st.number_input("CFG Scale", min_value=0.0, value=5.0)

if "prompts" not in st.session_state:
    st.session_state.prompts = [{"text": "", "weight": 1}]


def add_prompt():
    st.session_state.prompts.append({"text": "", "weight": 1})


def remove_prompt(index):
    del st.session_state.prompts[index]


for i in range(len(st.session_state.prompts)):
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        st.session_state.prompts[i]["text"] = st.text_input(
            f"프롬프트 {i + 1}", key=f"text_{i}"
        )
    with col2:
        st.session_state.prompts[i]["weight"] = st.number_input(
            "가중치",
            min_value=-1.0,
            max_value=2.0,
            value=1.0,
            step=0.01,
            key=f"weight_{i}",
        )
    with col3:
        if len(st.session_state.prompts) > 1:  # 적어도 하나의 프롬프트는 유지
            remove_button = st.button("제거", key=f"remove_{i}")
            if remove_button:
                remove_prompt(i)
                # 페이지를 다시 로드하여 UI를 업데이트함
                st.experimental_rerun()
    if (
        i == len(st.session_state.prompts) - 1
    ):  # 마지막 프롬프트 옆에만 추가 버튼을 표시
        with col4:
            st.button("추가", on_click=add_prompt)

# T2I와 I2I 섹션
col1, col2 = st.columns(2)

with col1:
    text_prompts = [
        {"text": prompt["text"], "weight": prompt["weight"]}
        for prompt in st.session_state.prompts
        if prompt["text"]
    ]
    st.header("Text-to-Image")
    if st.button("Generate Text-to-Image"):
        body = {
            "steps": steps,
            "width": width,
            "height": height,
            "seed": seed,
            "cfg_scale": cfg_scale,
            "samples": 1,
            "text_prompts": text_prompts,
        }
        url = f"https://api.stability.ai/v1/generation/{engine_id}/text-to-image"
        headers = {"Accept": "application/json", "Authorization": f"Bearer {api_key}"}
        try:
            data = call_api(api_key, url, body, headers)
            save_and_display_image(data, "txt2img")
        except Exception as e:
            st.error(e)

with col2:
    st.header("Image-to-Image")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    image_strength = st.slider(
        "Image Strength", min_value=0.0, max_value=1.0, value=0.35
    )

    if st.button("Generate Image-to-Image"):
        if uploaded_file is not None:
            # 이미지를 읽어서 PIL 이미지 객체로 변환
            input_image = Image.open(uploaded_file)

            # 지정된 크기로 이미지 크기 조정
            # 이 부분에서는 API 요구 사항에 맞는 크기를 선택해야 합니다. 예를 들어 1024x1024
            resized_image = input_image.resize((width, height))

            # PIL 이미지를 바이트로 변환하여 API 요청을 위한 파일로 준비
            img_byte_arr = io.BytesIO()
            resized_image.save(
                img_byte_arr, format=uploaded_file.type.split("/")[-1].upper()
            )
            img_byte_arr = img_byte_arr.getvalue()

            files = {"init_image": img_byte_arr}

            # text_prompts를 API 요청 형태에 맞게 변환
            data = {
                "init_image_mode": "IMAGE_STRENGTH",
                "image_strength": image_strength,
                "steps": steps,
                "seed": seed,
                "cfg_scale": cfg_scale,
                "samples": 1,
            }

            # 프롬프트 정보 추가
            for i, prompt in enumerate(st.session_state.prompts):
                data[f"text_prompts[{i}][text]"] = prompt["text"]
                data[f"text_prompts[{i}][weight]"] = prompt["weight"]

            url = f"https://api.stability.ai/v1/generation/{engine_id}/image-to-image"
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
            try:
                response = requests.post(url, headers=headers, files=files, data=data)
                if response.status_code != 200:
                    raise Exception("Non-200 response: " + str(response.text))
                data = response.json()
                save_and_display_image(data, "img2img")
            except Exception as e:
                st.error(e)
        else:
            st.error("Please upload an image.")
