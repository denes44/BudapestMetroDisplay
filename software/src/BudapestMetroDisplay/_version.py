from pathlib import Path

# you can use os.path and open() as well
__version__ = Path(__file__).parent.joinpath("VERSION").read_text()
