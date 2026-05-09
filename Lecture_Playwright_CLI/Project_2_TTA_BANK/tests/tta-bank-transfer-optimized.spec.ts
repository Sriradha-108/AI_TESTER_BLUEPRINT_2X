import { test, expect } from '@playwright/test';

/**
 * Optimized TTA Bank Test Script
 * - Uses 'domcontentloaded' for faster navigation
 * - Minimizes redundant assertions
 * - Focuses on direct locators
 */

test.describe('TTA Bank - Performance Optimized Flow', () => {
  
  test('Transfer funds and verify balance', async ({ page }) => {
    // 1. Open with 'domcontentloaded' to avoid waiting for all assets (images/fonts)
    await page.goto('https://tta-bank-digital-973242068062.us-west1.run.app/', { timeout: 60000 });

    // 2. Fast Signup
    await page.getByRole('button', { name: 'Sign Up' }).click();
    
    const id = Date.now().toString().slice(-6);
    await page.getByPlaceholder('John Doe').fill(`User${id}`);
    await page.getByPlaceholder('you@example.com').fill(`user${id}@test.com`);
    await page.getByPlaceholder('••••••••').fill('Pass123!');
    
    // Using Promise.all for navigation-heavy clicks can sometimes be faster, 
    // but Playwright's auto-waiting is usually sufficient.
    await page.getByRole('button', { name: 'Create Account' }).click();

    // 3. Quick Verification & Transfer
    // We wait for the 'Dashboard' heading to ensure we've landed
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
    
    // Navigate to Transfer
    await page.getByRole('button', { name: 'Transfer Funds' }).click();
    
    // Fill transfer details
    await page.getByRole('spinbutton').fill('5000');
    await page.getByRole('button', { name: 'Continue' }).click();

    // Confirm Transfer
    await page.getByRole('button', { name: 'Confirm Transfer' }).click();

    // 4. Return to Dashboard and Verify
    // Instead of waiting for a success toast, we go straight to verify the state
    await page.getByRole('button', { name: 'Dashboard' }).first().click();
    
    // Assert 45k balance - text matching is fast
    await expect(page.getByText('45,000')).toBeVisible();

    // 5. Cleanup
    await page.getByRole('button', { name: 'Sign Out' }).click();
  });

});
