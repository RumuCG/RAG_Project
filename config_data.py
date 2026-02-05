md5_path = "./md5.text"
# Chroma
collection_name ="rag" # 向量库名称
persist_directory = "./chroma_db"

# spliter
chunk_size = 1000
chunk_overlap = 100
separators = ["。", "？", "！", "；", "，", "、", "。", "？", "！", "；", "，", "、" ,"\n", "\n\n"]
min_spliter_length = 100 #分割阈值