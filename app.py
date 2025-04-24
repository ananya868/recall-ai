#!/usr/bin/env python3
import os
import sys
import json
import asyncio
from typing import List
import platform
from pydantic import BaseModel, Field
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import print as rprint
from rich.table import Table
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import your existing modules
# Assuming all your processor classes are in a file called flashcard_processors.py
# and FlashCardGenerator is in a file called flashcard_generator.py
from core import (
    ProcessTextInput, ProcessImageInput, ProcessAudioInput, 
    ProcessPDF, ProcessLink, ProcessTopic, ProcessUserBackground, 
    UserBio, FlashCardGenerator
)

# Import the factory and service
from core import ContentProcessorFactory, FlashCardService

# Initialize Rich console
console = Console()

# Define emojis based on input types
INPUT_EMOJI = {
    "text": "📝",
    "image": "🖼️",
    "audio": "🎙️",
    "pdf": "📄",
    "link": "🔗",
    "topic": "🧠",
    "user_bio": "👤"
}

# Define colors for different input types
INPUT_COLORS = {
    "text": "green",
    "image": "blue",
    "audio": "yellow",
    "pdf": "red",
    "link": "cyan",
    "topic": "magenta",
    "user_bio": "bright_green"
}

def clear_screen():
    """Clear the terminal screen."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def display_header():
    """Display the app header."""
    clear_screen()
    console.print(Panel.fit(
        "[bold yellow]🧠 AI Flash Card Generator 🧠[/bold yellow]\n"
        "[italic cyan]Generate custom flash cards from various inputs![/italic cyan]",
        border_style="bright_yellow",
        padding=(1, 10)
    ))

def display_input_options():
    """Display the available input options."""
    table = Table(title="[bold]Available Input Types[/bold]", show_header=True, header_style="bold magenta")
    table.add_column("Option", style="dim", width=6)
    table.add_column("Input Type", style="bright_yellow")
    table.add_column("Description", style="green")
    
    table.add_row("1", f"{INPUT_EMOJI['text']} Text", "Enter text directly")
    table.add_row("2", f"{INPUT_EMOJI['image']} Image", "Process text from an image file")
    table.add_row("3", f"{INPUT_EMOJI['audio']} Audio", "Transcribe audio recording")
    table.add_row("4", f"{INPUT_EMOJI['pdf']} PDF", "Extract content from a PDF file")
    table.add_row("5", f"{INPUT_EMOJI['link']} Web Link", "Retrieve content from a URL")
    table.add_row("6", f"{INPUT_EMOJI['topic']} Topic", "Generate content on a specific topic")
    table.add_row("7", f"{INPUT_EMOJI['user_bio']} User Bio", "Personalize based on user demographics")
    table.add_row("0", "🚪 Exit", "Quit the application")
    
    console.print(table)

def get_user_bio():
    """Get user bio information."""
    console.print("\n[bold green]👤 Enter User Demographics:[/bold green]")
    
    name = Prompt.ask("👤 Name")
    
    age = None
    while age is None:
        try:
            age = int(Prompt.ask("🔢 Age"))
        except ValueError:
            console.print("[red]Please enter a valid number for age[/red]")
    
    degree_name = Prompt.ask("🎓 Degree name")
    
    degree_year = None
    while degree_year is None:
        try:
            degree_year = int(Prompt.ask("📅 Degree year"))
        except ValueError:
            console.print("[red]Please enter a valid number for degree year[/red]")
    
    course_name = Prompt.ask("📚 Course name")
    
    interested_subjects_input = Prompt.ask("🧠 Interested subjects (comma separated)")
    interested_subjects = [subj.strip() for subj in interested_subjects_input.split(",")]
    
    return UserBio(
        name=name,
        age=age,
        degree_name=degree_name,
        degree_year=degree_year,
        course_name=course_name,
        interested_subjects=interested_subjects
    )

def display_flash_cards(flash_cards: dict):
    """Display generated flash cards in a visually appealing way."""
    if not flash_cards:
        console.print("[bold red]No flash cards were generated.[/bold red]")
        return
    
    console.print(f"\n[bold yellow]📚 {flash_cards['title']} 📚[/bold yellow]")
    console.print(f"[italic cyan]Subject: {flash_cards['subject']}[/italic cyan]")
    console.print(f"[italic cyan]Difficulty: {flash_cards['difficulty_level']}[/italic cyan]")
    console.print(f"[italic cyan]Total Cards: {flash_cards['total_cards']}[/italic cyan]\n")
    
    for i, card in enumerate(flash_cards['cards'], 1):
        importance_stars = "⭐" * card["importance"]
        console.print(Panel.fit(
            f"[bold green]Q: {card['question']}[/bold green]\n\n"
            f"[bold blue]A: {card['answer']}[/bold blue]\n\n"
            f"[dim]Category: {card['category']} | Importance: {importance_stars}[/dim]",
            title=f"Card {i}/{flash_cards['total_cards']}",
            border_style=f"{'red' if card['importance'] >= 4 else 'yellow' if card['importance'] >= 2 else 'green'}"
        ))
        
        # If not the last card, ask to continue
        if i < len(flash_cards['cards']):
            if not Confirm.ask("[cyan]View next card?[/cyan]", default=True):
                break

async def main():
    display_header()
    
    while True:
        display_input_options()
        
        choice = Prompt.ask("\n[bold]Choose an input type[/bold]", choices=["0", "1", "2", "3", "4", "5", "6", "7"])
        
        if choice == "0":
            console.print("[yellow]👋 Thank you for using the AI Flash Card Generator! Goodbye![/yellow]")
            break
        
        # Get number of cards
        num_cards = 5  # Default
        try:
            num_cards_input = Prompt.ask("\n[bold]Number of flash cards to generate[/bold] (default: 5)")
            if num_cards_input:
                num_cards = int(num_cards_input)
                if num_cards <= 0:
                    raise ValueError
        except ValueError:
            console.print("[red]Invalid number. Using default (5 cards).[/red]")
            num_cards = 5
        
        flash_card_service = FlashCardService(num_cards=num_cards)
        
        try:
            # Handle different input types
            if choice == "1":  # Text
                console.print(f"\n[bold {INPUT_COLORS['text']}]{INPUT_EMOJI['text']} Enter your text:[/bold {INPUT_COLORS['text']}]")
                text = console.input("[dim](Press Enter twice or type 'EOF' on a new line to finish)[/dim]\n")
                
                # Allow multi-line input
                buffer = []
                while True:
                    line = console.input()
                    if line.strip() == "EOF" or (not line and buffer):
                        break
                    buffer.append(line)
                
                if buffer:
                    text = text + "\n" + "\n".join(buffer)
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                ) as progress:
                    progress.add_task(description="[green]Generating flash cards...", total=None)
                    flash_cards = await flash_card_service.generate_from_input(
                        input_type="text",
                        text=text
                    )
                
            elif choice == "2":  # Image
                image_path = Prompt.ask(f"\n[bold {INPUT_COLORS['image']}]{INPUT_EMOJI['image']} Enter the path to your image[/bold {INPUT_COLORS['image']}]")
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                ) as progress:
                    progress.add_task(description="[blue]Processing image and generating flash cards...", total=None)
                    flash_cards = await flash_card_service.generate_from_input(
                        input_type="image",
                        image_path=image_path
                    )
                
            elif choice == "3":  # Audio
                audio_path = Prompt.ask(f"\n[bold {INPUT_COLORS['audio']}]{INPUT_EMOJI['audio']} Enter the path to your audio file[/bold {INPUT_COLORS['audio']}]")
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                ) as progress:
                    progress.add_task(description="[yellow]Transcribing audio and generating flash cards...", total=None)
                    flash_cards = await flash_card_service.generate_from_input(
                        input_type="audio",
                        audio_path=audio_path
                    )
                
            elif choice == "4":  # PDF
                pdf_path = Prompt.ask(f"\n[bold {INPUT_COLORS['pdf']}]{INPUT_EMOJI['pdf']} Enter the path to your PDF file[/bold {INPUT_COLORS['pdf']}]")
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                ) as progress:
                    progress.add_task(description="[red]Extracting PDF content and generating flash cards...", total=None)
                    flash_cards = await flash_card_service.generate_from_input(
                        input_type="pdf",
                        pdf_path=pdf_path
                    )
                
            elif choice == "5":  # Link
                link = Prompt.ask(f"\n[bold {INPUT_COLORS['link']}]{INPUT_EMOJI['link']} Enter the URL[/bold {INPUT_COLORS['link']}]")
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                ) as progress:
                    progress.add_task(description="[cyan]Crawling website and generating flash cards...", total=None)
                    flash_cards = await flash_card_service.generate_from_input(
                        input_type="link",
                        link=link
                    )
                
            elif choice == "6":  # Topic
                topic = Prompt.ask(f"\n[bold {INPUT_COLORS['topic']}]{INPUT_EMOJI['topic']} Enter the topic[/bold {INPUT_COLORS['topic']}]")
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                ) as progress:
                    progress.add_task(description="[magenta]Researching topic and generating flash cards...", total=None)
                    flash_cards = await flash_card_service.generate_from_input(
                        input_type="topic",
                        topic=topic
                    )
                
            elif choice == "7":  # User Bio
                user_bio = get_user_bio()
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                ) as progress:
                    progress.add_task(description="[bright_green]Personalizing content and generating flash cards...", total=None)
                    flash_cards = await flash_card_service.generate_from_input(
                        input_type="user_bio",
                        user_bio=user_bio
                    )
            
            # Display the flash cards
            display_flash_cards(flash_cards)
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
        
        # Ask if user wants to continue
        if not Confirm.ask("\n[bold yellow]Generate more flash cards?[/bold yellow]", default=True):
            console.print("[yellow]👋 Thank you for using the AI Flash Card Generator! Goodbye![/yellow]")
            break
        
        display_header()  # Refresh the header for the next iteration

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Program interrupted. Goodbye![/yellow]")
        sys.exit(0)