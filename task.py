import os
import threading
import time

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from init import db


def update_vector_db():
    folder_path="C:\projects\pdf_dir"
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    while True:
        for file in os.listdir(folder_path):
            print(f"📄 检测到新的文件，开始进行识别并更新向量数据库，文档名称: {file}")
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(folder_path, file)
                loader = PyPDFLoader(full_path)
                docs = loader.load()
                split_docs = splitter.split_documents(docs)
                db.add_documents(split_docs)
                print(f"📄 新文档导入向量数据库完成，文档名称: {file}")
                os.remove(full_path)
                print(f"📄 删除本地完成，文档名称: {file}")
        time.sleep(10)
def start_file_watcher():
    print(f"📄守护线程开始启动，准备开始实时加载文件到向量数据库")
    t = threading.Thread(target=update_vector_db)
    t.daemon = True
    t.start()
    print(f"📄 守护线程完成启动，开始实时加载文件到向量数据库")