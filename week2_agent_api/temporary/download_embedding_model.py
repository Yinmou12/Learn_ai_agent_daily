import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction,
)

load_dotenv()

model_name = os.environ["EMBEDDING_MODEL"]
cache_folder = Path(os.environ["EMBEDDING_CACHE_FOLDER"])

cache_folder.mkdir(parents=True, exist_ok=True)

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name=model_name,
    device="cpu",
    normalize_embeddings=True,
    cache_folder=str(cache_folder),
)

# 调用一次，确认下载、加载和推理均正常
embedding = embedding_function(["这是一段用于验证多语言嵌入模型的中文文本。"])[0]

print(f"模型：{model_name}")
print(f"缓存根目录：{cache_folder.resolve()}")
print(f"向量维度：{len(embedding)}")
print(f"向量范数：{np.linalg.norm(embedding):.6f}")
print("模型下载与验证完成。")
