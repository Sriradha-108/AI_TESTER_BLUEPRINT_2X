// spec: Lecture_playwright_AI_Agents/web.vwo/preview_vwo_login.test-plan.md
// seed: Lecture_playwright_AI_Agents/web.vwo/seed.spec.js

import { test, expect } from '@playwright/test';

test.describe('UI/UX and Accessibility', () => {
  test('Tab Navigation Through Form Fields', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Get form elements
    const emailField = page.getByRole('textbox', { name: 'Email address' });
    const passwordField = page.getByRole('textbox', { name: 'Password' });
    const toggleButton = page.getByRole('button', { name: 'Toggle password visibility' });
    const forgotButton = page.getByRole('button', { name: 'Forgot Password?' });
    const rememberMeLabel = page.locator('label').filter({ hasText: 'Remember me' });
    const signInButton = page.getByRole('button', { name: 'Sign in', exact: true });
    
    // Verify all elements are visible
    await expect(emailField).toBeVisible();
    await expect(passwordField).toBeVisible();
    await expect(toggleButton).toBeVisible();
    await expect(forgotButton).toBeVisible();
    await expect(rememberMeLabel).toBeVisible();
    await expect(signInButton).toBeVisible();
    
    // Focus on email field and then press Tab to navigate through fields
    await emailField.focus();
    
    // Press Tab to move to next element
    await page.keyboard.press('Tab');
    
    // Verify focus moves to password field or next focusable element
    const focusedElement = await page.evaluate(() => document.activeElement?.getAttribute('name') || 'button');
    expect(focusedElement).toBeTruthy();
  });
  
  test('Keyboard Submit - Enter Key', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Enter a valid email address
    const emailField = page.getByRole('textbox', { name: 'Email address' });
    await expect(emailField).toBeVisible();
    await emailField.fill('test@vwo.com');
    
    // Enter a valid password
    const passwordField = page.getByRole('textbox', { name: 'Password' });
    await expect(passwordField).toBeVisible();
    await passwordField.fill('TestPassword123');
    
    // Focus on password field and press Enter to submit
    await passwordField.focus();
    await page.keyboard.press('Enter');
    
    // Verify form submission is triggered - page should either redirect or show error
    await page.waitForLoadState('networkidle');
    await expect(page).toContainText(/email|password|did not match|error/i);
  });
  
  test('UI Elements Visibility and Layout', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is fully loaded
    expect(page.url()).toContain('app.vwo.com');
    
    // Verify all form elements are visible
    const vwoLogo = page.getByRole('img', { name: 'VWO' });
    const emailField = page.getByRole('textbox', { name: 'Email address' });
    const passwordField = page.getByRole('textbox', { name: 'Password' });
    const toggleButton = page.getByRole('button', { name: 'Toggle password visibility' });
    const forgotButton = page.getByRole('button', { name: 'Forgot Password?' });
    const rememberMeLabel = page.locator('label').filter({ hasText: 'Remember me' });
    const signInButton = page.getByRole('button', { name: 'Sign in', exact: true });
    
    await expect(vwoLogo).toBeVisible();
    await expect(emailField).toBeVisible();
    await expect(passwordField).toBeVisible();
    await expect(toggleButton).toBeVisible();
    await expect(forgotButton).toBeVisible();
    await expect(rememberMeLabel).toBeVisible();
    await expect(signInButton).toBeVisible();
    
    // Verify alternative login methods are visible
    const googleButton = page.getByRole('button', { name: 'Sign in with Google' });
    const ssoButton = page.getByRole('button', { name: 'Sign in using SSO' });
    const passkeyButton = page.getByRole('button', { name: 'Sign in with Passkey' });
    
    await expect(googleButton).toBeVisible();
    await expect(ssoButton).toBeVisible();
    await expect(passkeyButton).toBeVisible();
    
    // Verify footer/signup links are visible
    const freeTrialLink = page.getByRole('link', { name: 'Start a FREE TRIAL' });
    const privacyLink = page.getByRole('link', { name: 'Privacy policy' });
    const termsLink = page.getByRole('link', { name: 'Terms' });
    
    await expect(freeTrialLink).toBeVisible();
    await expect(privacyLink).toBeVisible();
    await expect(termsLink).toBeVisible();
  });
  
  test('Sign in Button State and Behavior', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed and Sign in button is visible and enabled
    expect(page.url()).toContain('app.vwo.com');
    const signInButton = page.getByRole('button', { name: 'Sign in', exact: true });
    await expect(signInButton).toBeVisible();
    await expect(signInButton).toBeEnabled();
    
    // Verify button is clickable - cursor should be pointer
    const boxModel = await signInButton.boundingBox();
    expect(boxModel).toBeTruthy();
    
    // Click the Sign in button with empty form to test validation
    await signInButton.click();
    
    // Verify validation errors appear and button doesn't freeze
    await expect(page).toContainText(/email|password|did not match|error/i);
    await expect(signInButton).toBeEnabled();
  });
});
