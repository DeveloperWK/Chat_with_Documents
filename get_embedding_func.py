from langchain_ollama import OllamaEmbeddings

def get_embedding_function():
    embedding = OllamaEmbeddings(model="mxbai-embed-large")
    return embedding