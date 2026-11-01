/**
 * Shared visual testing utilities — import in all component tests
 */

// Standard viewport sizes matching Percy/Chromatic
export const VIEWPORTS = {
  mobile: { width: 375, height: 812 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1280, height: 720 }
} as const;

// CSS to disable all animations/transitions for stable snapshots
export const DISABLE_ANIMATIONS_CSS = `
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-delay: 0.01ms !important;
    transition-duration: 0.01ms !important;
    transition-delay: 0.01ms !important;
  }
`;

// Component showcase wrapper — consistent padding/layout
export function ShowcaseLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      {children}
    </div>
  );
}

// Generate data-testid for variants
export function testId(component: string, element?: string) {
  return element ? `${component}:${element}` : component;
}
