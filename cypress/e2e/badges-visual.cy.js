describe('Badges — Visual E2E', () => {
  beforeEach(() => {
    cy.visit('/badge-showcase');
    cy.document().then(d => d.documentElement.classList.remove('dark'));
  });

  it('All Variants — Light', () => {
    cy.get('[data-testid="badge-variants"]').should('exist');
    cy.snapshotStable('Badges — All Variants (Light)');
  });

  it('All Variants — Dark', () => {
    cy.document().then(d => d.documentElement.classList.add('dark'));
    cy.snapshotStable('Badges — All Variants (Dark)');
  });

  it('All Sizes', () => {
    cy.get('[data-testid="badge-sizes"]').should('exist');
    cy.snapshotStable('Badges — Sizes');
  });
});
