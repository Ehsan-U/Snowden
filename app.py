import os.path

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from linkedin_ai.core import messanger

console = Console()

def display_title():
    title = Text("Welcome To SalesGPT", style="bold magenta")
    console.print(Panel(title, expand=False, border_style="blue"))

def auth():
    console.print("Authenticating...", style="bold green")
    if os.path.exists("./data/cookies.json"):
        os.remove("./data/cookies.json")
    bot = messanger.Messanger()
    bot.run()

def chat():
    console.print("Starting Chat...\n", style="bold green")
    bot = messanger.Messanger()
    bot.run()

def main():
    display_title()
    modes = {
        "1": {
            "name": "Auth",
            "description": "refresh the linkedin session"
        },
        "2": {
            "name": "Chat",
            "description": "start the chatbot"
        }
    }
    console.print("Available Modes:\n", style="bold yellow")
    for key, value in modes.items():
        console.print(f"{key}. {value['name']} - {value['description']}")

    mode = Prompt.ask("\nSelect a mode", default="2")
    if mode == "1":
        auth()
    elif mode == "2":
        chat()
    else:
        console.print("Invalid Mode", style="bold red")

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        console.print("\nExiting...", style="bold red")

