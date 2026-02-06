from langchain_core.runnables import Runnable, RunnablePassthrough, RunnableWithMessageHistory
from langchain_core.documents import Document
from vector_store import VectorStoreService
from langchain_community.embeddings import  DashScopeEmbeddings
from langchain_core.prompts import ChatPromptTemplate, format_document, MessagesPlaceholder
import config_data as config
from langchain_community.chat_models import ChatTongyi
from file_history_store import get_history
from langchain_core.runnables import RunnableLambda
class RagService(object):
    def __init__(self):
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name)
        )

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "以我提供的参考资料为主,简洁和专业的回答用户的问题,参考资料如下:{context}"),
                ("system","并且用户的历史记录如下"),
                MessagesPlaceholder(variable_name="history"),
                ("user","请回答用户提问 {input}")
            ]
        )

        self.chat_model = ChatTongyi(model=config.chat_model_name)

        self.chain = self.__get_chain()
    def __get_chain(self):
        """
        获取执行链
        :return:
        """
        def format_document(docs:list[Document]):
            if not docs:
                return "无参考资料"
            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段:{doc.page_content} \n 文档元数据:{doc.metadata} \n\n"
            return formatted_str
        def temp1(value:dict):
            return value["input"]

        def temp2(value):
            new_value = {}
            new_value["input"] = value["input"]["input"]
            new_value["history"] = value["input"]["history"]
            new_value["context"] = value["context"]
            return  new_value

        retriever = self.vector_service.get_retriever()
        chain = (
            {
                "input": RunnablePassthrough(),
                "context": RunnableLambda(temp1) |retriever | format_document
            }|RunnableLambda(temp2)| self.prompt_template|(lambda x: (print('=' * 20 + '\n' + x.to_string() + '\n' + '=' * 20) or x)) |self.chat_model |(lambda x: x.content)
        )

        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )
        return conversation_chain

if __name__ == '__main__':
    #session_id配置
    session_config = {
        "configurable":{
            "session_id":"user_001",
        }
    }
    rag_service = RagService()
    res = rag_service.chain.invoke({"input":"请计算1+1"},session_config)
    print(res)
