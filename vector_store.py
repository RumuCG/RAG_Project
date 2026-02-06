from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
import  config_data as config
class VectorStoreService(object):
    def __init__(self,embedding):
        """
        :param embedding: 嵌入模型的传入
        """
        self.embedding = embedding
        self.vector_store = Chroma(
            collection_name=config.collection_name,
            embedding_function=self.embedding,
            persist_directory=config.persist_directory,
        )
    def get_retriever(self):
        """
        :return: 返回向量检索器
        """
        return self.vector_store.as_retriever(search_kwargs={"k":config.similarity_threshold}) # 返回几个匹配的结果
if __name__ == '__main__':
    retriever = VectorStoreService(DashScopeEmbeddings(model='text-embedding-v4')).get_retriever()
    res = retriever.invoke("11")
    print(res)