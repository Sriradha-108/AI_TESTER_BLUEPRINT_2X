// spec: Lecture_playwright_AI_Agents/web.vwo/preview_vwo_login.test-plan.md
// seed: Lecture_playwright_AI_Agents/web.vwo/seed.spec.js

import { test, expect } from '@playwright/test';

test.describe('Alternative Login Methods', () => {
  test('Google Sign-in Button Visibility', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Verify the Sign in with Google button is visible
    const googleButton = page.getByRole('button', { name: 'Sign in with Google' });
    await expect(googleButton).toBeVisible();
    
    // Verify button text is clear
    const buttonText = await googleButton.innerText();
    expect(buttonText.toLowerCase()).toContain('google');
    
    // Verify button is enabled
    await expect(googleButton).toBeEnabled();
  });
  
  test('SSO Sign-in Button Visibility', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Verify the Sign in using SSO button is visible
    const ssoButton = page.getByRole('button', { name: 'Sign in using SSO' });
    await expect(ssoButton).toBeVisible();
    
    // Verify button text is clear
    const buttonText = await ssoButton.innerText();
    expect(buttonText.toLowerCase()).toContain('sso');
    
    // Verify button is enabled
    await expect(ssoButton).toBeEnabled();
  });
  
  test('Passkey Sign-in Button Visibility', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Verify the Sign in with Passkey button is visible
    const passkeyButton = page.getByRole('button', { name: 'Sign in with Passkey' });
    await expect(passkeyButton).toBeVisible();
    
    // Verify button text is clear
    const buttonText = await passkeyButton.innerText();
    expect(buttonText.toLowerCase()).toContain('passkey');
    
    // Verify button is enabled
    await expect(passkeyButton).toBeEnabled();
  });
});

test.describe('Sign Up and External Links', () => {
  test('Free Trial Link Navigation', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Verify the Start a FREE TRIAL link is visible
    const freeTrialLink = page.getByRole('link', { name: 'Start a FREE TRIAL' });
    await expect(freeTrialLink).toBeVisible();
    
    // Verify link has correct URL
    const linkUrl = await freeTrialLink.getAttribute('href');
    expect(linkUrl).toContain('vwo.com/free-trial');
  });
  
  test('Privacy Policy Link', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Verify the Privacy policy link is visible
    const privacyLink = page.getByRole('link', { name: 'Privacy policy' });
    await expect(privacyLink).toBeVisible();
    
    // Verify link has correct URL
    const linkUrl = await privacyLink.getAttribute('href');
    expect(linkUrl).toContain('vwo.com/privacy-policy');
  });
  
  test('Terms Link', async ({ page }) => {
    // Navigate to https://app.vwo.com
    await page.goto('https://app.vwo.com');
    
    // Verify login page is displayed
    expect(page.url()).toContain('app.vwo.com');
    
    // Verify the Terms link is visible
    const termsLink = page.getByRole('link', { name: 'Terms' });
    await expect(termsLink).toBeVisible();
    
    // Verify link has correct URL
    const linkUrl = await termsLink.getAttribute('href');
    expect(linkUrl).toContain('vwo.com/terms');
  });
});
