import json
import os

from rich.console import Console
from rich.text import Text


_console=Console()


DEFAULT_CONFIG={
    "preferred_ai_service":"ollama",
    "ollama_chat_model":"mistral",
    "ollama_embedding_model": "mxbai-embed-large",
    "gemini_chat_model": "gemini-pro", 
    "openai_chat_model": "gpt-3.5-turbo", 
    "vector_store_path": "chroma",   
}


def get_config_file_path()->str:
    home_dir=os.path.expanduser("~")
    app_config_dir=os.path.join(home_dir,".chat_with_docs")
    config_file=os.path.join(app_config_dir,"config.json")
    return config_file


def load_config()->dict:
    config_path = get_config_file_path()
    try:
        if os.path.exists(config_path):
            with open(config_path) as f:
                settings=json.load(f)
                merged_settings=DEFAULT_CONFIG.copy()
                merged_settings.update(settings)
                _console.print(f"[green]Configuration loaded from {config_path}[/green]")
                return merged_settings
        else:
            _console.print(f"[yellow]Configuration file not found at {config_path}. Using default settings.[/yellow]")
            return DEFAULT_CONFIG.copy()
    except json.JSONDecodeError:
        _console.print(f"[bold red]Error: Invalid JSON in config file {config_path}. Using default settings.[/bold red]")
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        _console.print(f"[bold red]An unexpected error occurred loading config: {e}. Using default settings.[/bold red]")
        return DEFAULT_CONFIG.copy()





def save_config(settings:dict):
    config_path = get_config_file_path()
    app_config_dir=os.path.dirname(config_path)
    try:
        os.makedirs(app_config_dir,exist_ok=True)
        with open(config_path,'w')as f:
            json.dump(settings,f,indent=4)
        _console.print(f"[green]Configuration saved to {config_path}[/green]")
    except IOError as e:
         _console.print(f"[bold red]Error: Could not save configuration to {config_path}: {e}[/bold red]")
    except Exception as e:
         _console.print(f"[bold red]An unexpected error occurred saving config: {e}[/bold red]")

         


def get_setting(key:str,default=None):
    config=load_config()
    return config.get(key,default)




def set_setting(key:str,value):
    config = load_config()
    config[key] = value
    save_config(config)


def is_configured(config:dict)->bool:
    required_settings = [
        "preferred_ai_service",
        "vector_store_path",
    ]
    for setting in required_settings:
        if setting not in config or not config[setting]:
            return False
    service = config.get("preferred_ai_service")
    match service:
        case"ollama":
            if not config.get("ollama_chat_model") or not config.get("ollama_embedding_model"):
                return False
        case "gemini":
            if not config.get("gemini_chat_model"):
                return False
        case "openai":
            if not config.get("openai_chat_model"):
                return False
    return True






