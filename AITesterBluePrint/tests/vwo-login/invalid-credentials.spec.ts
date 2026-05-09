// spec: Lecture_playwright_AI_Agents/web.vwo/preview_vwo_login.test-plan.md
// seed: Lecture_playwright_AI_Agents/web.vwo/seed.spec.js

import { test, expect } from '@playwright/test';

test.describe('Validation and Error Handling', () => {
  test('Invalid Email Format', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Enter an invalid email format
    const emailField = page.getByRole('textbox', { name: 'Email address' });
    await expect(emailField).toBeVisible();
    await emailField.fill('notanemail');
    
    // Enter a valid password
    const passwordField = page.getByRole('textbox', { name: 'Password' });
    await expect(passwordField).toBeVisible();
    await passwordField.fill('TestPassword123');
    
    // Click Sign in button
    const signInButton = page.getByRole('button', { name: 'Sign in', exact: true });
    await signInButton.click();
    
    // Verify email format validation is triggered or error message is shown
    await expect(page).toContainText(/email|password|did not match|error/i);
    
    // Verify user remains on the login page
    expect(page.url()).toContain('app.vwo.com');
  });
  
  test('Wrong Password', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Enter a valid email address for a registered account
    const emailField = page.getByRole('textbox', { name: 'Email address' });
    await expect(emailField).toBeVisible();
    await emailField.fill('test@vwo.com');
    
    // Enter an incorrect password
    const passwordField = page.getByRole('textbox', { name: 'Password' });
    await expect(passwordField).toBeVisible();
    await passwordField.fill('WrongPassword123');
    
    // Click Sign in button
    const signInButton = page.getByRole('button', { name: 'Sign in', exact: true });
    await signInButton.click();
    
    // Verify error message indicating invalid credentials
    await expect(page).toContainText(/password|email|did not match|invalid|error/i);
    
    // Verify user remains on the login page
    expect(page.url()).toContain('app.vwo.com');
  });
  
  test('Unregistered Email', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Enter an email that is not registered
    const emailField = page.getByRole('textbox', { name: 'Email address' });
    await expect(emailField).toBeVisible();
    await emailField.fill('unregistered@vwo.com');
    
    // Enter a password
    const passwordField = page.getByRole('textbox', { name: 'Password' });
    await expect(passwordField).toBeVisible();
    await passwordField.fill('TestPassword123');
    
    // Click Sign in button
    const signInButton = page.getByRole('button', { name: 'Sign in', exact: true });
    await signInButton.click();
    
    // Verify error message indicating invalid credentials or unregistered email
    await expect(page).toContainText(/email|password|did not match|invalid|error/i);
    
    // Verify user remains on the login page
    expect(page.url()).toContain('app.vwo.com');
  });
});
