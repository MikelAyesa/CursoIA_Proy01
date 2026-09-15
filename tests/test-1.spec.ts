import { test, expect } from '@playwright/test';

test('Debería buscar Logroño con éxito y redirigir a su artículo', async ({ page }) => {
  await page.goto('https://www.wikipedia.org/');
  await page.getByRole('searchbox', { name: 'Search Wikipedia' }).fill('logroño');
  await page.getByRole('searchbox', { name: 'Search Wikipedia' }).press('Enter');
  await expect(page).toHaveURL(/Logro%C3%B1o/);
});