from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode

# 1. Define the State
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. Define a Tool
def calculator(operation: str, a: float, b: float) -> float:
    """Perform basic arithmetic: add, subtract, multiply, divide."""
    if operation == "add": return a + b
    if operation == "subtract": return a - b
    if operation == "multiply": return a * b
    if operation == "divide": return a / b
    raise ValueError("Unknown operation")

tools = [calculator]

# 3. Set up the LLM with tools
llm = init_chat_model("openai:gpt-4.1")
llm_with_tools = llm.bind_tools(tools)

# 4. Define Nodes
def agent(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

tool_node = ToolNode(tools=tools)

# 5. Conditional routing: does the LLM want to call a tool?
def should_continue(state: State):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# 6. Build the Graph
builder = StateGraph(State)
builder.add_node("agent", agent)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
builder.add_edge("tools", "agent")  # Loop back after tool execution

graph = builder.compile()

# 7. Run it
result = graph.invoke({
    "messages": [{"role": "user", "content": "What is a million times 408?"}]
})
print(result["messages"][-1].content)
# Output: "A million times 408 is 408,000,000."
                         
