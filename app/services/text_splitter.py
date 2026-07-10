import re


def clean_text(text: str) -> str:
    """
    清洗解析出来的原始文本。
    """
    # 统一 Windows / Mac / Linux 不同换行符
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 去掉每一行首尾多余空格
    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if line:
            lines.append(line)

    # 用单个换行重新拼接有效文本行
    text = "\n".join(lines)

    # 把连续 3 个以上换行压缩成 2 个换行
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_text(text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> list[str]:
    #传进来一整段 text 默认每 800 个字符切一段
# 相邻两段之间重叠 100 个字符 最后返回 list[str]，也就是很多个字符串 chunk
    """
    把长文本切分成多个 chunks。

    chunk_size：每个 chunk 最大字符数
    chunk_overlap：相邻 chunk 之间重叠的字符数
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0") #因为“每段 0 个字符”没意义。

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be greater than or equal to 0")
    #         # 为了让后面的第二个chunk有上文， 所以 我们才设置了overlap这个属性
    #         # 第二个 chunk 单独看就有点断，少了前面的语境。
    #         # 但如果有 overlap，可能变成：
    #         # chunk 1：Merkle Tree 是一种哈希树，可以用来高效证明
    #         # chunk 2：可以用来高效证明某个交易是否存在于区块中。
    #         # 这样第二个 chunk 也能保留一点上下文。

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    text = clean_text(text)

    if not text:
        return []
    # 如果清洗完文本是空的，那就直接返回空列表

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # 为了截取chunk
        chunk = text[start:end].strip()


        if chunk:
            chunks.append(chunk)

        start = end - chunk_overlap
    #     更新下一个start的位置， 因为我们要保留overlap部分， 所以我们在设置下个start开始的位置的时候 要剪掉 overlap

    return chunks