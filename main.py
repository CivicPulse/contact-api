import subprocess

import typer
import uvicorn

app = typer.Typer()
db_app = typer.Typer()
app.add_typer(db_app, name="db")


@app.command()
def serve() -> None:
    """Start the uvicorn server."""
    from app.core.config import settings

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        log_config=None,
    )


@db_app.command("upgrade")
def db_upgrade() -> None:
    """Run alembic upgrade head."""
    subprocess.run(["alembic", "upgrade", "head"], check=True)


@db_app.command("downgrade")
def db_downgrade() -> None:
    """Run alembic downgrade -1."""
    subprocess.run(["alembic", "downgrade", "-1"], check=True)


@db_app.command("current")
def db_current() -> None:
    """Show alembic current revision."""
    subprocess.run(["alembic", "current"], check=True)


if __name__ == "__main__":
    app()
