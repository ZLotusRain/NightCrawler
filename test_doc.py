import docx
from docx import Document
path = "C:/Users/zhuhuayu/Downloads/7024095.docx"
test_1_path = "C:/Users/zhuhuayu/Downloads/test1.docx"
with open(path, "rb") as fo:
    open(test_1_path, "wb").write(fo.read())

doc = Document(test_1_path)