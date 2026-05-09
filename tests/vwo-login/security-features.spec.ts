// spec: Lecture_playwright_AI_Agents/web.vwo/preview_vwo_login.test-plan.md
// seed: Lecture_playwright_AI_Agents/web.vwo/seed.spec.js

import { test, expect } from '@playwright/test';

test.describe('Security and Password Features', () => {
  test('Password Visibility Toggle', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Enter a password in the password field
    const passwordField = page.getByRole('textbox', { name: 'Password' });
    await expect(passwordField).toBeVisible();
    await passwordField.fill('TestPassword123');
    
    // Verify password is masked initially
    let inputType = await passwordField.getAttribute('type');
    expect(inputType).toBe('password');
    
    // Verify password visibility toggle button is visible
    const toggleButton = page.getByRole('button', { name: 'Toggle password visibility' });
    await expect(toggleButton).toBeVisible();
    
    // Click the password visibility toggle button to show password
    await toggleButton.click();
    
    // Verify password becomes visible in plain text
    inputType = await passwordField.getAttribute('type');
    expect(inputType).toBe('text');
    
    // Click the password visibility toggle button again to hide password
    await toggleButton.click();
    
    // Verify password is masked again
    inputType = await passwordField.getAttribute('type');
    expect(inputType).toBe('password');
  });
  
  test('HTTPS Protocol Verification', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify page loads with HTTPS protocol
    const pageUrl = page.url();
    expect(pageUrl).toContain('https://');
    expect(pageUrl).toContain('app.vwo.com');
  });
  
  test('Password Not Prefilled After Page Refresh', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Enter a password in the password field
    const passwordField = page.getByRole('textbox', { name: 'Password' });
    await expect(passwordField).toBeVisible();
    await passwordField.fill('TestPassword123');
    
    // Verify password is entered and masked
    await expect(passwordField).toHaveValue('TestPassword123');
    
    // Refresh the page
    await page.reload();
    
    // Verify password field is empty after refresh
    const refreshedPasswordField = page.getByRole('textbox', { name: 'Password' });
    await expect(refreshedPasswordField).toHaveValue('');
  });
  
  test('Email Not Prefilled After Page Refresh', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Enter an email address in the email field
    const emailField = page.getByRole('textbox', { name: 'Email address' });
    await expect(emailField).toBeVisible();
    await emailField.fill('test@vwo.com');
    
    // Verify email is entered
    await expect(emailField).toHaveValue('test@vwo.com');
    
    // Refresh the page
    await page.reload();
    
    // Verify email field is empty after refresh (form is cleared)
    const refreshedEmailField = page.getByRole('textbox', { name: 'Email address' });
    await expect(refreshedEmailField).toHaveValue('');
  });
});
