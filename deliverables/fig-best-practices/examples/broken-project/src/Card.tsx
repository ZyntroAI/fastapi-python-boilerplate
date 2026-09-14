/**
 * Broken example — hard-coded colours that should be tokens.
 * DESIGN reports each literal with its file and line.
 */
export function Card({ title }: { title: string }) {
  return (
    <div
      style={{
        background: "#ff00aa",
        color: "#333333",
        border: "1px solid #e2e8f0",
      }}
    >
      <h3 style={{ color: "rgb(0, 0, 0)" }}>{title}</h3>
    </div>
  );
}

export default Card;
