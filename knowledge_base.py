"""
知识库
"""
import os
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from polars.polars import spearman_rank_corr
from datetime import datetime

from sqlalchemy.testing.suite.test_reflection import metadata

import config_data as config
import hashlib
from langchain_chroma import Chroma
def check_md5(md5_str:str):
    """
    检查传入的md5的字符串是否已经被处理过了
    """
    if not os.path.exists(config.md5_path):
        open(config.md5_path,'w',encoding='utf-8').close()
        return  False
    else:
        with open(config.md5_path,'r',encoding='utf-8') as f:
            md5_list = f.readlines()
            for md5 in md5_list:
                if md5_str == md5.strip():
                    return True
            return False

def save_md5(md5_str:str):
    """
    将传入的md5字符串记录到文件内保存
    """
    with open(config.md5_path,'a',encoding='utf-8') as f:
        f.write(md5_str+'\n')

def get_string_md5(md5_str:str,encode='utf-8'):
    """
    传入字符串，返回md5字符串
    """
    #先将字符串转化为字节流
    str_bytes = md5_str.encode(encoding=encode)
    md5_obj = hashlib.md5() # md5 对象
    md5_obj.update(str_bytes)
    md5_hex = md5_obj.hexdigest() #转化为16进制字符串
    return md5_hex

class KnowledgeBaseService(object):
    def __init__(self):
        os.makedirs(config.persist_directory,exist_ok = True) # 存在则跳过
        self.chroma = Chroma(
            collection_name= config.collection_name,
            persist_directory= config.persist_directory, # 数据本地存储位置
            embedding_function=DashScopeEmbeddings(model='text-embedding-v4'),
        ) # 向量存储的实例Chroma向量库对象
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size, # 分割文本后的字符重叠数量
            chunk_overlap=config.chunk_overlap, # 连续文本段之间的字符重叠数量
            separators=config.separators, # 自然段落划分的符号
            length_function=len,# 使用len()作为长度依据
        ) # 文本分割器的对象
    def upload_by_str(self,data,filename):
        """
        将传入的字符串转化为md5字符串
        """
        md5_hex = get_string_md5(data)
        if check_md5(md5_hex):
            return f"{filename} 已经处理过了"
        if len(data) > config.min_spliter_length:
            knowledge_chunks:list[str] = self.spliter.split_text(data)
        else:
            knowledge_chunks = [data]
        metadata = {
            "source": filename,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator":"admin",
        }
        self.chroma.add_texts(
            texts=knowledge_chunks,
            metadatas=[metadata]*len(knowledge_chunks)
        )
        save_md5(md5_hex)
        return f"{filename} 处理完成,存入向量库"

if __name__ == '__main__':
    service = KnowledgeBaseService()
    print(service.upload_by_str("12345","testfile"))

