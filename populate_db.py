import argparse
import os 
import shutil

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_func import get_embedding_function
from langchain_chroma import Chroma


CHROMA_PATH = "chroma"
DATA_PATH ="data"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset",action="store_true",help="Reset the DB")
    arg = parser.parse_args()
    if arg.reset:
        print("✨ Clearing Database")
        clear_DB()
    doc = load_Doc()
    chunk = split_doc(doc)
    add_to_DB(chunk)


def load_Doc():
    doc_loader = PyPDFDirectoryLoader(DATA_PATH)
    return doc_loader.load()

documents = load_Doc()

def split_doc(doc:list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False

    )
    return text_splitter.split_documents(doc)
text_chunk = split_doc(documents)
print("chunk",text_chunk[0])
def add_to_DB(chunks:list[Document]):
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function()
    )
    chunks_with_ids = calculate_chunk_ids(chunks)
    
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)
    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks,ids=new_chunk_ids)
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_idx = 0 
    for chunk in chunks:
        src = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{src}:{page}"

        if current_page_id ==last_page_id:
            current_chunk_idx+=1
        else:
            current_chunk_idx =0
        
        chunk_id=f"{current_page_id}:{current_chunk_idx}"
        last_page_id=current_page_id

        chunk.metadata["id"]=chunk_id
    return chunks

def clear_DB():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


if __name__=="__main__":
    main()

    # Debug: Inspect a loaded and chunked document
    # documents = load_Doc()
    # chunks = split_doc(documents)
    # print("🧪 First Chunk Preview:")
    # print("Content:", chunks[0].page_content[:300])
    # print("Metadata:", chunks[0].metadata)








