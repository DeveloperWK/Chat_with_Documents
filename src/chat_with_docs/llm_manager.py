import os
import requests
import sys

from typing import Any
from pydantic import SecretStr

from chat_with_docs import cli_utils


from langchain_ollama import OllamaLLM
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()



GEMINI_CHAT_MODELS=["gemini-1.5-pro-latest","gemini-1.5-flash-latest","gemini-1.0-pro-vision-latest"]
OPENAI_CHAT_MODELS=["gpt-3.5-turbo", "gpt-4o", "gpt-4"]

import sys
import platform

def _print_env_var_instructions(service_name: str, env_var_name: str):
    """Prints instructions on how to manually set an environment variable."""
    cli_utils.print_info(
        f"\n[bold]To use your {service_name.capitalize()} API Key persistently without saving it to config.json,[/bold]"
    )
    cli_utils.print_info(
        f"you can set it as an environment variable named [bold cyan]{env_var_name}[/bold cyan]."
    )
    cli_utils.print_info("Here's how to do it:\n")

    system = platform.system().lower()
    
    if system in ("linux", "darwin"):  # macOS or Linux
        cli_utils.print_info("[bold underline]For Linux/macOS (Bash/Zsh):[/bold underline]\n")
        cli_utils.print_info(" [bold yellow]Temporary (current terminal session):[/bold yellow]")
        cli_utils.console.print(f"   [green]export {env_var_name}=\"YOUR_API_KEY_HERE\"[/green]")
        cli_utils.print_info("   Then run your script in the same terminal.\n")

        cli_utils.print_info(" [bold yellow]Permanent (for all new terminals):[/bold yellow]")
        cli_utils.print_info("   Add this line to [italic]~/.bashrc[/italic], [italic]~/.zshrc[/italic], or [italic]~/.profile[/italic]:")
        cli_utils.console.print(f"   [green]export {env_var_name}=\"YOUR_API_KEY_HERE\"[/green]")
        cli_utils.print_info("   Then run [italic]source ~/.bashrc[/italic] (or equivalent), or open a new terminal.")

    elif system == "windows":
        cli_utils.print_info("[bold underline]For Windows (Command Prompt or PowerShell):[/bold underline]\n")
        cli_utils.print_info(" [bold yellow]Temporary (current terminal session):[/bold yellow]")
        cli_utils.print_info("   [italic]Command Prompt:[/italic]")
        cli_utils.console.print(f"   [green]set {env_var_name}=YOUR_API_KEY_HERE[/green]")
        cli_utils.print_info("   [italic]PowerShell:[/italic]")
        cli_utils.console.print(f"   [green]$env:{env_var_name}=\"YOUR_API_KEY_HERE\"[/green]")
        cli_utils.print_info("   Then run your script in the same terminal.\n")

        cli_utils.print_info(" [bold yellow]Permanent (system-wide):[/bold yellow]")
        cli_utils.print_info("   1. Search for [italic]'Environment Variables'[/italic] in the Windows search bar.")
        cli_utils.print_info("   2. Click [italic]'Edit the system environment variables'[/italic].")
        cli_utils.print_info("   3. Click [italic]'Environment Variables...'[/italic].")
        cli_utils.print_info("   4. Under [italic]'User variables'[/italic], click [italic]'New...'[/italic].")
        cli_utils.print_info(f"      - Variable name: [bold cyan]{env_var_name}[/bold cyan]")
        cli_utils.print_info("      - Variable value: your API key")
        cli_utils.print_info("   5. Click OK and open a new terminal to apply the changes.")

    else:
        cli_utils.print_warning(f"Unrecognized platform: [italic]{sys.platform}[/italic]. Please set the variable manually.")

    cli_utils.print_info("\n🔐 Remember to replace [bold yellow]\"YOUR_API_KEY_HERE\"[/bold yellow] with your actual API key.\n")


def get_api_key(service_name:str,config:dict)->str|None:
    env_var_name=f"{service_name.upper()}_API_KEY"
    env_api_key=os.getenv(env_var_name) 
    config_key_name=f"{service_name}_api_key"
    found_api_key = None
    if env_api_key:
        cli_utils.print_info(f"Using {service_name.capitalize()} API key from environment variable '[bold cyan]{env_var_name}[/bold cyan]'.")
        found_api_key = env_api_key
    elif config.get(config_key_name):
        cli_utils.print_info(f"Using {service_name.capitalize()} API key from config.json (previously loaded).")
        found_api_key = config[config_key_name]
    if not found_api_key:
        cli_utils.print_warning(f"No {service_name.capitalize()} API key found in environment variable '{env_var_name}'.")
        cli_utils.print_info(f"Please visit the respective platform to get your API key:")
        match service_name:
            case "gemini":
                cli_utils.print_info("  - Google AI Studio: [https://ai.google.dev/gemini-api/docs/api-key](https://ai.google.dev/gemini-api/docs/api-key)")
            case "openai":
                cli_utils.print_info("  - OpenAI Platform: [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)")
        api_key_input=cli_utils.get_user_input(f"Enter your {service_name.capitalize()} API Key (or leave blank to skip):")
        if api_key_input:
            found_api_key=api_key_input
            if cli_utils.confirm_action(f"Do you want to save this {service_name.capitalize()} API Key in config.json? (Less secure than environment variables)", default=False):
                config[config_key_name] = found_api_key
                cli_utils.print_success(f"{service_name.capitalize()} API Key will be saved to config.json.")
            else:
                cli_utils.print_info(f"API Key will only be used for this session.")
                _print_env_var_instructions(service_name, env_var_name)
        else:
            cli_utils.print_warning(f"No {service_name.capitalize()} API Key provided. This service may not function.")
            config[config_key_name] = None 
            return None 
    if found_api_key:
        config[config_key_name]=found_api_key
    return found_api_key


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
        config["preferred_ai_service"]=selected_service
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
                available_models=[m['name'] for m in models_data.get("models",[])]

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
                config["ollama_chat_model"]= selected_model
            except requests.exceptions.RequestException as e:
                raise Exception(f"Failed to fetch Ollama models: {e}. Ensure Ollama is running and accessible.")
            except Exception as e:
                raise e
        case "gemini":
            api_key=get_api_key("gemini",config)
            if not api_key:
                raise Exception("Gemini API key is required but not provided.")
            current_gemini_model = config.get("gemini_chat_model","gemini-pro")
            default_index=GEMINI_CHAT_MODELS.index(current_gemini_model) if current_gemini_model in GEMINI_CHAT_MODELS else 0
            selected_model = cli_utils.select_from_list(
                f"Select a Gemini chat model (Current: [bold yellow]{current_gemini_model}[/bold yellow]):",
                GEMINI_CHAT_MODELS,
                default_index=default_index
            )
            config["gemini_chat_model"]=selected_model
        case "openai":
            api_key=get_api_key("openai",config)
            if not api_key:
                raise Exception("Openai API key is required but not provided.")
            current_openai_model = config.get("openai_chat_model", "gpt-3.5-turbo")
            default_index=OPENAI_CHAT_MODELS.index(current_openai_model) if current_openai_model in OPENAI_CHAT_MODELS else 0
            selected_model = cli_utils.select_from_list(
                f"Select a Gemini chat model (Current: [bold yellow]{current_openai_model}[/bold yellow]):",
                OPENAI_CHAT_MODELS,
                default_index=default_index
            )
            config["openai_chat_model"]=selected_model
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






