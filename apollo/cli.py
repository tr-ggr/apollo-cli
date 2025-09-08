import os
import typer
from dotenv import load_dotenv
from apollo.core import GeminiAPIHandler, FileHandler
from apollo.models import Content

app = typer.Typer(
    name="apollo-cli",
    help="A sleek CLI for quick knowledge search and OSINT.",
    no_args_is_help=True,
    rich_help_panel=True
)

@app.command(
    name="search",
    help="Quick knowledge search for CTF tools and concepts.",
    no_args_is_help=True,
)
def search_mode(
    prompt: str = typer.Argument(..., help="The search query."),
):
    """
    Performs a quick knowledge search for CTF-related questions.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        typer.echo("Error: GEMINI_API_KEY not found in .env file.", err=True)
        raise typer.Exit(code=1)

    try:
        handler = GeminiAPIHandler(api_key=api_key)
        content = Content(prompt=prompt)
        response_text = handler.generate_response(content)
        typer.echo(response_text)
    except Exception as e:
        typer.echo(f"Error: An API error occurred. {e}", err=True)
        raise typer.Exit(code=1)


@app.command(
    name="osint",
    help="OSINT mode for analyzing images.",
    no_args_is_help=True,
)
def osint_mode(
    prompt: str = typer.Argument(..., help="The OSINT question related to the image."),
    file: str = typer.Option(
        None, "--file", "-f", help="Path to a local image file."
    ),
    url: str = typer.Option(
        None, "--url", "-u", help="URL of an image."
    ),
):
    """
    Performs OSINT on an image from a local path or URL.
    """
    if not (file or url):
        typer.echo("Error: You must provide either a --file or a --url.", err=True)
        raise typer.Exit(code=1)

    if file and url:
        typer.echo("Error: You can only provide one of --file or --url.", err=True)
        raise typer.Exit(code=1)

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        typer.echo("Error: GEMINI_API_KEY not found in .env file.", err=True)
        raise typer.Exit(code=1)
        
    try:
        file_handler = FileHandler()
        image_data = None
        mime_type = None

        if file:
            image_data, mime_type = file_handler.get_image_from_path(file)
        elif url:
            image_data, mime_type = file_handler.get_image_from_url(url)
        
        handler = GeminiAPIHandler(api_key=api_key)
        content = Content(prompt=prompt, image_data=image_data, mime_type=mime_type)
        response_text = handler.generate_response(content)
        typer.echo(response_text)

    except (FileNotFoundError, ValueError, ConnectionError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: An API error occurred. {e}", err=True)
        raise typer.Exit(code=1)

# The main entry point for the CLI is in run.py