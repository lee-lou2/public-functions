import ebooklib
from ebooklib import epub
import pypandoc


book = epub.read_epub("worker.epub")

content = []
for item in book.get_items():
    if item.get_type() == ebooklib.ITEM_DOCUMENT:
        content.append(item.get_content())

html_content = b"".join(content).decode("utf-8")

# 출력 파일 이름 지정
output_file = "output1.docx"
pypandoc.convert_text(html_content, "docx", format="html", outputfile=output_file)
