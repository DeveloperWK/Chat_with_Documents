import os
import sys
from typing import Any


from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt 
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress,SpinnerColumn,TextColumn

import cli_utils
import vector_store_manager



PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""



_console=Console()


def print_intro():
    instructions = Text.from_markup(
        "\n[bold green]📝 You can either:[/bold green]\n"
        "1. Pass your question as a CLI argument:\n"
        "   [italic]python main.py query 'Your question'[/italic]\n"
        "2. Or enter interactively below.\n\n"
        "[yellow]💡 Type 'q' and hit Enter to exit interactive mode.[/yellow]\n"
        "[yellow]💡 Type 'clear' to clear the screen.[/yellow]"
    )

    panel = Panel.fit(
        Align.left(instructions),
        title="[bold cyan]🔍 RAG Query Interface[/bold cyan]",
        border_style="bright_blue",
        padding=(1, 4)
    )

    _console.print(panel)



def main(config:dict,llm_model:Any,embedding_func:Any,query_text:str  | None =None):
    print_intro()
    try:
        db = vector_store_manager.get_vector_store(config,embedding_func)
    except Exception as e:
        cli_utils.print_error(f"Failed to initialize vector store: {e}")
        sys.exit(1)
    if query_text:
        query_rag(query_text,db,llm_model)
        return
    while True:
        try:
            query_input=Prompt.ask("🔍 Enter your query (or 'q' to quit, 'clear' to clear screen)").strip()
        except(KeyboardInterrupt,EOFError):
            cli_utils.print_info("\n👋 Exiting.")
            break
        if query_input.lower()=="q":
            cli_utils.print_info("\n👋 Exiting.")
            break
        elif query_input.lower()=="clear":
            os.system('cls' if os.name=="nt" else "clear")
            print_intro()
        elif query_input:
             query_rag(query_input, db, llm_model)


def query_rag(query_text:str,db:Chroma,llm_model:Any):
    cli_utils.print_info(f"Searching for relevant documents for: '{query_text}'")
    results = db.similarity_search_with_score(query_text, k=5) # k=5 for top 5 relevant chunks
    if not results:
        cli_utils.print_warning("No relevant documents found in the database for your query.")
        return
    context_chunk=[doc.page_content for doc,_ in results]
    context_text="\n\n---\n\n".join(context_chunk)
    prompt_template=ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    cli_utils.print_info("Generating response with LLM...")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=cli_utils.console,
        transient=True # Spinner disappears after completion
    ) as progress:
        task=progress.add_task("[cyan]Thinking...", total=None)
        try:
            response=llm_model.invoke(prompt)
            progress.stop()
            response_text=response.content if hasattr(response,"content") else str(response)
        except Exception as e :
            progress.stop()
            cli_utils.print_error(f"Error invoking LLM: {e}")
            return
    sources=[doc.metadata.get("id","unknown") for doc,_ in results]
    cli_utils.console.print("\n[bold magenta]🧠 Response:[/bold magenta]")
    cli_utils.console.print(Markdown(response_text))

    cli_utils.console.print("\n[bold yellow]📚 Sources:[/bold yellow]", style="bold yellow")
    for source_id in sorted(list(set(sources))):
        cli_utils.console.print(f"  - {source_id}")



