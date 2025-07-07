# %%
import argparse
import sys

import cli_utils
import config_manager
import llm_manager
import embedding_manager
import vector_store_manager

import populate_db
import query_data

def setup_wizard(config:dict)->dict:
    cli_utils.print_info("🚀 Starting setup wizard for Chat with Documents!")
    cli_utils.print_info("Let's configure your AI service, models, and data storage.")
    cli_utils.print_info("\n--- AI Service Selection ---")
    selected_service = llm_manager.select_ai_service(config)
    config["preferred_ai_service"] = selected_service
    config_manager.save_config(config)
    cli_utils.print_success(f"Selected AI Service: [bold green]{selected_service.upper()}[/bold green]")
    cli_utils.print_info("\n--- Chat Model Selection ---")
    try:
        llm_manager.select_chat_model(config)
        config_manager.save_config(config)
        cli_utils.print_success(f"Selected Chat Model: [bold green]{config.get(f'{selected_service}_chat_model', 'N/A')}[/bold green]")
    except Exception as e:
        cli_utils.print_error(f"Failed to set up chat model: {e}")
        cli_utils.print_info("Please resolve the issue and run setup again.")
        sys.exit(1) # Exit if chat model setup fails
    cli_utils.print_info("\n--- Embedding Model Selection ---")
    try:
        embedding_manager.select_embedding_model(config)
        config_manager.save_config(config)
        cli_utils.print_success(f"Selected Embedding Model: [bold green]{config.get(f'{selected_service}_embedding_model', 'N/A')}[/bold green]")
    except Exception as e:
        cli_utils.print_error(f"Failed to set up embedding model: {e}")
        cli_utils.print_info("Please resolve the issue and run setup again.")
        sys.exit(1) # Exit if embedding model setup fails
    cli_utils.print_info("\n--- Vector Store Location ---")
    vector_store_manager.set_vector_store_path(config)
    config_manager.save_config(config)
    cli_utils.print_success(f"Vector Store Path: [bold green]{config['vector_store_path']}[/bold green]")

    cli_utils.print_success("\n✅ Setup complete! Your preferences have been saved.")
    return config


def main():
    config=config_manager.load_config()
    parser=argparse.ArgumentParser(
        description="Chat with your documents using various AI models.",
        formatter_class=argparse.RawTextHelpFormatter # For better help text formatting
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run the interactive setup wizard to configure AI services, models, and data paths."
    )
    subparsers=parser.add_subparsers(dest="command",help="Available commands")
    populate_parser=subparsers.add_parser(
        "populate-db",
        help="Load documents from the 'data/' directory, chunk them, create embeddings, and store them in the vector database.",
        description="This command processes your documents and prepares them for querying.\n"
                    "Ensure your PDF, DOCX, or image files are in the 'data/' directory."
    )
    populate_parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear the existing vector database before adding new documents."
    )
    query_parser=subparsers.add_parser(
        "query",
        help="Ask questions about your documents using the configured AI model.",
        description="Enter interactive mode to chat with your documents.\n"
                    "Alternatively, provide a query directly as an argument."
    )
    query_parser.add_argument(
        "query_text",
        type=str,
        nargs="?", # Optional argument
        help="The specific question to ask about your documents. If not provided, enters interactive mode."
    )
    args=parser.parse_args()
    if args.setup or not config_manager.is_configured(config):
        config=setup_wizard(config)
        if not args.command:
            cli_utils.print_info("\nSetup complete. You can now run 'python main.py populate-db' or 'python main.py query'.")
            sys.exit(0)
    if not config_manager.is_configured(config):
        cli_utils.print_error("Configuration is incomplete. Please run 'python main.py --setup' first.")
        sys.exit(1)
    if args.command=="populate-db":
        cli_utils.print_info("\n--- Populating Document Database ---")
        try:
            embedding_func=embedding_manager.get_embedding_function(config)
            populate_db.main(config,embedding_func,reset_db=args.reset)
        except Exception as e:
            cli_utils.print_error(f"Error during database population: {e}")
            sys.exit(1)
    elif args.command=="query":
        cli_utils.print_info("\n--- Querying Documents ---")
        try:
            llm_model=llm_manager.get_chat_llm(config)
            embedding_func=embedding_manager.get_embedding_function(config)
            query_data.main(config, llm_model, embedding_func, query_text=args.query_text) # type: ignore
        except Exception as e :
            cli_utils.print_error(f"Error during query: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        if not args.command:
            sys.exit(0)
        else:
            sys.exit(1)



if __name__=="__main__":
    main()


