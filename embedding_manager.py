# %%
import os 
import sys
import requests

from typing import List,Dict,Any
from pydantic import SecretStr

import cli_utils
import config_manager
import llm_manager

from langchain_ollama import OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings

# %%
OLLAMA_EMBEDDING_MODELS_KNOWN_BASE_NAMES = ["nomic-embed-text", "mxbai-embed-large", "bge-large"]
GEMINI_EMBEDDING_MODELS = ["gemini-embedding-001", "text-embedding-004"]
OPENAI_EMBEDDING_MODELS = ["text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large"]

# %%
def get_base_model_name(full_model_name: str) -> str:
    """
    Extracts the base model name from a full Ollama model name (e.g., 'model:tag' -> 'model').
    """
    return full_model_name.split(':')[0]

# %%
def select_embedding_model(config:dict):
    service=config.get("preferred_ai_service")
    selected_model=None
    match service:
        case "ollama":
            cli_utils.show_spinner("Checking Ollama server status for embedding models...")
            if not cli_utils.check_ollama_server_running():
                raise Exception("Ollama server is not running. Please start Ollama before selecting an embedding model.")
            try:
                cli_utils.show_spinner("Fetching available Ollama models...", duration=0) 
                response = requests.get("http://localhost:11434/api/tags", timeout=10)
                response.raise_for_status()
                models_data = response.json()
                available_ollama_models = [m['name'] for m in models_data.get('models', [])]
                if not available_ollama_models:
                    raise Exception("No Ollama models found. Please pull models (e.g., 'ollama pull mistral') and try again.")
                embedding_options=[]
                general_llm_options=[]
                for model_full_name in available_ollama_models:
                    base_name=get_base_model_name(model_full_name)
                    if base_name in OLLAMA_EMBEDDING_MODELS_KNOWN_BASE_NAMES:
                        embedding_options.append(model_full_name)
                    else:
                        general_llm_options.append(model_full_name)                             
                if embedding_options:
                    cli_utils.print_info("Found dedicated Ollama embedding models:")
                    current_ollama_embedding_model = config.get("ollama_embedding_model")
                    if current_ollama_embedding_model not in embedding_options:
                        current_ollama_embedding_model=embedding_options[0]
                    default_index=embedding_options.index(current_ollama_embedding_model)
                    selected_model=cli_utils.select_from_list(
                        f"Select an Ollama embedding model (Current: [bold yellow]{current_ollama_embedding_model}[/bold yellow]):",
                        embedding_options,
                        default_index=default_index
                    )
                    config_manager.set_setting("ollama_embedding_model", selected_model)
                else:
                    cli_utils.print_warning(
                    "No dedicated embedding models (e.g., 'nomic-embed-text', 'mxbai-embed-large') "
                    "were found on your local Ollama instance."
                    )
                    cli_utils.print_info(
                        "It is highly recommended to pull one for better search quality. "
                        "You can pull one by running 'ollama pull nomic-embed-text' in your terminal."
                        )
                    if general_llm_options:
                        if cli_utils.confirm_action(
                        "Do you want to proceed with a general-purpose LLM for embeddings (may yield lower quality)?",
                        default=False
                        ):
                            current_ollama_embedding_model=config.get("ollama_embedding_model", general_llm_options[0])
                            default_index=general_llm_options.index(current_ollama_embedding_model) if current_ollama_embedding_model in general_llm_options else 0
                            selected_model=cli_utils.select_from_list(
                            f"Select a general-purpose Ollama model for embeddings (Current: [bold yellow]{current_ollama_embedding_model}[/bold yellow]):",
                            general_llm_options,
                            default_index=default_index
                            )
                            config_manager.set_setting("ollama_embedding_model",selected_model)
                        else:
                            cli_utils.print_info("Exiting to allow you to pull a dedicated embedding model.")
                            sys.exit(0)
                    else:
                        raise Exception("No Ollama models (neither embedding nor general-purpose) found. Cannot proceed with Ollama embeddings.")

            except requests.exceptions.RequestException as e:
                raise Exception(f"Failed to fetch Ollama models: {e}. Ensure Ollama is running and accessible.")
            except Exception as e:
                raise e
        case "gemini":
            api_key = llm_manager.get_api_key("gemini")
            if not api_key:
                raise Exception("Gemini API key is required but not provided for embeddings.")
            current_gemini_embedding_model = config.get("gemini_embedding_model", GEMINI_EMBEDDING_MODELS[0])
            default_index=GEMINI_EMBEDDING_MODELS.index(current_gemini_embedding_model) if current_gemini_embedding_model in GEMINI_EMBEDDING_MODELS else 0

            selected_model=cli_utils.select_from_list(
                 f"Select a Gemini embedding model (Current: [bold yellow]{current_gemini_embedding_model}[/bold yellow]):",
                 GEMINI_EMBEDDING_MODELS,
                 default_index=default_index
            )
            config_manager.set_setting("gemini_embedding_model", selected_model)
        
        case "openai":
            api_key=llm_manager.get_api_key("openai")
            if not api_key:
                raise Exception("OpenAI API key is required but not provided for embeddings.")
            current_openai_embedding_model = config.get("openai_embedding_model", OPENAI_EMBEDDING_MODELS[0])
            default_index=OPENAI_EMBEDDING_MODELS.index(current_openai_embedding_model) if current_openai_embedding_model in OPENAI_EMBEDDING_MODELS else 0

            selected_model = cli_utils.select_from_list(
            f"Select an OpenAI embedding model (Current: [bold yellow]{current_openai_embedding_model}[/bold yellow]):",
            OPENAI_EMBEDDING_MODELS,
            default_index=default_index
            )
            config_manager.set_setting("openai_embedding_model", selected_model)
            if selected_model:
                cli_utils.print_success(f"Embedding model for {service.upper()} set to: [bold green]{selected_model}[/bold green]")
            else:
                cli_utils.print_warning(f"No embedding model selected for {service.upper()}.")


