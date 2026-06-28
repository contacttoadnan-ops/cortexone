"""
CortexOne Loader

Responsible for loading documents from the repository.
"""

from pathlib import Path

from config import EXECUTIVE_OS, EXECUTIVES


SUPPORTED_EXTENSIONS = (".md", ".yaml", ".yml")


def _load_directory(path: Path):

    documents = []

    if not path.exists():
        return documents

    for file in sorted(path.rglob("*")):

        if not file.is_file():
            continue

        if file.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:

            content = file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

        except Exception as e:

            content = f"<<ERROR READING FILE: {e}>>"

        documents.append({

            "name": file.name,

            "path": str(file),

            "relative_path": str(file.relative_to(path)),

            "extension": file.suffix,

            "content": content

        })

    return documents


def load_executive_os():

    return _load_directory(EXECUTIVE_OS)


def load_executive(executive_name: str):

    executive_path = EXECUTIVES / executive_name.lower()

    return _load_directory(executive_path)