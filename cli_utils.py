import sys
import time
import requests

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner

console = Console()

# ---------------------- UI OUTPUT FUNCTIONS ----------------------

def print_intro(title: str, instructions: str):
    panel = Panel.fit(
        Text(instructions, justify="left"),
        title=Text(title, style="bold cyan"),
        border_style="bright_blue",
        padding=(1, 2)
    )
    console.print(panel)


def print_info(message: str):
    console.print(f"[blue]ℹ️ {message}[/blue]")


def print_warning(message: str):
    console.print(f"[yellow]⚠️ {message}[/yellow]")


def print_error(message: str):
    console.print(f"[bold red]❌ {message}[/bold red]")


def print_success(message: str):
    console.print(f"[bold green]✅ {message}[/bold green]")

# ---------------------- PROMPT FUNCTIONS ----------------------

def select_from_list(prompt_message: str, options: list, default_index: int = 0) -> str:
    if not options:
        print_error("No options provided for selection.")
        sys.exit(1)

    console.print(f"\n[bold]{prompt_message}[/bold]")
    for i, option in enumerate(options):
        console.print(f"[cyan]{i + 1}.[/cyan] {option}")

    while True:
        try:
            choice_str = Prompt.ask(
                "Enter the number of your choice",
                choices=[str(i + 1) for i in range(len(options))],
                default=str(default_index + 1)
            )
            return options[int(choice_str) - 1]
        except ValueError:
            print_error("Invalid input. Please enter a number from the list.")
        except IndexError:
            print_error("Invalid choice. Please select a number within the range.")
        except (KeyboardInterrupt, EOFError):
            print_info("🚪 Operation cancelled. Exiting.")
            sys.exit(0)


def get_user_input(prompt_message: str, default_value: str = "") -> str:
    try:
        return Prompt.ask(prompt_message, default=default_value).strip()
    except (KeyboardInterrupt, EOFError):
        print_info("🚪 Operation cancelled. Exiting.")
        sys.exit(0)


def confirm_action(message: str, default: bool = True) -> bool:
    try:
        return Confirm.ask(message, default=default)
    except (KeyboardInterrupt, EOFError):
        print_info("🚪 Operation cancelled. Exiting.")
        sys.exit(0)

# ---------------------- SPINNER & STATUS ----------------------

def show_spinner(text: str, duration: int = 0):
    if duration > 0:
        with Live(Spinner("dots", text=Text(text, style="cyan")), refresh_per_second=8):
            time.sleep(duration)
    else:
        print_info(f"⏳ {text}...")


# ---------------------- OLLAMA STATUS CHECK ----------------------

def check_ollama_server_running(base_url: str = "http://localhost:11434") -> bool:
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        response.raise_for_status()
        return True
    except requests.exceptions.ConnectionError:
        print_error(f"Could not connect to Ollama server at {base_url}. Please ensure Ollama is running.")
        return False
    except requests.exceptions.ConnectTimeout:
        print_error(f"Timed out connecting to Ollama server at {base_url}. It might be slow to respond.")
        return False
    except requests.exceptions.RequestException as e:
        print_error(f"An unexpected error occurred while checking Ollama server:\n{e}")
        return False