# %%
def get_embedding_function(config:dict)-> Any:
    service =config.get("preferred_ai_service")
    if service =="ollama":
         model_name = config.get("ollama_embedding_model")
         if not model_name or not model_name.strip():
              raise ValueError("Ollama embedding model not configured. Please run setup.")
         cli_utils.print_info(f"Initializing OllamaEmbeddings with model: {model_name}")
         return OllamaEmbeddings(model=model_name)
    elif service =="gemini":
         model_name=config.get("gemini_embedding_model")
         api_key = config.get("gemini_api_key") or os.getenv("GEMINI_API_KEY")
         if not api_key or not model_name:
              raise ValueError("Gemini embedding model or API key not configured. Please run setup.")
         cli_utils.print_info(f"Initializing GoogleGenerativeAIEmbeddings with model: {model_name}")
         return GoogleGenerativeAIEmbeddings(model=model_name,google_api_key=SecretStr(api_key))
    elif service =="openai":
         model_name=config.get("openai_embedding_model")
         api_key=config.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
         if not model_name or not api_key:
              raise ValueError("OpenAI embedding model or API key not configured. Please run setup.")
         cli_utils.print_info(f"Initializing OpenAIEmbeddings with model: {model_name}")
         return OpenAIEmbeddings(model=model_name,api_key=SecretStr(api_key))
    else:
          raise ValueError(f"Unsupported AI service configured for embeddings: {service}. Please run setup.")

# %%
if __name__ == "__main__":
    cli_utils.print_info("--- Testing embedding_manager.py ---")

    # Load initial config
    current_config = config_manager.load_config()
    cli_utils.print_info(f"Current config: {current_config}")

    # Test selecting embedding model (this will prompt based on the selected service in config)
    cli_utils.print_info("\nTesting select_embedding_model...")
    try:
        select_embedding_model(current_config)
        current_config = config_manager.load_config() # Reload after update
        cli_utils.print_info(f"Config after embedding model selection: {current_config}")
    except Exception as e:
        cli_utils.print_error(f"Error during embedding model selection test: {e}")
        # If testing Ollama and it's not running, this might exit.

    # Test getting embedding function
    cli_utils.print_info("\nTesting get_embedding_function...")
    try:
        embedding_func = get_embedding_function(current_config)
        cli_utils.print_success(f"Successfully initialized Embedding Function: {embedding_func.__class__.__name__} "
                                f"with model {embedding_func.model if hasattr(embedding_func, 'model') else 'N/A'}")
        
        # Optional: Test a small embedding to confirm it works (requires API key or Ollama running)
        # test_text = "Hello, world!"
        # cli_utils.print_info(f"Embedding '{test_text}' (first 5 values):")
        # embedding_vector = embedding_func.embed_query(test_text)
        # cli_utils.print_info(str(embedding_vector[:5]))

    except ValueError as e:
        cli_utils.print_error(f"Error getting embedding function: {e}")
    except Exception as e:
        cli_utils.print_error(f"An unexpected error occurred during embedding function test: {e}")


    # Clean up (optional: remove the created config file for fresh start)
    config_file = config_manager.get_config_file_path()
    if os.path.exists(config_file):
        cli_utils.print_info(f"\nCleaning up: Deleting {config_file}")
        os.remove(config_file)
        app_config_dir = os.path.dirname(config_file)
        if os.path.exists(app_config_dir) and not os.listdir(app_config_dir):
            os.rmdir(app_config_dir)


