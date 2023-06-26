import { expect, test } from '@playwright/test';

test('app', async ({ page }) => {
  await page.goto('/');
  expect(true).toBe(true);
});
