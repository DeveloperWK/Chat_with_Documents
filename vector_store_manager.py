import os 


import cli_utils


from typing import Any,List
from langchain_chroma import Chroma



def set_vector_store_path(config:dict):
    current_path = config.get("vector_store_path", "chroma")
    cli_utils.print_info(f"Current vector store path: [bold yellow]{current_path}[/bold yellow]")
    cli_utils.print_info("This is where your document embeddings will be saved.")

    while True:
        suggested_path=cli_utils.get_user_input(
            "Enter the desired directory for your vector store (absolute path or relative to current directory)",
            default_value=current_path
        )
        resolved_path=os.path.abspath(suggested_path)
        if not os.path.isabs(resolved_path):
            cli_utils.print_warning("It's recommended to use an absolute path or ensure the relative path is stable.")
        try:
            os.makedirs(resolved_path,exist_ok=True)
            test_file=os.path.join(resolved_path,".test_write")
            with open(test_file,"w") as f:
                f.write("test")
            os.remove(test_file)

            cli_utils.print_success(f"Vector store path set to: [bold green]{resolved_path}[/bold green]")
            config["vector_store_path"]=resolved_path
            break
        except OSError as e:
            cli_utils.print_error(f"Cannot use path '{resolved_path}': {e}")
            cli_utils.print_warning("Please ensure the path is valid and you have write permissions.")
        except Exception as e:
            cli_utils.print_error(f"An unexpected error occurred while validating path: {e}")
            cli_utils.print_warning("Please try a different path.")



def get_vector_store(config:dict,embedding_function:Any)->Chroma:
    vector_store_path = config.get("vector_store_path")
    if not vector_store_path:
        raise ValueError("Vector store path is not configured. Please run setup.")
    cli_utils.print_info(f"Initializing Chroma vector store at: [blue]{vector_store_path}[/blue]")
    try:
        os.makedirs(vector_store_path,exist_ok=True)
        db = Chroma(
            persist_directory=vector_store_path,
            embedding_function=embedding_function
        )
        cli_utils.print_success("Chroma vector store initialized successfully.")
        return db
    except Exception as e:
        cli_utils.print_error(f"Failed to initialize Chroma vector store at '{vector_store_path}': {e}")
        raise




