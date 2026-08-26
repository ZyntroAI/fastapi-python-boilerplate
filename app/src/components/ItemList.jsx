import { useEffect, useState } from "react";
import { getItems } from "../api/items";

export default function ItemList() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    getItems().then(setItems);
  }, []);

  return (
    <div>
      <h2>Items</h2>
      <ul>
        {items.map((i) => (
          <li key={i.id}>{i.name} - {i.description}</li>
        ))}
      </ul>
    </div>
  );
}
