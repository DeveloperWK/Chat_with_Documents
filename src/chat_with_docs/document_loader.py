import os
import pytesseract
from chat_with_docs import cli_utils

from typing import List
from langchain.schema.document import Document
from langchain_community.document_loaders import PyPDFLoader,Docx2txtLoader
from PIL import Image



def load_pdf(file_path:str)->List[Document]:
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        cli_utils.print_info(f"Loaded PDF: {os.path.basename(file_path)} ({len(documents)} pages)")
        return documents
    except Exception as e:
        cli_utils.print_warning(f"Could not load PDF '{os.path.basename(file_path)}': {e}")
        return []


def load_docx(file_path:str)->List[Document]:
    try:
        loader = Docx2txtLoader(file_path)
        documents = loader.load()
        if documents:
            cli_utils.print_info(f"Loaded DOCX: {os.path.basename(file_path)}")
            return documents
        else:
             cli_utils.print_warning(f"DOCX '{os.path.basename(file_path)}' loaded but no content found.")
             return []
    except Exception as e:
        cli_utils.print_warning(f"Could not load DOCX '{os.path.basename(file_path)}': {e}")
        return []
            


def load_img(file_path:str)->List[Document]:
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        if text.strip():
            document = Document(
                page_content=text.strip(),
                metadata={"source":file_path,"type":"image_ocr"}
            )
            cli_utils.print_info(f"Loaded Image (OCR): {os.path.basename(file_path)}")
            return [document]
        else:
            cli_utils.print_warning(f"No text found in image '{os.path.basename(file_path)}' after OCR.")
            return []
    except pytesseract.TesseractNotFoundError:
        cli_utils.print_error(
            "Tesseract OCR engine not found. Please install it to enable image processing. "
            "Refer to the README for installation instructions."
        )
        return []
    except FileNotFoundError:
        cli_utils.print_warning(f"Image file not found: {os.path.basename(file_path)}")
        return []
    except Exception as e:
         cli_utils.print_warning(f"Could not process image '{os.path.basename(file_path)}' for OCR: {e}")
         return []
        


def load_documents_from_directory(data_path:str)->List[Document]:
    all_documents:List[Document]=[]
    supported_extensions = {
        ".pdf":load_pdf,
        ".docx":load_docx,
        ".png":load_img,
        ".jpg":load_img,
        ".jpeg":load_img,
        ".tiff":load_img,
        ".bmp":load_img,
        ".gif":load_img,
    }
    if not os.path.exists(data_path):
        cli_utils.print_error(f"Data folder '{data_path}' not found. Please create it and add your documents.")
        return []
    if not os.listdir(data_path):
        cli_utils.print_warning(f"Data folder '{data_path}' is empty. Add some documents to load.")
        return []
    cli_utils.print_info(f"Scanning '{data_path}' for documents...")
    for root,_,files in os.walk(data_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1].lower()

            if file_extension in supported_extensions:
                loader_func = supported_extensions[file_extension]
                documents = loader_func(file_path)
                all_documents.extend(documents)
            else:
                cli_utils.print_info(f"Skipping unsupported file: {os.path.basename(file_path)}")
        if not all_documents:
            cli_utils.print_warning("No supported documents were loaded from the directory.")
        else:
            cli_utils.print_success(f"Successfully loaded {len(all_documents)} document parts from {len(files)} files.")
    return all_documents
        



