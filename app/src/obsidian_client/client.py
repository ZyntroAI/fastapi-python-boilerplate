from obsidian_client import ObsidianClient

client = ObsidianClient.from_env()   # or ObsidianClient(base_url=..., api_key=...)

print(client.status())
print(client.list_vault())
print(client.get_note("Folder/Note.md"))
client.append_note("Inbox.md", "\n- new item")
