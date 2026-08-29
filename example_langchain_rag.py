"""
Example RAG chain following the langchain-research skill conventions.
Use case: answer a question against the same pgvector doc_embeddings
store the FastAPI endpoint above populates.
"""

from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings


# --- 1. Structured output instead of freeform text ------------------------

class ResearchAnswer(BaseModel):
    answer: str = Field(description="Direct answer to the question")
    sources: list[str] = Field(description="Titles or URLs of documents cited")
    confidence: float = Field(ge=0, le=1, description="Model's self-rated confidence")


parser = PydanticOutputParser(pydantic_object=ResearchAnswer)


# --- 2. Prompt kept out of the orchestration logic -------------------------
# In a real project this lives in prompts/research_qa.yaml, not inline.

SYSTEM_PROMPT = """\
You are a research assistant answering questions strictly from the provided
context. If the context does not contain the answer, say so explicitly —
never fabricate a citation.

{format_instructions}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ]
).partial(format_instructions=parser.get_format_instructions())


# --- 3. Retriever over the shared pgvector store ---------------------------

def build_retriever(supabase_client, table_name: str = "doc_embeddings", k: int = 5):
    store = SupabaseVectorStore(
        client=supabase_client,
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        table_name=table_name,
        query_name="match_doc_embeddings",  # matching SQL function in Supabase
    )
    return store.as_retriever(search_kwargs={"k": k})


def format_docs(docs) -> str:
    return "\n\n".join(f"[{d.metadata.get('title', 'untitled')}] {d.page_content}" for d in docs)


# --- 4. Retry wrapper for the flaky-provider case --------------------------

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def _invoke_llm(chain, inputs: dict) -> ResearchAnswer:
    return await chain.ainvoke(inputs)


# --- 5. Assemble the LCEL chain --------------------------------------------

def build_research_qa_chain(supabase_client, model: str = "gpt-4o-mini"):
    retriever = build_retriever(supabase_client)
    llm = ChatOpenAI(model=model, temperature=0)

    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | parser
    )
    return chain


async def answer_research_question(supabase_client, question: str) -> ResearchAnswer:
    chain = build_research_qa_chain(supabase_client)
    try:
        return await _invoke_llm(chain, question)
    except Exception as exc:
        # Surface a typed failure instead of letting a raw provider error
        # propagate — the FastAPI layer maps this to a clean 502/503.
        raise RuntimeError(f"research QA chain failed after retries: {exc}") from exc
