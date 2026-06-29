from rich.console import Console

from executive_runtime import ExecutiveRuntime


console = Console()

console.rule("[cyan]CortexOne Executive Runtime[/cyan]")

runtime = ExecutiveRuntime()

runtime.boot("coo")

prompt = runtime.ask(

    "What should we work on today?"

)

from llm_adapter import LLMAdapter

adapter = LLMAdapter()

response = adapter.ask(prompt)

from response_parser import ResponseParser

parser = ResponseParser()

result = parser.parse(response)

console.print()

console.rule("[green]COO Response[/green]")

console.print(result)