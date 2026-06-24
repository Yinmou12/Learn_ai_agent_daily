import sys
from app.cli import handle_cli_error, run_cli

if __name__ == "__main__":
    debug = "--debug" in sys.argv
    try:
        run_cli()
    except Exception as error:
        handle_cli_error(error, debug)