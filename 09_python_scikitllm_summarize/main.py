import os
from skllm.config import SKLLMConfig
from skllm.models.gpt.text2text.summarization import GPTSummarizer
from dotenv import load_dotenv


load_dotenv()

SKLLMConfig.set_openai_key(os.environ.get("OPENAI_API_KEY"))
SKLLMConfig.set_openai_org(os.environ.get("OPENAI_API_ORGANIZATION"))


text_length = 500
text_to_summarize = """

"""
summarizer = GPTSummarizer(model="gpt-3.5-turbo", max_words=text_length)
X_summarized = summarizer.fit_transform([text_to_summarize])
print(X_summarized[0])
