"""
CortexOne Response Parser

Normalizes responses returned from LLMs.
"""

from datetime import datetime


class ResponseParser:

    def parse(self, response: str):

        return {

            "timestamp": datetime.now().isoformat(),

            "status": "success",

            "summary": response.strip(),

            "provider": "ollama"

        }