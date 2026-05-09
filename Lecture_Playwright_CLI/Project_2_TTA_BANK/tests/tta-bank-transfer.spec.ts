import { test, expect } from '@playwright/test';

test('TTA Bank Transfer Funds Flow', async ({ page }) => {
  // 1. open the https://tta-bank-digital-973242068062.us-west1.run.app/
  await page.goto('https://tta-bank-digital-973242068062.us-west1.run.app/');

  // 2. create a dummy signup with random email id, name and details
  await page.getByRole('button', { name: 'Sign Up' }).click();
  
  const randomStr = Math.random().toString(36).substring(2, 10);
  await page.getByPlaceholder('John Doe').fill(`Test User ${randomStr}`);
  await page.getByPlaceholder('you@example.com').fill(`test${randomStr}@example.com`);
  await page.getByPlaceholder('••••••••').fill('password123');
  await page.getByRole('button', { name: 'Create Account' }).click();

  // 3. verify that the 50k $ balance is present.
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await expect(page.getByText('50,000').first()).toBeVisible();

  // 4. In the Transfer Funds Tab and transfer the amount to the 5000$ to default dropdown
  await page.getByRole('button', { name: 'Transfer Funds' }).click();
  
  // Enter amount
  // First, verify we are on the transfer page
  await expect(page.getByRole('heading', { name: 'Transfer Funds' })).toBeVisible();
  
  // Fill 5000
  await page.getByRole('spinbutton').fill('5000');
  
  // Click Continue to move to Review screen
  await page.getByRole('button', { name: 'Continue' }).click();

  // 4.5 Confirm Transfer
  await expect(page.getByText('Review Transfer')).toBeVisible();
  await page.getByRole('button', { name: 'Confirm Transfer' }).click();

  // Wait for success message
  await expect(page.getByText('Transfer processed successfully')).toBeVisible();

  // 5. Verify that in the dashboard it will be the 45k $ balance.
  // Assuming it takes us back to the dashboard. If not, click Dashboard
  await page.getByRole('button', { name: 'Dashboard' }).first().click();
  
  // Note: If the app is a static mock, it might not actually update to 45k.
  // We use regex or text matching to verify what appears. The instructions say verify 45k balance.
  await expect(page.getByText('45,000').first()).toBeVisible({ timeout: 5000 }).catch(async () => {
    throw new Error("Expected $45,000 balance was not found on the dashboard after transfer.");
  });

  // 6. signout.
  await page.getByRole('button', { name: 'Sign Out' }).click();
  
  // Verify signed out by checking for Sign In button
  await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible();
});
