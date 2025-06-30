import argparse
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt 
from rich.panel import Panel
from get_embedding_func import get_embedding_function


CHROMA_PATH = "chroma"
PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""
console = Console()
def print_intro():
   console.print("[bold cyan]🔍 RAG Query Interface using Chroma + Ollama[/bold cyan]")
   console.print(Panel.fit(
    "[bold green]📝 You can either:[/bold green]\n"
    "1. Pass your question as a CLI argument:\n   [italic]python script.py 'Your question'[/italic]\n"
    "2. Or enter interactively below.\n\n"
    "[yellow]💡 Type 'q' and hit Enter to exit interactive mode.[/yellow]",
    title="Instructions",
    border_style="bright_blue"
))

def main():
    print_intro()

    parser = argparse.ArgumentParser(description="Query a RAG pipeline using a local vector DB and Ollama model.")
    parser.add_argument("query_text", type=str, nargs="?", help="The query text to search and answer.")
    args = parser.parse_args()

    # If query provided via CLI
    if args.query_text:
        query_rag(args.query_text)
        return

    # Else enter interactive mode
    while True:
        try:
            query_text = Prompt.ask("🔍 Enter your query (or 'q' to quit)").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Exiting.")
            break

        if query_text.lower() == "q":
            print("👋 Exiting.")
            break
        elif query_text:
            query_rag(query_text)

def query_rag(query_text: str) -> str:
    embedding_func = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_func)
    results = db.similarity_search_with_score(query_text, k=5)
    context_chunks = [doc.page_content for doc, _ in results]
    context_text = "\n\n---\n\n".join(context_chunks)

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = OllamaLLM(model="mistral")
    response = model.invoke(prompt)

    sources = [doc.metadata.get("id", "unknown") for doc, _ in results]
    console.print("\n[bold magenta]🧠 Response:[/bold magenta]")
    console.print(Markdown(response))  # for pretty formatting

    console.print("\n[bold yellow]📚 Sources:[/bold yellow]", style="bold yellow")
    console.print(sources)


    return response

if __name__ == "__main__":
    main()
