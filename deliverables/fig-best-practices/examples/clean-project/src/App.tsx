/**
 * Clean example — every value comes from a design token.
 * No colour literal appears here, which is what DESIGN checks for.
 */
const TOKENS = {
  color: {
    brandPrimary: "var(--color-brand-primary)",
    surfaceBase: "var(--color-surface-base)",
    textPrimary: "var(--color-text-primary)",
  },
  space: {
    sm: "var(--space-2)",
    md: "var(--space-4)",
  },
} as const;

export type CardProps = {
  title: string;
  body: string;
};

export function Card({ title, body }: CardProps) {
  return (
    <div
      style={{
        background: TOKENS.color.surfaceBase,
        color: TOKENS.color.textPrimary,
        padding: TOKENS.space.md,
        borderRadius: "var(--radius-md)",
        border: "1px solid var(--color-border-default)",
      }}
    >
      <h3 style={{ color: TOKENS.color.brandPrimary, margin: 0 }}>{title}</h3>
      <p style={{ marginTop: TOKENS.space.sm }}>{body}</p>
    </div>
  );
}

export default Card;
