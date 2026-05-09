// spec: Lecture_playwright_AI_Agents/web.vwo/preview_vwo_login.test-plan.md
// seed: Lecture_playwright_AI_Agents/web.vwo/seed.spec.js

import { test, expect } from '@playwright/test';

test.describe('Forgot Password and Recovery', () => {
  test('Navigate to Forgot Password', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Verify the Forgot Password button is visible
    const forgotButton = page.getByRole('button', { name: 'Forgot Password?' });
    await expect(forgotButton).toBeVisible();
    
    // Verify button is clickable
    await expect(forgotButton).toBeEnabled();
    
    // Click the Forgot Password button
    await forgotButton.click();
    
    // Verify user is redirected to password recovery page
    await page.waitForLoadState('networkidle');
    const currentUrl = page.url();
    expect(currentUrl).toBeTruthy();
    // The URL should change from /login
    expect(currentUrl).not.toContain('/#/login');
  });
  
  test('UI Elements - Button States and Links', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Verify all buttons and links are visible and enabled
    const forgotButton = page.getByRole('button', { name: 'Forgot Password?' });
    const googleButton = page.getByRole('button', { name: 'Sign in with Google' });
    const ssoButton = page.getByRole('button', { name: 'Sign in using SSO' });
    const passkeyButton = page.getByRole('button', { name: 'Sign in with Passkey' });
    const freeTrialLink = page.getByRole('link', { name: 'Start a FREE TRIAL' });
    
    await expect(forgotButton).toBeVisible();
    await expect(forgotButton).toBeEnabled();
    
    await expect(googleButton).toBeVisible();
    await expect(googleButton).toBeEnabled();
    
    await expect(ssoButton).toBeVisible();
    await expect(ssoButton).toBeEnabled();
    
    await expect(passkeyButton).toBeVisible();
    await expect(passkeyButton).toBeEnabled();
    
    await expect(freeTrialLink).toBeVisible();
  });
});
