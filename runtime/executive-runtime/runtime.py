from rich.console import Console

from executive_runtime import ExecutiveRuntime


console = Console()

console.rule("[cyan]CortexOne Executive Runtime[/cyan]")

runtime = ExecutiveRuntime()

runtime.boot("coo")

console.print()

console.rule("[green]Runtime Status[/green]")

console.print(runtime.status())

console.print()

console.rule("[yellow]Founder Question[/yellow]")

response = runtime.ask(

    "What should we work on today?"

)

console.print(response)