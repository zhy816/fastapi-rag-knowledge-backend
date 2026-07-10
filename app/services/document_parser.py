from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


class DocumentParseError(Exception):
    """
    文档解析失败时抛出的自定义异常。
    """
    pass

# 因为 .txt 文件不像 .docx / .pdf 那样有比较固定的格式，它可能是不同编码保存的。
# 尤其中文环境里，常见有：
# utf-8       比较通用
# utf-8-sig   带 BOM 头的 utf-8
# gbk         Windows 中文系统里很常见
def parse_txt(file_path: str) -> str:
    """
    解析 txt 文件，返回纯文本内容。
    """
    path = Path(file_path) # 这样后面可以更方便地读文件：path.read_text(...)

    encodings = ["utf-8", "utf-8-sig", "gbk"]
    # 我不知道这个 txt 到底是什么编码
    # 那我就按顺序试：
    # 先试 utf-8
    # 不行再试 utf-8-sig
    # 还不行再试 gbk

    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding) # 如果成功，直接 return 文本内容，函数结束
        except UnicodeDecodeError:
            continue

    return path.read_text(encoding="utf-8", errors="ignore")
    # 这个是兜底
    # 最后再用utf - 8 强行读一次。
    # 遇到实在识别不了的字符，就忽略掉。


# 它负责读取 Word 文档里的段落。
def parse_docx(file_path: str) -> str:
    """
    解析 docx 文件，提取每个段落的文字。
    """
    doc = DocxDocument(file_path)

    paragraphs = []
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)

# 它负责读取 PDF 每一页的文字。
# 不过注意，PDF 有两种情况：
# 文字型 PDF：可以正常提取文字
# 扫描版 PDF：本质是图片，pypdf 可能提取不到文字
# 扫描版 PDF 要 OCR，那是后面的扩展功能。我们这个阶段先不做 OCR。
def parse_pdf(file_path: str) -> str:
    """
    解析 pdf 文件，提取每一页的文字。
    """
    reader = PdfReader(file_path)

    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text.strip())

    return "\n".join(pages_text)


def parse_document_file(file_path: str, file_type: str) -> str:
    """
    根据文件类型，选择对应的解析方法。
    """
    path = Path(file_path)

    if not path.exists():
        raise DocumentParseError(f"File not found: {file_path}")

    file_type = file_type.lower().lstrip(".")

    if file_type == "txt":
        return parse_txt(file_path)

    if file_type == "docx":
        return parse_docx(file_path)

    if file_type == "pdf":
        return parse_pdf(file_path)

    raise DocumentParseError(f"Unsupported file type: {file_type}")