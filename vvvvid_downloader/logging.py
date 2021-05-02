import typer


def error(message: str) -> None:
    prefix = typer.style("[ERROR:]", fg=typer.colors.BRIGHT_RED)
    typer.echo(f"{prefix} {message}")


def info(message: str) -> None:
    prefix = typer.style("[INFO:]", fg=typer.colors.BRIGHT_GREEN)
    typer.echo(f"{prefix} {message}")
