import os 
import shutil
from typing import List,Any


from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_chroma import Chroma
from rich.progress import Progress,SpinnerColumn,TextColumn,BarColumn,TimeRemainingColumn,TimeElapsedColumn

import cli_utils
import document_loader



DATA_PATH="data"


def main(config:dict,embedding_func:Any,reset_db:bool=False):
    vector_store_path=config["vector_store_path"]
    if reset_db:
        cli_utils.print_info("✨ Clearing Database...")
        clear_DB(vector_store_path)
        cli_utils.print_success("Database cleared.")
    cli_utils.print_info(f"Loading documents from '{DATA_PATH}'...")

    documents=document_loader.load_documents_from_directory(DATA_PATH)
    if not documents:
        cli_utils.print_warning("No documents loaded. Exiting database population.")
        return
    cli_utils.print_info("Splitting documents into chunks...")
    chunks=split_documents(documents)

    if not chunks:
        cli_utils.print_warning("No chunks generated from documents. Exiting database population.")
        return
    if chunks:
        cli_utils.print_info("✅ First chunk preview:")
        cli_utils.console.print(f"  Content: {chunks[0].page_content[:200]}...")
        cli_utils.console.print(f"  Metadata: {chunks[0].metadata}")
    
    cli_utils.print_info("Adding documents to the vector database...")
    add_to_DB(chunks,vector_store_path,embedding_func)
    cli_utils.print_success("Database population complete!")



def split_documents(documents:list[Document])->List[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False

    )
    with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    TimeRemainingColumn(),
    TimeElapsedColumn(),
    console=cli_utils.console
    ) as progress:
        task = progress.add_task("[cyan]Splitting text...", total=len(documents))
        chunked_documents=[]
        for i ,doc in enumerate(documents):
            chunked_documents.extend(text_splitter.split_documents([doc]))
            progress.update(task,advance=1)
    cli_utils.print_info(f"Generated {len(chunked_documents)} chunks.")
    return chunked_documents



def calculate_chunk_ids(chunks:List[Document])->List[Document]:
    last_source_page_id = None
    current_chunk_idx = 0 
    for chunk in chunks:
        src = chunk.metadata.get("source")
        page = chunk.metadata.get("page","0")
        current_source_page_id = f"{src}:{page}"

        if current_source_page_id ==last_source_page_id:
            current_chunk_idx+=1
        else:
            current_chunk_idx =0
        
        chunk_id=f"{current_source_page_id}:{current_chunk_idx}"
        last_source_page_id=current_source_page_id
        chunk.metadata["id"]=chunk_id
    return chunks


def add_to_DB(chunks: List[Document], vector_store_path: str, embedding_func: Any):
    db = Chroma(
        persist_directory=vector_store_path,
        embedding_function=embedding_func
    )
    chunks_with_ids = calculate_chunk_ids(chunks)
    
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    cli_utils.print_info(f"Number of existing documents in DB: {len(existing_ids)}")

    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)
    if len(new_chunks):
        cli_utils.print_info(f"👉 Adding {len(new_chunks)} new documents...")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks,ids=new_chunk_ids)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            TimeElapsedColumn(),
            console=cli_utils.console
        ) as progress:
            task = progress.add_task("[green]Adding chunks to DB...", total=len(new_chunks))
            batch_size=100
            for i in range(0,len(new_chunks),batch_size):
                batch=new_chunks[i:i+batch_size]
                batch_ids=new_chunk_ids[i:i+batch_size]
                db.add_documents(batch,ids=batch_ids)
                progress.update(task,advance=len(batch))
        cli_utils.print_success(f"Added {len(new_chunks)} new documents to the database.")
    else:
        cli_utils.print_info("✅ No new documents to add.")




def clear_DB(vector_store_path:str):
    if os.path.exists(vector_store_path):
        shutil.rmtree(vector_store_path)
    else:
        cli_utils.print_warning(f"Database directory '{vector_store_path}' does not exist. Nothing to clear.")


