import { test, expect } from '@playwright/test';

test('seed planner data', async ({ page }) => {
  await page.goto('https://your-app-url.com');

  // Create a task
  await page.click('#add-task');
  await page.fill('#task-name', 'Sample Task');
  await page.click('#save');

  // Verify task is added
  await expect(page.locator('text=Sample Task')).toBeVisible();
});