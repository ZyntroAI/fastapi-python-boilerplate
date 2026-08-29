---
name: langchain-research
description: This skill should be used when the user asks to "build a RAG pipeline", "orchestrate an LLM chain", "add a vector store", "write a research agent", or design prompt templates and multi-step reasoning workflows with LangChain.
when_to_use: Apply when creating or modifying document-retrieval systems, prompt templates, vector-store integrations, or agentic research workflows built on LangChain.
argument-hint: [chain-or-research-task]
disable-model-invocation: false
user-invocable: true
allowed-tools: Read Edit Write Glob Grep Bash(pytest *) WebFetch
disallowed-tools: AskUserQuestion
paths:
  - "chains/**/*.py"
  - "research/**/*.py"
  - "prompts/**/*.txt"
  - "prompts/**/*.yaml"
  - "vectorstores/**/*.py"
effort: high
---

# LangChain Research Orchestration

Expert instructions for building robust LLM-powered research tools using LangChain.

## Core principles

- **Modularity**: compose chains from discrete components using LCEL (LangChain Expression Language).
- **Traceability**: enable verbose logging or LangSmith tracing so reasoning steps can be audited.
- **Prompt decoupling**: keep prompt templates in versioned files, separate from orchestration logic.
- **State management**: use the memory component that matches the conversation shape — don't default to full-history buffers for long research sessions.

## Pipeline architecture

### 1. RAG (retrieval-augmented generation)
- **Ingestion**: use recursive character splitting sized for research-paper structure (respect section boundaries where possible).
- **Retrieval**: query the vector store (Chroma, Pinecone, etc.) with semantic search; add re-ranking when precision matters more than recall.
- **Context assembly**: format retrieved chunks clearly (source, section) so the LLM can cite them.

### 2. Chain & agent construction
- Use `SequentialChain` (or LCEL pipes) for multi-step literature reviews: extract → summarize → synthesize.
- Give agents scoped research tools (search, Arxiv/PubMed lookups) rather than unrestricted web access.
- Use `OutputParsers` (or structured output via Pydantic) so research findings return in a predictable JSON shape.

### 3. Prompt engineering
- Use few-shot examples for complex extraction tasks where format matters.
- Write an explicit system message defining the assistant's role and constraints — don't rely on the default persona.
- Inject research context through input variables, not string concatenation.

### 4. Performance & reliability
- Add retry logic (exponential backoff) for flaky LLM providers.
- Use `astream` / `astream_events` for real-time feedback in research UIs.
- Summarize long-running research history before it re-enters the prompt, to control token cost.

## Example usage

- **Document QA**: load a PDF, chunk and embed it, answer technical questions with citations.
- **Synthesis agent**: search multiple sources and compile a structured summary report.

## Evaluation

- Build an evaluation chain that grades outputs against ground-truth answers.
- Watch for hallucinated citations or claims not present in retrieved context — flag them rather than silently passing.
