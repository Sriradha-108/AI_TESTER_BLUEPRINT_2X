# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: vwo-login.spec.ts >> VWO Login – Invalid Credentials Error Verification >> TC-02: Error notification appears for invalid email + invalid password
- Location: tests\vwo-login.spec.ts:69:7

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
```

```
TimeoutError: page.goto: Timeout 30000ms exceeded.
Call log:
  - navigating to "https://app.vwo.com/#/login", waiting until "load"

```

# Test source

```ts
  1  | /**
  2  |  * Page Object Model: VWO Login Page
  3  |  * Encapsulates all selectors and actions for the VWO login page.
  4  |  */
  5  | import { type Page, type Locator, expect } from '@playwright/test';
  6  | 
  7  | export class LoginPage {
  8  |   readonly page: Page;
  9  | 
  10 |   // ── Locators ────────────────────────────────────────────────────────────────
  11 |   readonly emailInput: Locator;
  12 |   readonly passwordInput: Locator;
  13 |   readonly signInButton: Locator;
  14 |   readonly errorMessage: Locator;
  15 |   readonly forgotPasswordLink: Locator;
  16 |   readonly rememberMeCheckbox: Locator;
  17 |   readonly signInWithGoogleButton: Locator;
  18 |   readonly signInWithSSOButton: Locator;
  19 | 
  20 |   // ── Constants ────────────────────────────────────────────────────────────────
  21 |   static readonly URL = '/#/login';
  22 |   static readonly ERROR_TEXT =
  23 |     'Your email, password, IP address or location did not match';
  24 | 
  25 |   constructor(page: Page) {
  26 |     this.page = page;
  27 |     this.emailInput = page.locator('#login-username');
  28 |     this.passwordInput = page.locator('#login-password');
  29 |     this.signInButton = page.locator('#js-login-btn');
  30 |     this.errorMessage = page.locator('#js-notification-box-msg');
  31 |     this.forgotPasswordLink = page.locator('button.btn--link:has-text("Forgot Password?")');
  32 |     this.rememberMeCheckbox = page.locator('#checkbox-remember');
  33 |     this.signInWithGoogleButton = page.locator('#js-google-signin-btn');
  34 |     this.signInWithSSOButton = page.locator('button:has-text("Sign in using SSO")');
  35 |   }
  36 | 
  37 |   // ── Actions ──────────────────────────────────────────────────────────────────
  38 | 
  39 |   /** Navigate to the VWO login page */
  40 |   async goto(): Promise<void> {
> 41 |     await this.page.goto(LoginPage.URL);
     |                     ^ TimeoutError: page.goto: Timeout 30000ms exceeded.
  42 |     await this.page.waitForLoadState('domcontentloaded');
  43 |   }
  44 | 
  45 |   /** Fill in the email field */
  46 |   async fillEmail(email: string): Promise<void> {
  47 |     await this.emailInput.fill(email);
  48 |   }
  49 | 
  50 |   /** Fill in the password field */
  51 |   async fillPassword(password: string): Promise<void> {
  52 |     await this.passwordInput.fill(password);
  53 |   }
  54 | 
  55 |   /** Click the Sign In button */
  56 |   async clickSignIn(): Promise<void> {
  57 |     await this.signInButton.click();
  58 |   }
  59 | 
  60 |   /**
  61 |    * Perform a full login attempt with the given credentials.
  62 |    * @param email    - User email / username
  63 |    * @param password - User password
  64 |    */
  65 |   async login(email: string, password: string): Promise<void> {
  66 |     await this.fillEmail(email);
  67 |     await this.fillPassword(password);
  68 |     await this.clickSignIn();
  69 |   }
  70 | 
  71 |   // ── Assertions ───────────────────────────────────────────────────────────────
  72 | 
  73 |   /** Assert that the error notification is visible */
  74 |   async expectErrorVisible(): Promise<void> {
  75 |     await expect(this.errorMessage).toBeVisible({ timeout: 15_000 });
  76 |   }
  77 | 
  78 |   /** Assert the error notification contains the expected text */
  79 |   async expectErrorText(expectedText: string = LoginPage.ERROR_TEXT): Promise<void> {
  80 |     await expect(this.errorMessage).toContainText(expectedText, {
  81 |       timeout: 15_000,
  82 |     });
  83 |   }
  84 | 
  85 |   /** Assert that all critical login form elements are visible */
  86 |   async expectPageLoaded(): Promise<void> {
  87 |     await expect(this.emailInput).toBeVisible();
  88 |     await expect(this.passwordInput).toBeVisible();
  89 |     await expect(this.signInButton).toBeVisible();
  90 |   }
  91 | }
  92 | 
```