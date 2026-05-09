/**
 * Page Object Model: VWO Login Page
 * Encapsulates all selectors and actions for the VWO login page.
 */
import { type Page, type Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;

  // ── Locators ────────────────────────────────────────────────────────────────
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly signInButton: Locator;
  readonly errorMessage: Locator;
  readonly forgotPasswordLink: Locator;
  readonly rememberMeCheckbox: Locator;
  readonly signInWithGoogleButton: Locator;
  readonly signInWithSSOButton: Locator;

  // ── Constants ────────────────────────────────────────────────────────────────
  static readonly URL = '/#/login';
  static readonly ERROR_TEXT =
    'Your email, password, IP address or location did not match';

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.locator('#login-username');
    this.passwordInput = page.locator('#login-password');
    this.signInButton = page.locator('#js-login-btn');
    this.errorMessage = page.locator('#js-notification-box-msg');
    this.forgotPasswordLink = page.locator('button.btn--link:has-text("Forgot Password?")');
    this.rememberMeCheckbox = page.locator('#checkbox-remember');
    this.signInWithGoogleButton = page.locator('#js-google-signin-btn');
    this.signInWithSSOButton = page.locator('button:has-text("Sign in using SSO")');
  }

  // ── Actions ──────────────────────────────────────────────────────────────────

  /** Navigate to the VWO login page */
  async goto(): Promise<void> {
    await this.page.goto(LoginPage.URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
  }

  /** Fill in the email field */
  async fillEmail(email: string): Promise<void> {
    await this.emailInput.fill(email);
  }

  /** Fill in the password field */
  async fillPassword(password: string): Promise<void> {
    await this.passwordInput.fill(password);
  }

  /** Click the Sign In button */
  async clickSignIn(): Promise<void> {
    await this.signInButton.click();
  }

  /**
   * Perform a full login attempt with the given credentials.
   * @param email    - User email / username
   * @param password - User password
   */
  async login(email: string, password: string): Promise<void> {
    await this.fillEmail(email);
    await this.fillPassword(password);
    await this.clickSignIn();
  }

  // ── Assertions ───────────────────────────────────────────────────────────────

  /** Assert that the error notification is visible */
  async expectErrorVisible(): Promise<void> {
    await expect(this.errorMessage).toBeVisible({ timeout: 15_000 });
  }

  /** Assert the error notification contains the expected text */
  async expectErrorText(expectedText: string = LoginPage.ERROR_TEXT): Promise<void> {
    await expect(this.errorMessage).toContainText(expectedText, {
      timeout: 15_000,
    });
  }

  /** Assert that all critical login form elements are visible */
  async expectPageLoaded(): Promise<void> {
    await expect(this.emailInput).toBeVisible();
    await expect(this.passwordInput).toBeVisible();
    await expect(this.signInButton).toBeVisible();
  }
}
