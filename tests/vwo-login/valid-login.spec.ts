// spec: Lecture_playwright_AI_Agents/web.vwo/preview_vwo_login.test-plan.md
// seed: Lecture_playwright_AI_Agents/web.vwo/seed.spec.js

import { test, expect } from '@playwright/test';

test.describe('Happy Path - Email/Password Login', () => {
  test('Valid Login with Correct Credentials', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify page loads at login URL
    expect(page.url()).toContain('app.vwo.com');
    
    // Verify email input field is visible and focused
    const emailField = page.getByRole('textbox', { name: 'Email address' });
    await expect(emailField).toBeVisible();
    
    // Verify password input field is visible
    const passwordField = page.getByRole('textbox', { name: 'Password' });
    await expect(passwordField).toBeVisible();
    
    // Verify password visibility toggle button is present
    const toggleButton = page.getByRole('button', { name: 'Toggle password visibility' });
    await expect(toggleButton).toBeVisible();
    
    // Enter valid test email
    await emailField.fill('test@vwo.com');
    await expect(emailField).toHaveValue('test@vwo.com');
    
    // Enter valid test password (masked should be visible)
    await passwordField.fill('TestPassword123');
    
    // Verify password field has focus and value is masked
    const inputType = await passwordField.getAttribute('type');
    expect(inputType).toBe('password');
    
    // Verify Sign in button is visible and enabled
    const signInButton = page.getByRole('button', { name: 'Sign in', exact: true });
    await expect(signInButton).toBeVisible();
    await expect(signInButton).toBeEnabled();
  });
});
