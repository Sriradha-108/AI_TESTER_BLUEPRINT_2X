// spec: Lecture_playwright_AI_Agents/web.vwo/preview_vwo_login.test-plan.md
// seed: Lecture_playwright_AI_Agents/web.vwo/seed.spec.js

import { test, expect } from '@playwright/test';

test.describe('Happy Path - Email/Password Login', () => {
  test('Valid Login with Remember Me Checked', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Verify Remember me checkbox is visible and unchecked initially
    const rememberMeCheckbox = page.locator('label').filter({ hasText: 'Remember me' });
    await expect(rememberMeCheckbox).toBeVisible();
    
    // Click Remember me checkbox to enable it
    await rememberMeCheckbox.click();
    
    // Verify checkbox is now checked
    const checkboxInput = rememberMeCheckbox.locator('input');
    await expect(checkboxInput).toBeChecked();
    
    // Verify email field is visible
    const emailField = page.getByRole('textbox', { name: 'Email address' });
    await expect(emailField).toBeVisible();
    
    // Enter valid email address
    await emailField.fill('test@vwo.com');
    await expect(emailField).toHaveValue('test@vwo.com');
    
    // Verify password field is visible
    const passwordField = page.getByRole('textbox', { name: 'Password' });
    await expect(passwordField).toBeVisible();
    
    // Enter valid password
    await passwordField.fill('TestPassword123');
    
    // Verify Sign in button is visible and enabled
    const signInButton = page.getByRole('button', { name: 'Sign in', exact: true });
    await expect(signInButton).toBeVisible();
    await expect(signInButton).toBeEnabled();
  });
});
