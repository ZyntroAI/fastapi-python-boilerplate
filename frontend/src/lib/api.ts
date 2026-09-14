// Type-safe API client for the ZyntroAI backend.
const BASE = import.meta.env.VITE_API_URL ?? "/api/v1";

export interface Item {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface Health {
  status: string;
  env: string;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error((body as { detail?: string; message?: string }).detail ?? (body as { message?: string }).message ?? `HTTP ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<Health>("/../health"),
  listItems: () => request<Item[]>("/items"),
  createItem: (body: { name: string; description?: string }) =>
    request<Item>("/items", { method: "POST", body: JSON.stringify(body) }),
  getItem: (id: number) => request<Item>(`/items/${id}`),
  updateItem: (id: number, body: { name?: string; description?: string }) =>
    request<Item>(`/items/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  deleteItem: (id: number) => request<void>(`/items/${id}`, { method: "DELETE" }),
};
