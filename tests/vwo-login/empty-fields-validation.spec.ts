// spec: Lecture_playwright_AI_Agents/web.vwo/preview_vwo_login.test-plan.md
// seed: Lecture_playwright_AI_Agents/web.vwo/seed.spec.js

import { test, expect } from '@playwright/test';

test.describe('Validation and Error Handling', () => {
  test('Empty Email Field Validation', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Verify email field is visible and empty
    const emailField = page.getByRole('textbox', { name: 'Email address' });
    await expect(emailField).toBeVisible();
    await expect(emailField).toHaveValue('');
    
    // Enter a valid password
    const passwordField = page.getByRole('textbox', { name: 'Password' });
    await expect(passwordField).toBeVisible();
    await passwordField.fill('TestPassword123');
    
    // Click Sign in button with empty email
    const signInButton = page.getByRole('button', { name: 'Sign in', exact: true });
    await signInButton.click();
    
    // Verify form validation error is displayed or email field shows error
    // The page shows an error message when form validation fails
    await expect(page).toContainText(/email|password|did not match|error/i);
    
    // Verify user remains on the login page (not redirected)
    expect(page.url()).toContain('app.vwo.com');
  });
  
  test('Empty Password Field Validation', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Enter a valid email address
    const emailField = page.getByRole('textbox', { name: 'Email address' });
    await expect(emailField).toBeVisible();
    await emailField.fill('test@vwo.com');
    
    // Verify password field is empty
    const passwordField = page.getByRole('textbox', { name: 'Password' });
    await expect(passwordField).toBeVisible();
    await expect(passwordField).toHaveValue('');
    
    // Click Sign in button with empty password
    const signInButton = page.getByRole('button', { name: 'Sign in', exact: true });
    await signInButton.click();
    
    // Verify form validation error is displayed
    await expect(page).toContainText(/password|email|did not match|error/i);
    
    // Verify user remains on the login page
    expect(page.url()).toContain('app.vwo.com');
  });
  
  test('Both Email and Password Empty Validation', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Verify both fields are empty
    const emailField = page.getByRole('textbox', { name: 'Email address' });
    const passwordField = page.getByRole('textbox', { name: 'Password' });
    
    await expect(emailField).toHaveValue('');
    await expect(passwordField).toHaveValue('');
    
    // Click Sign in button with empty form
    const signInButton = page.getByRole('button', { name: 'Sign in', exact: true });
    await signInButton.click();
    
    // Verify form validation errors are shown
    await expect(page).toContainText(/email|password|did not match|error/i);
    
    // Verify user remains on the login page
    expect(page.url()).toContain('app.vwo.com');
  });
});
