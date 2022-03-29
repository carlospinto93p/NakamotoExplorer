
from pathlib import Path


def get_project_root() -> str:
    return str(Path(__file__).parent.parent.parent)


DEBUG_MODE = False

DATA_FOLDER = f'{get_project_root()}/data'
