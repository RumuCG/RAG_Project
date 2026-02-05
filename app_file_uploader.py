"""
基于 streamlit 完成网页上传服务
"""
import time

import streamlit as st
from knowledge_base import KnowledgeBaseService
st.title('知识库更新服务')
#st.session_state() 字典.. streamlit每次都刷新
if "service" not in st.session_state:
    st.session_state.service = KnowledgeBaseService()

uploaded_file = st.file_uploader(
    "选择文件",
    type=['txt'],
    accept_multiple_files= False, #表示只能上传一个文件
)
if uploaded_file:
    st.subheader(f"文件名: {uploaded_file.name}")
    st.write(f"格式 {uploaded_file.type} | 大小: {uploaded_file.size / 1024:.2f} KB")
    text = uploaded_file.read().decode('utf-8')
    st.write(text)
    with st.spinner("载入知识库中..."):
        time.sleep(1)
        res = st.session_state["service"].upload_by_str(text, uploaded_file.name)
        st.write(res)