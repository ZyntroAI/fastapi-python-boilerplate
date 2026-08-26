import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

export async function getItems() {
  const response = await axios.get(`${API_URL}/items`);
  return response.data;
}

export async function createItem(item) {
  const response = await axios.post(`${API_URL}/items`, item);
  return response.data;
}
