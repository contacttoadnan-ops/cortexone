"""
CortexOne Prompt Builder

Builds the final prompt sent to an LLM.
"""

from datetime import datetime


class PromptBuilder:

    def __init__(self):
        self.sections = []

    def add_system(self, text: str):
        self.sections.append(
            f"""
================ SYSTEM ================

{text}
"""
        )

    def add_identity(self, executive_name: str):
        self.sections.append(
            f"""
================ EXECUTIVE ================

You are the {executive_name.upper()} of CortexOne.

Operate according to your executive handbook,
Executive Operating System,
company constitution,
and company knowledge.

Your responsibility is to make executive-level decisions,
not engineering decisions unless specifically delegated.
"""
        )

    def add_founder_request(self, request: str):
        self.sections.append(
            f"""
================ FOUNDER REQUEST ================

{request}
"""
        )

    def add_context(self, context):

        self.sections.append(
            f"""
================ CONTEXT ================

Executive OS Documents:
{context["executive_os_documents"]}

Executive Documents:
{context["executive_documents"]}
"""
        )

    def add_timestamp(self):

        self.sections.append(
            f"""
================ TIME ================

{datetime.now().isoformat()}
"""
        )

    def build(self):

        return "\n".join(self.sections)