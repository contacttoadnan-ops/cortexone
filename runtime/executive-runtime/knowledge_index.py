"""
CortexOne Knowledge Index

Version: 1.0

Purpose
-------
Scans the CortexOne repository and builds a lightweight
index of every document.

The index stores metadata only.

Document contents are loaded later by the Retriever.
"""

from pathlib import Path
import json

from config import EXECUTIVE_OS, EXECUTIVES


SUPPORTED_EXTENSIONS = (
    ".md",
    ".yaml",
    ".yml",
)


class KnowledgeIndex:

    def __init__(self):

        self.documents = []

    # ====================================================
    # Build
    # ====================================================

    def build(self):

        self.documents = []

        self._scan(EXECUTIVE_OS)

        self._scan(EXECUTIVES)

        return self.documents

    # ====================================================
    # Scan Directory
    # ====================================================

    def _scan(self, root: Path):

        if not root.exists():
            return

        for file in root.rglob("*"):

            if not file.is_file():
                continue

            if file.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            self.documents.append(

                {

                    "name": file.name,

                    "path": str(file),

                    "relative_path": str(file.relative_to(root)),

                    "extension": file.suffix.lower(),

                    "size": file.stat().st_size,

                    "keywords": self._keywords(file),

                }

            )

    # ====================================================
    # Keyword Extraction
    # ====================================================

    def _keywords(self, file: Path):

        words = set()

        #
        # Filename
        #

        filename = (

            file.stem

            .replace("-", " ")

            .replace("_", " ")

            .lower()

        )

        words.update(filename.split())

        #
        # First 20 lines only
        #

        try:

            with open(

                file,

                "r",

                encoding="utf-8",

                errors="ignore"

            ) as f:

                for _ in range(20):

                    line = f.readline()

                    if not line:
                        break

                    line = (

                        line

                        .replace("#", " ")

                        .replace("-", " ")

                        .replace("_", " ")

                        .lower()

                    )

                    words.update(line.split())

        except Exception:

            pass

        #
        # Remove tiny words
        #

        return sorted(

            [

                w

                for w in words

                if len(w) > 3

            ]

        )

    # ====================================================
    # Save
    # ====================================================

    def save(

        self,

        filename="knowledge_index.json"

    ):

        with open(

            filename,

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                self.documents,

                f,

                indent=2,

                ensure_ascii=False

            )

    # ====================================================
    # Statistics
    # ====================================================

    def stats(self):

        return {

            "documents": len(self.documents),

            "markdown":

                len(

                    [

                        d

                        for d in self.documents

                        if d["extension"] == ".md"

                    ]

                ),

            "yaml":

                len(

                    [

                        d

                        for d in self.documents

                        if d["extension"] in (".yaml", ".yml")

                    ]

                )

        }