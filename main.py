from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.theme import Theme
import requests
import json
import itertools

console = Console()

# ----------- THEMES -----------
THEMES = {
    "Light": Theme({
        "user": "bold black on white",
        "ai": "bold blue on white",
        "system": "dim cyan",
        "banner": "bold magenta"
    }),
    "Dark": Theme({
        "user": "bold white",
        "ai": "bold green",
        "system": "dim cyan",
        "banner": "bold magenta"
    }),
    "Terminal": Theme({
        "user": "bold green",
        "ai": "bold light_green",
        "system": "dim green",
        "banner": "bold green"
    }),
    # Rainbow handled separately
}

RAINBOW_COLORS = ["red", "orange1", "yellow1", "green", "cyan", "blue", "magenta"]

# ----------- DEFAULT SYSTEM PROMPT -----------
DEFAULT_SYSTEM_PROMPT = (
    "You're a chill, funny Hack Clubber who talks like a real person in a group chat. "
    "Keep your replies informal, friendly, and upbeat—use slang, emojis, and memes if it fits! "
    "Don't be stiff or overly formal. If someone says \"Wsp\", you might reply with \"Not much, you?\", "
    "\"Hey hey!\", or \"Just vibing! What about you?\". Make sure your replies are short, to the point, "
    "and sound like a real teen hacker. If you don't know something, just say so in a casual way."
)

# ----------- RAINBOW TEXT UTILS -----------
def rainbow_text(text):
    words = text.split(' ')
    colored_words = []
    color_cycle = itertools.cycle(RAINBOW_COLORS)
    for word in words:
        color = next(color_cycle)
        colored_words.append(f"[{color}]{word}[/{color}]")
    return ' '.join(colored_words)

# ----------- MENU UI -----------
def show_menu():
    console.print(Panel("[bold magenta]TerminalCraft AI[/bold magenta] - [cyan]Main Menu[/cyan]", expand=False))
    console.print("[bold]1.[/bold] Theme")
    console.print("[bold]2.[/bold] System Prompt")
    console.print("[bold]3.[/bold] Start Chat")
    console.print("[bold]4.[/bold] Quit\n")

def theme_menu():
    console.print("\n[bold cyan]Select a Theme:[/bold cyan]")
    for idx, theme in enumerate(list(THEMES.keys()) + ["Rainbow"], 1):
        console.print(f"{idx}. {theme}")
    sel = Prompt.ask("[yellow]Choose a theme number[/yellow]", choices=[str(i) for i in range(1, len(THEMES)+2)], default="2")
    theme_choice = (list(THEMES.keys()) + ["Rainbow"])[int(sel)-1]
    return theme_choice

def system_prompt_menu():
    console.print("\n[bold cyan]Customize the AI's Personality![/bold cyan]")
    console.print("Press [green]ENTER[/green] to keep the [bold]default casual Hack Clubber[/bold] vibe, or type your own prompt below.")
    prompt = Prompt.ask("[yellow]System Prompt[/yellow]", default=DEFAULT_SYSTEM_PROMPT)
    return prompt

def print_banner(theme_choice):
    if theme_choice == "Rainbow":
        console.print(rainbow_text("Welcome to TerminalCraft AI!"))
    else:
        with console.use_theme(THEMES[theme_choice]):
            console.print("[banner]Welcome to TerminalCraft AI![/banner]")

# ----------- PRINTING UTILS -----------
def ai_print(text, theme_choice):
    # Capitalize first letter, ensure ends with punctuation
    text = text.strip()
    if text:
        if not text[0].isupper():
            text = text[0].upper() + text[1:]
        if text[-1] not in ".!?":
            text += "."
    if theme_choice == "Rainbow":
        console.print(rainbow_text(text))
    else:
        with console.use_theme(THEMES[theme_choice]):
            console.print(f"[ai]{text}[/ai]")

def user_print(text, theme_choice):
    if theme_choice == "Rainbow":
        console.print(rainbow_text(text))
    else:
        with console.use_theme(THEMES[theme_choice]):
            console.print(f"[user]{text}[/user]")

# ----------- CHAT LOOP -----------
def chat_loop(system_prompt, theme_choice):
    chat_history = [{"role": "system", "content": system_prompt}]
    print_banner(theme_choice)
    while True:
        user_msg = Prompt.ask("\n[bold blue]You[/bold blue]")
        if user_msg.strip().lower() in {"exit", "quit"}:
            ai_print("Goodbye! 👋", theme_choice)
            break
        chat_history.append({"role": "user", "content": user_msg})
        ai_response = get_ai_response(chat_history)
        if ai_response:
            chat_history.append({"role": "assistant", "content": ai_response})
            ai_print(ai_response, theme_choice)
        else:
            ai_print("Error: No response from AI.", theme_choice)

# ----------- HACK CLUB AI API -----------
def get_ai_response(history):
    url = "https://ai.hackclub.com/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    recent_history = history[-10:] if len(history) > 10 else history
    payload = {"messages": recent_history}
    try:
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        else:
            return f"API Error: {resp.status_code}"
    except Exception as e:
        return f"API call failed: {e}"

# ----------- MAIN -----------
if __name__ == "__main__":
    theme_choice = "Dark"
    system_prompt = DEFAULT_SYSTEM_PROMPT
    while True:
        show_menu()
        choice = Prompt.ask("[bold yellow]Choose an option[/bold yellow]", choices=["1", "2", "3", "4"], default="3")
        if choice == "1":
            theme_choice = theme_menu()
        elif choice == "2":
            system_prompt = system_prompt_menu()
        elif choice == "3":
            chat_loop(system_prompt, theme_choice)
            break
        elif choice == "4":
            console.print("[bold red]Goodbye![/bold red]")
            break