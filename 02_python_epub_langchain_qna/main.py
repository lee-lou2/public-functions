import ebooklib
import streamlit as st
import tiktoken
from docx import Document
from ebooklib import epub
from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import Docx2txtLoader
from langchain.memory import ConversationBufferMemory
from langchain.memory import StreamlitChatMessageHistory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv


load_dotenv()


def main():
    st.set_page_config(page_title="도서 Q&A", page_icon=":books:")

    st.title("도서 :red[Q&A]_ :books:")

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    if "processComplete" not in st.session_state:
        st.session_state.processComplete = None

    with st.sidebar:
        uploaded_files = st.file_uploader(
            "Upload your file", type=["epub"], accept_multiple_files=True
        )
        process = st.button("업로드")
    if process:
        files = []
        for file in uploaded_files:
            docx_file_name = os.path.splitext(file.name)[0] + ".docx"
            epub_to_docx(file, docx_file_name)
            files.append(docx_file_name)
        files_text = get_text(files)
        text_chunks = get_text_chunks(files_text)
        vetorestore = get_vectorstore(text_chunks)

        st.session_state.conversation = get_conversation_chain(vetorestore)

        st.session_state.processComplete = True

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "안녕하세요! 주어진 도서에 대해 궁금하신 것이 있으면 언제든 물어봐주세요!",
            }
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    history = StreamlitChatMessageHistory(key="chat_messages")

    # Chat logic
    if query := st.chat_input("질문을 입력해주세요."):
        st.session_state.messages.append({"role": "user", "content": query})

        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            chain = st.session_state.conversation

            with st.spinner("Thinking..."):
                result = chain({"question": query})
                with get_openai_callback() as cb:
                    st.session_state.chat_history = result["chat_history"]
                response = result["answer"]
                source_documents = result["source_documents"]

                st.markdown(response)
                with st.expander("참고 문서 확인"):
                    st.markdown(
                        source_documents[0].metadata["source"],
                        help=source_documents[0].page_content,
                    )
                    st.markdown(
                        source_documents[1].metadata["source"],
                        help=source_documents[1].page_content,
                    )
                    st.markdown(
                        source_documents[2].metadata["source"],
                        help=source_documents[2].page_content,
                    )

        # Add assistant message to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})


def tiktoken_len(text):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    return len(tokens)


def epub_to_docx(epub_file, docx_file_path):
    # EPUB 파일 읽기
    file_name = epub_file.name
    with open(file_name, "wb") as file:
        file.write(epub_file.getvalue())
    book = epub.read_epub(file_name)

    # 새로운 Word 문서 생성
    doc = Document()

    # EPUB 파일의 각 항목을 순회하며 내용을 Word 문서에 추가
    for item in book.get_items():
        try:
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                doc.add_paragraph(item.get_content().decode("utf-8"))
        except KeyError as e:
            print(f"Error reading {item.get_name()}: {e}")

    # Word 문서 저장
    doc.save(docx_file_path)


def get_text(docs):
    doc_list = []

    for doc in docs:
        loader = Docx2txtLoader(doc)
        documents = loader.load_and_split()
        doc_list.extend(documents)
    return doc_list


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=900, chunk_overlap=100, length_function=tiktoken_len
    )
    chunks = text_splitter.split_documents(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vectordb = FAISS.from_documents(text_chunks, embeddings)
    return vectordb


def get_conversation_chain(vetorestore):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        chain_type="stuff",
        retriever=vetorestore.as_retriever(search_type="mmr", vervose=True),
        memory=ConversationBufferMemory(
            memory_key="chat_history", return_messages=True, output_key="answer"
        ),
        get_chat_history=lambda h: h,
        return_source_documents=True,
        verbose=True,
    )
    return conversation_chain


if __name__ == "__main__":
    main()
