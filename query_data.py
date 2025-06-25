import argparse

from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

from get_embedding_func import get_embedding_function

CHROMA_PATH = "chroma"
PROMPT_TEMPLATE="""
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}

"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text",type=str,help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)

def query_rag(query_text):
    embedding_func = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_func)

    results = db.similarity_search_with_score(query_text,k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc,_source in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text,question=query_text)
    model = OllamaLLM(model="mistral")
    res_text = model.invoke(prompt)

    # src = [doc.metadata.get("id", None) for doc, _score in results]
    src = []
    for doc, _ in results:
        doc_id = doc.metadata.get("id")
        src.append(doc_id if doc_id else "unknown")


    formatted_res = f"Response: {res_text}\nSources: {src}"
    print(formatted_res)
    return res_text


if __name__=="__main__":
    main()


