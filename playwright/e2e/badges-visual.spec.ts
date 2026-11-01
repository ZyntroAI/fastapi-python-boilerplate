import { test } from '@playwright/test';
import { percySnapshot } from '@percy/playwright';

test.describe('Badges — Playwright', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/badge-showcase');
    await page.addStyleTag({ content: `* { transition: none !important; animation: none !important; }` });
  });

  test('Variants — Light', async ({ page }) => {
    await page.getByTestId('badge-variants').waitFor();
    await percySnapshot(page, 'PW — Badge Variants (Light)');
  });

  test('Variants — Dark', async ({ page }) => {
    await page.evaluate(() => document.documentElement.classList.add('dark'));
    await percySnapshot(page, 'PW — Badge Variants (Dark)');
  });

  test('Responsive — Mobile', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await percySnapshot(page, 'PW — Badges Mobile');
  });
});
