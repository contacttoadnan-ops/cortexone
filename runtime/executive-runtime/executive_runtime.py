"""
CortexOne Executive Runtime

This is the heart of CortexOne.

Responsibilities:
- Boot executives
- Load Executive OS
- Load executive packages
- Build runtime context
- Prepare prompts for AI models
"""

from rich.console import Console

from loader import (
    load_executive_os,
    load_executive,
)

from context_loader import build_context


class ExecutiveRuntime:

    def __init__(self):

        self.console = Console()

        self.executive_name = None

        self.executive_os = []

        self.executive_package = []

        self.context = None

    # ----------------------------------------------------
    # Boot Executive
    # ----------------------------------------------------

    def boot(self, executive: str):

        self.executive_name = executive.lower()

        self.console.rule(f"[cyan]Booting {self.executive_name.upper()}[/cyan]")

        self.console.print("Loading Executive OS...")

        self.executive_os = load_executive_os()

        self.console.print(
            f"[green]✓[/green] {len(self.executive_os)} Executive OS documents loaded"
        )

        self.console.print()

        self.console.print(f"Loading {self.executive_name.upper()} package...")

        self.executive_package = load_executive(self.executive_name)

        self.console.print(
            f"[green]✓[/green] {len(self.executive_package)} Executive documents loaded"
        )

        self.console.print()

        self.console.print("Building runtime context...")

        self.context = build_context(
            self.executive_os,
            self.executive_package,
        )

        self.console.print("[green]✓ Context Ready[/green]")

        return self

    # ----------------------------------------------------
    # Ask Executive
    # ----------------------------------------------------

    def ask(self, founder_message: str):

        from prompt_builder import PromptBuilder

        builder = PromptBuilder()

        builder.add_system(
            "You are running inside CortexOne Executive Runtime."
        )

        builder.add_identity(self.executive_name)

        builder.add_context(self.context)

        builder.add_founder_request(founder_message)

        builder.add_timestamp()

        return builder.build()

    # ----------------------------------------------------
    # Status
    # ----------------------------------------------------

    def status(self):

        return {

            "executive": self.executive_name,

            "executive_os_documents": len(self.executive_os),

            "executive_documents": len(self.executive_package),

            "context_ready": self.context is not None

        }