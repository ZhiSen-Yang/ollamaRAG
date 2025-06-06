import yaml
from langchain_community.llms.ollama import Ollama
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings



def load_config(path: str):
    with open(path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
persist_dir = "./chroma_ollama"
db = Chroma(persist_directory=persist_dir, embedding_function=embedding_model)
llm = Ollama(model="deepseek-r1:8b")
config = load_config("application.yml")