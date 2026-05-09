/**
 * ─────────────────────────────────────────────────────────────────────────────
 *  VWO Login – Production-Ready Playwright Test Suite
 *  Generated via: playwright-cli codegen → refined to POM + data-driven pattern
 * ─────────────────────────────────────────────────────────────────────────────
 *
 *  Test Plan:
 *    TC-01  Login page loads correctly (smoke)
 *    TC-02  Error shown for invalid email + invalid password       ← CORE CASE
 *    TC-03  Error message text matches expected string
 *    TC-04  Error shown for empty email field
 *    TC-05  Error shown for empty password field
 *    TC-06  Password field masks characters (type=password)
 *    TC-07  Forgot Password link is visible and navigates correctly
 *    TC-08  Sign in with Google button is visible
 *    TC-09  Data-driven: multiple invalid credential combinations
 * ─────────────────────────────────────────────────────────────────────────────
 */

import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { INVALID_CREDENTIALS, EXPECTED_ERRORS } from '../test-data/loginData';

// ── Shared setup ──────────────────────────────────────────────────────────────
test.beforeEach(async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.expectPageLoaded();
});

// ─────────────────────────────────────────────────────────────────────────────
// SUITE 1: Page Load / Smoke
// ─────────────────────────────────────────────────────────────────────────────
test.describe('VWO Login Page – Smoke Tests', () => {

  test('TC-01: Login page loads with all required elements', async ({ page }) => {
    const loginPage = new LoginPage(page);

    // URL should contain the login hash
    await expect(page).toHaveURL(/\/#\/login/);

    // All form elements must be present
    await expect(loginPage.emailInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.signInButton).toBeVisible();
    await expect(loginPage.forgotPasswordLink).toBeVisible();
    await expect(loginPage.rememberMeCheckbox).toBeVisible();
    await expect(loginPage.signInWithGoogleButton).toBeVisible();
  });

  test('TC-06: Password field masks entered characters', async ({ page }) => {
    const loginPage = new LoginPage(page);

    // The input type must be "password" so the browser masks characters
    await expect(loginPage.passwordInput).toHaveAttribute('type', 'password');
  });

  test('TC-08: "Sign in with Google" button is visible', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await expect(loginPage.signInWithGoogleButton).toBeVisible();
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// SUITE 2: Invalid Login – Core Negative Tests
// ─────────────────────────────────────────────────────────────────────────────
test.describe('VWO Login – Invalid Credentials Error Verification', () => {

  test('TC-02: Error notification appears for invalid email + invalid password', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const { email, password } = INVALID_CREDENTIALS.wrongEmailWrongPass;

    // 1. Enter invalid credentials
    await loginPage.fillEmail(email);
    await loginPage.fillPassword(password);

    // 2. Take screenshot before submitting (shows filled form)
    await page.screenshot({ path: 'test-results/screenshots/TC-02-before-submit.png' });

    // 3. Submit the form
    await loginPage.clickSignIn();

    // 4. Error notification must appear
    await loginPage.expectErrorVisible();

    // 5. Screenshot after submit (shows error state)
    await page.screenshot({ path: 'test-results/screenshots/TC-02-error-shown.png' });
  });

  test('TC-03: Error message text matches expected error string', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const { email, password } = INVALID_CREDENTIALS.wrongEmailWrongPass;

    await loginPage.login(email, password);

    // Verify the EXACT error message text
    await loginPage.expectErrorText(EXPECTED_ERRORS.invalidCredentials);

    // Also assert it is visible (double guard)
    await expect(loginPage.errorMessage).toBeVisible();
    await expect(loginPage.errorMessage).toContainText(
      'Your email, password, IP address or location did not match'
    );
  });

  test('TC-04: Error shown when email field is empty', async ({ page }) => {
    const loginPage = new LoginPage(page);

    // Leave email blank, fill in a password, then submit
    await loginPage.fillPassword('SomePassword123!');
    await loginPage.clickSignIn();

    // VWO may show its own error OR the browser prevents submission via HTML5 validation.
    // Either way the page must stay on the login URL.
    await expect(page).toHaveURL(/\/#\/login/, { timeout: 8_000 });

    // Check for either native browser validation or VWO error banner
    const isVwoError   = await loginPage.errorMessage.isVisible().catch(() => false);
    const isEmailInvalid = await loginPage.emailInput.evaluate(
      (el: HTMLInputElement) => el.validity.valueMissing || !el.validity.valid
    ).catch(() => false);

    expect(isVwoError || isEmailInvalid).toBe(true);
  });

  test('TC-05: Error shown when password field is empty', async ({ page }) => {
    const loginPage = new LoginPage(page);

    // Fill valid-format email, leave password blank, then submit
    await loginPage.fillEmail('someone@example.com');
    await loginPage.clickSignIn();

    // Page must stay on login
    await expect(page).toHaveURL(/\/#\/login/, { timeout: 8_000 });

    const isVwoError = await loginPage.errorMessage.isVisible().catch(() => false);
    const isPasswordInvalid = await loginPage.passwordInput.evaluate(
      (el: HTMLInputElement) => el.validity.valueMissing || !el.validity.valid
    ).catch(() => false);

    expect(isVwoError || isPasswordInvalid).toBe(true);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// SUITE 3: Data-Driven Invalid Login Scenarios
// ─────────────────────────────────────────────────────────────────────────────
test.describe('VWO Login – Data-Driven Negative Scenarios', () => {

  // Core scenario that triggers the VWO error banner
  const scenarios = [
    INVALID_CREDENTIALS.wrongEmailWrongPass,
    INVALID_CREDENTIALS.sqlInjection,
    INVALID_CREDENTIALS.xssAttempt,
  ];

  for (const scenario of scenarios) {
    test(`TC-09: Invalid login blocked — ${scenario.description}`, async ({ page }) => {
      const loginPage = new LoginPage(page);

      await loginPage.login(scenario.email, scenario.password);

      // Must NOT navigate away from login page
      await expect(page).toHaveURL(/\/#\/login/);

      // Wait up to 10s for VWO error banner OR check browser-level validation
      const hasError = await loginPage.errorMessage
        .waitFor({ state: 'visible', timeout: 10_000 })
        .then(() => true)
        .catch(() => false);

      const emailInvalid = await loginPage.emailInput.evaluate(
        (el: HTMLInputElement) => !el.validity.valid
      ).catch(() => false);

      expect(hasError || emailInvalid).toBe(true);
    });
  }
});

// ─────────────────────────────────────────────────────────────────────────────
// SUITE 4: Navigation Tests
// ─────────────────────────────────────────────────────────────────────────────
test.describe('VWO Login – Navigation', () => {

  test('TC-07: Forgot Password link navigates to password reset page', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.forgotPasswordLink.click();

    // Should navigate away from the login page
    await expect(page).not.toHaveURL(/\/#\/login/, { timeout: 10_000 });
  });
});
