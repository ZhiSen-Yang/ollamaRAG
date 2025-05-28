import os
import threading
import time
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader, CSVLoader, \
    UnstructuredHTMLLoader, UnstructuredEmailLoader, UnstructuredPowerPointLoader, UnstructuredExcelLoader, \
    UnstructuredEPubLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from init import db, config

def get_loader(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return PyPDFLoader(file_path)
    elif ext in [".doc", ".docx"]:
        return UnstructuredWordDocumentLoader(file_path)
    elif ext == ".txt":
        return TextLoader(file_path, encoding='utf-8')
    elif ext == ".csv":
        return CSVLoader(file_path)
    elif ext in [".html", ".htm"]:
        return UnstructuredHTMLLoader(file_path)
    elif ext in [".eml", ".msg"]:
        return UnstructuredEmailLoader(file_path)
    elif ext == ".pptx":
        return UnstructuredPowerPointLoader(file_path)
    elif ext in [".xlsx", ".xls"]:
        return UnstructuredExcelLoader(file_path)
    elif ext == ".epub":
        return UnstructuredEPubLoader(file_path)
    else:
        return None


def update_vector_db():
    folder_path= config["app"]["file"]["path"]
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    while True:
        for file in os.listdir(folder_path):
            full_path = os.path.join(folder_path, file)
            loader =  get_loader(full_path)
            if loader is None:
                print(f"⚠️ 跳过不支持的文件类型: {file}")
                continue
            try:
                print(f"📄 处理文件: {file}")
                docs = loader.load()
                split_docs = splitter.split_documents(docs)
                db.add_documents(split_docs)
                print(f"✅ 已更新向量数据库，文档: {file}")
                os.remove(full_path)
                print(f"🗑️ 已删除本地文档: {file}")
            except Exception as e:
                print(f"❌ 处理文件出错: {file}，错误: {e}")
                os.remove(full_path)
        time.sleep(10)


def start_file_watcher():
    print(f"📄守护线程开始启动，准备开始实时加载文件到向量数据库")
    t = threading.Thread(target=update_vector_db)
    t.daemon = True
    t.start()
    print(f"📄 守护线程完成启动，开始实时加载文件到向量数据库")