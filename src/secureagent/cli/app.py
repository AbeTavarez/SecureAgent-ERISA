import typer

app = typer.Typer(
    name="secureagent",
    help="SecureAgent CLI /clear to reset, /help to show commands",
    no_args_is_help=True,
)

# ===== Commands =====


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Host to run the API on"),
    port: int = typer.Option(8000, help="Port to run the API on"),
    reload: bool = typer.Option(True, help="Reload the API on code changes"),
):
    """Serve the CRM SecureAgent API."""
    from secureagent.main import run as run_api  # lazy import to avoid circular imports

    run_api(host=host, port=port, reload=reload)


@app.command()
def chat(
    prompt: str | None = typer.Option(
        None, "--prompt", "-p", help="Run a single prompt non-interactively"
    ),
    show_metadata: bool = typer.Option(
        False, "--show-metadata", "-m", help="Show the full message metadata"
    ),
    thread_id: str | None = typer.Option(
        None, "--thread-id", "-t", help="Thread ID to use for the conversation"
    ),
):
    """Runs the ERISA agent with the given prompt."""
    # (import ssl) forces Python to initialize OpenSSL's AppLink first, so when Langfuse/Groq load their SSL stack afterward, they don't crash. TODO: Remove this after lazy loading is implemented in secureagent.agents.nodes.py
    import ssl
    from secureagent.agents.graph import run_agent
    import uuid

    if prompt:
        messages = run_agent(prompt, thread_id=thread_id or str(uuid.uuid4()))
        typer.echo(f"SecureAgent: {messages['messages'][-1].content}")
        if show_metadata:
            typer.echo(f"\nMetadata: {messages['metadata']}")
        return

    typer.echo("SecureAgent Chat (ctrl+c to exit, /clear to reset)")

    session_thread = thread_id or str(uuid.uuid4())
    typer.echo(f"Session Thread: {session_thread}")

    while True:
        user_input = typer.prompt("You")
        command = user_input.strip().lower()

        if command == "/help":
            typer.echo("Commands: /help — show this help; /clear, /reset — start a new conversation")
            continue

        if command in ["/clear", "/reset"]:
            session_thread = str(uuid.uuid4())
            typer.echo(f"Conversation cleared. New session: {session_thread}")
            continue
        
        if not user_input.strip():
            typer.echo("Please enter a message.")
            continue

        messages = run_agent(user_input, thread_id=session_thread)
        typer.echo(f"\n\nSecureAgent: {messages['messages'][-1].content}")
        
        if show_metadata:
            typer.echo(f"\nMetadata: {messages['metadata']}")


def main() -> None:
    app(prog_name="secureagent")


if __name__ == "__main__":
    main()
