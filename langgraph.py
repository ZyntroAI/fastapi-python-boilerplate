from langgraph.pregel import RetryPolicy

builder.add_node(
    "worker",
    worker_node,
    retry=RetryPolicy(max_attempts=3, retry_on=Exception)
)

# Tool timeout
async def web_search_tool(query: str):
    async with asyncio.timeout(30):
        return await search_api(query)
