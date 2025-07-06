
import os
import requests

from typing import Any
from pydantic import SecretStr

import cli_utils
import config_manager

from langchain_ollama import OllamaLLM
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()



GEMINI_CHAT_MODELS=["gemini-pro","gemini-1.5-flash","gemini-1.0-pro"]
OPENAI_CHAT_MODELS=["gpt-3.5-turbo", "gpt-4o", "gpt-4"]



def get_api_key(service_name:str)->str|None:
    env_var_name=f"{service_name.upper()}_API_KEY"
    api_key=os.getenv(env_var_name)
    if api_key:
        cli_utils.print_info(f"Using {service_name.capitalize()} API key from environment variable '{env_var_name}'.")
        return api_key
    cli_utils.print_warning(f"No {service_name.capitalize()} API key found in environment variable '{env_var_name}'.")
    cli_utils.print_info(f"Please visit the respective platform to get your API key:")
    match service_name:
        case "gemini":
            cli_utils.print_info("  - Google AI Studio: [https://ai.google.dev/gemini-api/docs/api-key](https://ai.google.dev/gemini-api/docs/api-key)")
        case "openai":
            cli_utils.print_info("  - OpenAI Platform: [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)")
    api_key=cli_utils.get_user_input(f"Enter your {service_name.capitalize()} API Key (or leave blank to skip):")
    if api_key:
        if cli_utils.confirm_action(f"Do you want to save this {service_name.capitalize()} API Key in config.json? (Less secure than environment variables)", default=False):
            config = config_manager.load_config()
            config[f"{service_name}_api_key"]=api_key
            config_manager.save_config(config)
            cli_utils.print_success(f"{service_name.capitalize()} API Key saved to config.json.")
        return api_key
    else:
        cli_utils.print_warning(f"No {service_name.capitalize()} API Key provided. This service may not function.")
        return None


def select_ai_service(config:dict)->str:
    options = ["Ollama (Local)", "Gemini (Google)", "OpenAI"]
    current_service=config.get("preferred_ai_service", "ollama").capitalize()
    default_index=0
    match current_service:
        case "Gemini":
            default_index=1
        case "Openai":
            default_index=2
    selected_option=cli_utils.select_from_list(
        f"Select your preferred AI service (Current: [bold yellow]{current_service}[/bold yellow]):",
        options,
        default_index=default_index
    )
    selected_service=selected_option.split(" ")[0].lower()
    if selected_service != config.get("preferred_ai_service"):
        config_manager.set_setting("preferred_ai_service", selected_service)
        cli_utils.print_success(f"Preferred AI service set to: [bold green]{selected_service.upper()}[/bold green]")
    return selected_service


def select_chat_model(config:dict):
    service = config.get("preferred_ai_service")
    selected_model=None
    
    match service:
        case "ollama":
            cli_utils.print_info("Checking Ollama server status...")
            if not cli_utils.check_ollama_server_running():
                raise Exception("Ollama server is not running. Please start Ollama before selecting a model.")
            try:
                cli_utils.show_spinner("Fetching available Ollama models...", duration=0)
                response = requests.get("http://localhost:11434/api/tags",timeout=10)
                response.raise_for_status()
                models_data=response.json()
                available_models=[m['name'] for m in models_data.get("model",[])]
                if not available_models:
                    raise Exception("No Ollama models found. Please pull models (e.g., 'ollama pull mistral') and try again.")
                cli_utils.console.print("\n")
                current_ollama_model= config.get("ollama_chat_model","mistral")
                default_index=available_models.index(current_ollama_model) if current_ollama_model in available_models else 0

                selected_model = cli_utils.select_from_list(
                f"Select an Ollama chat model (Current: [bold yellow]{current_ollama_model}[/bold yellow]):",
                available_models,
                default_index=default_index
                )
                config_manager.set_setting("ollama_chat_model", selected_model)
            except requests.exceptions.RequestException as e:
                raise Exception(f"Failed to fetch Ollama models: {e}. Ensure Ollama is running and accessible.")
            except Exception as e:
                raise e
        case "gemini":
            api_key=get_api_key("gemini")
            if not api_key:
                raise Exception("Gemini API key is required but not provided.")
            current_gemini_model = config.get("gemini_chat_model","gemini-pro")
            default_index=GEMINI_CHAT_MODELS.index(current_gemini_model) if current_gemini_model in GEMINI_CHAT_MODELS else 0
            selected_model = cli_utils.select_from_list(
                f"Select a Gemini chat model (Current: [bold yellow]{current_gemini_model}[/bold yellow]):",
                GEMINI_CHAT_MODELS,
                default_index=default_index
            )
            config_manager.set_setting("gemini_chat_model", selected_model)
        case "openai":
            api_key=get_api_key("openai")
            if not api_key:
                raise Exception("Openai API key is required but not provided.")
            current_openai_model = config.get("openai_chat_model", "gpt-3.5-turbo")
            default_index=OPENAI_CHAT_MODELS.index(current_openai_model) if current_openai_model in OPENAI_CHAT_MODELS else 0
            selected_model = cli_utils.select_from_list(
                f"Select a Gemini chat model (Current: [bold yellow]{current_openai_model}[/bold yellow]):",
                OPENAI_CHAT_MODELS,
                default_index=default_index
            )
            config_manager.set_setting("openai_chat_model", selected_model)
            if selected_model:
                cli_utils.print_success(f"Chat model for {service.upper()} set to: [bold green]{selected_model}[/bold green]")
            else:
                cli_utils.print_warning(f"No chat model selected for {service.upper()}.")


def get_chat_llm(config:dict)->Any:
    service=config.get("preferred_ai_service")
    match service:
        case "ollama":
            model_name=config.get("ollama_chat_model")
            if not model_name:
                 raise ValueError("Ollama chat model not configured. Please run setup.")
            cli_utils.print_info(f"Initializing OllamaLLM with model: {model_name}")
            return OllamaLLM(model=model_name)
        case "gemini":
            model_name=config.get("gemini_chat_model")
            api_key=config.get("gemini_api_key") or os.getenv("GEMINI_API_KEY")
            if not model_name or not api_key:
                raise ValueError("Gemini chat model or API key not configured. Please run setup.")
            cli_utils.print_info(f"Initializing ChatGoogleGenerativeAI with model: {model_name}")
            return ChatGoogleGenerativeAI(model=model_name,google_api_key=SecretStr(api_key))
        case "openai":
            model_name=config.get("openai_chat_model")
            api_key=config.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
            if not model_name or not api_key:
                raise ValueError("OpenAI chat model or API key not configured. Please run setup.")
            cli_utils.print_info(f"Initializing ChatOpenAI with model: {model_name}")
            return ChatOpenAI(model=model_name, api_key=SecretStr(api_key))
        case _:
             raise ValueError(f"Unsupported AI service configured: {service}. Please run setup.")






