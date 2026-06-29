"""
CortexOne Executive Runtime

Core runtime responsible for:

- Booting executives
- Loading Executive OS
- Loading Executive Packages
- Building execution context
- Building AI prompts
"""

from rich.console import Console

from loader import (
    load_executive_os,
    load_executive,
)

from context_loader import build_context
from context_assembler import ContextAssembler


class ExecutiveRuntime:

    def __init__(self):

        self.console = Console()

        self.executive_name = None

        self.executive_os = []

        self.executive_package = []

        self.context = None

    # ======================================================
    # Boot Executive
    # ======================================================

    def boot(self, executive: str):

        self.executive_name = executive.lower()

        self.console.rule(
            f"[cyan]Booting {self.executive_name.upper()}[/cyan]"
        )

        #
        # Executive OS
        #

        self.console.print("Loading Executive OS...")

        self.executive_os = load_executive_os()

        self.console.print(
            f"[green]✓[/green] {len(self.executive_os)} Executive OS documents loaded"
        )

        self.console.print()

        #
        # Executive Package
        #

        self.console.print(
            f"Loading {self.executive_name.upper()} package..."
        )

        self.executive_package = load_executive(
            self.executive_name
        )

        self.console.print(
            f"[green]✓[/green] {len(self.executive_package)} Executive documents loaded"
        )

        self.console.print()

        #
        # Runtime Context
        #

        self.console.print(
            "Building runtime context..."
        )

        self.context = build_context(

            self.executive_os,

            self.executive_package

        )

        self.console.print(
            "[green]✓ Context Ready[/green]"
        )

        return self

    # ======================================================
    # Ask Executive
    # ======================================================

    def ask(self, founder_message: str):

        assembler = ContextAssembler()

        runtime_context = assembler.assemble(

            executive_name=self.executive_name,

            executive_os=self.executive_os,

            executive_package=self.executive_package,

            founder_request=founder_message

        )

        return runtime_context["prompt"]

    # ======================================================
    # Status
    # ======================================================

    def status(self):

        return {

            "executive": self.executive_name,

            "executive_os_documents": len(
                self.executive_os
            ),

            "executive_documents": len(
                self.executive_package
            ),

            "context_ready": self.context is not None

        }