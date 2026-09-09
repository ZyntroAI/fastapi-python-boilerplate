import { useEffect, useState } from "react";
import { api, type Item } from "./lib/api";

export function App() {
  const [items, setItems] = useState<Item[]>([]);
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<string>("checking…");

  useEffect(() => {
    api.health().then((h) => setHealth(h.status)).catch(() => setHealth("offline"));
    refresh();
  }, []);

  async function refresh() {
    setItems(await api.listItems());
  }

  async function create() {
    setError(null);
    if (!name.trim()) return;
    try {
      await api.createItem({ name: name.trim() });
      setName("");
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "create failed");
    }
  }

  return (
    <main style={{ fontFamily: "system-ui", maxWidth: 640, margin: "3rem auto", padding: "0 1rem" }}>
      <h1>ZyntroAI Console</h1>
      <p>
        Backend: <strong>{health}</strong>
      </p>

      <div style={{ display: "flex", gap: 8, margin: "1rem 0" }}>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && create()}
          placeholder="New item name"
          aria-label="Item name"
        />
        <button onClick={create}>Add</button>
      </div>
      {error && <p style={{ color: "crimson" }}>{error}</p>}

      <ul>
        {items.map((it) => (
          <li key={it.id}>
            {it.name} <span style={{ color: "#888" }}>#{it.id}</span>
          </li>
        ))}
      </ul>
    </main>
  );
}
