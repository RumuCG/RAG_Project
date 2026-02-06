import os,json
from typing import Sequence
from langchain_core.messages import message_to_dict, messages_from_dict, BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory
# message_to_dict:单个消息对象(BaseMessage类实例) -> 字典
# messages_from_dict: [字典,字典 .. ] -> [消息,消息 .. ]
# AIMessage,HumanMessage,SystemMessage 都是 BaseMessage的子类
def get_history(session_id):
    return FileChatMessageHistory(session_id,storage_path="./chat_history")

class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self,session_id,storage_path):
        self.session_id = session_id # 会话id
        self.storage_path = storage_path #不同会话id的存储文件所在文件夹路径
        #合成
        self.file_path = os.path.join(self.storage_path,self.session_id)
        #确保文件夹存在
        os.makedirs(os.path.dirname(self.file_path),exist_ok=True)
    def add_messages(self, messages: Sequence[BaseMessage]):# Sequence序列 类似 list tuple
        all_messages = list(self.messages)
        all_messages.extend(messages)
        # 同步写入文件
        # 类对象写入文件实际上是二进制数据
        # 为了方便,可以将BaseMessage消息转为字典(借助json 以字符串写入
        new_messages = [message_to_dict(message) for message in all_messages]
        with open(self.file_path,"w",encoding="utf-8") as f:
            json.dump(new_messages,f,ensure_ascii=False)
    @ property
    def messages(self) -> Sequence[BaseMessage]:
        try:
            with open(self.file_path,"r",encoding="utf-8") as f:
                messages_dict = json.load(f) # 返回list[字典,字典 .. ]
                return messages_from_dict(messages_dict)
        except FileNotFoundError:
            return []
    def clear(self):
        with open(self.file_path,"w",encoding="utf-8") as f:
            json.dump([],f)
