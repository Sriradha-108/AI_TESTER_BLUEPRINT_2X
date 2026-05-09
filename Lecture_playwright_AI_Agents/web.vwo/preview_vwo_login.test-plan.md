# VWO Login Page Test Plan

## Application Overview

Comprehensive test plan for VWO login page (app.vwo.com). Covers happy path scenarios, validation, security, error handling, accessibility, and alternative login methods. The login page provides multiple authentication options including email/password, Google Sign-in, SSO, and Passkey methods, along with forgot password functionality and free trial signup.

## Test Scenarios

### 1. Happy Path - Email/Password Login

**Seed:** `Lecture_playwright_AI_Agents/web.vwo/seed.spec.js`

#### 1.1. Valid Login with Correct Credentials

**File:** `tests/vwo-login/valid-login.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Page loads at login URL (https://app.vwo.com/#/login)
    - expect: VWO logo is visible
    - expect: Login form is displayed
  2. Verify that the email input field is visible and focused
    - expect: Email textbox with placeholder 'Enter email ID' is visible
    - expect: Email field is the active/focused element
  3. Verify that the password input field is visible
    - expect: Password textbox with placeholder 'Enter password' is visible
    - expect: Password visibility toggle button is present
  4. Enter a valid test email address in the email field (e.g., test@vwo.com)
    - expect: Text is entered in the email field
  5. Enter a valid test password in the password field
    - expect: Password is masked with dots/asterisks
    - expect: Password visibility toggle button is clickable
  6. Click the 'Sign in' button
    - expect: Button submit action is triggered
    - expect: User is either logged in or appropriate response is shown

#### 1.2. Valid Login with Remember Me Checked

**File:** `tests/vwo-login/valid-login-remember-me.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Verify the 'Remember me' checkbox is visible and unchecked by default
    - expect: Remember me checkbox is visible
    - expect: Checkbox is unchecked initially
  3. Click the 'Remember me' checkbox to enable it
    - expect: Checkbox is now checked
    - expect: Visual indication of checked state is shown
  4. Enter valid email address
    - expect: Email is entered successfully
  5. Enter valid password
    - expect: Password is entered successfully
  6. Click the 'Sign in' button
    - expect: Login request is submitted
    - expect: Remember me preference is sent with login request

### 2. Validation and Error Handling

**Seed:** `Lecture_playwright_AI_Agents/web.vwo/seed.spec.js`

#### 2.1. Empty Email Field Validation

**File:** `tests/vwo-login/empty-email.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Leave the email field empty
    - expect: Email field remains empty
  3. Enter a valid password
    - expect: Password is entered successfully
  4. Click the 'Sign in' button
    - expect: Form validation is triggered
    - expect: Email field is highlighted as invalid or error message is shown
    - expect: Form submission is prevented

#### 2.2. Empty Password Field Validation

**File:** `tests/vwo-login/empty-password.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Enter a valid email address
    - expect: Email is entered successfully
  3. Leave the password field empty
    - expect: Password field remains empty
  4. Click the 'Sign in' button
    - expect: Form validation is triggered
    - expect: Password field is highlighted as invalid or error message is shown
    - expect: Form submission is prevented

#### 2.3. Both Email and Password Empty Validation

**File:** `tests/vwo-login/both-empty.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Leave both email and password fields empty
    - expect: Both fields are empty
  3. Click the 'Sign in' button
    - expect: Form validation is triggered
    - expect: Both fields show validation errors
    - expect: Form submission is prevented

#### 2.4. Invalid Email Format

**File:** `tests/vwo-login/invalid-email-format.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Enter an invalid email format (e.g., 'notanemail' or 'user@' or '@domain.com')
    - expect: Invalid email text is entered
  3. Enter a valid password
    - expect: Password is entered
  4. Click the 'Sign in' button
    - expect: Email format validation is triggered
    - expect: Error message indicates invalid email format
    - expect: Form submission is prevented

#### 2.5. Invalid Credentials - Wrong Password

**File:** `tests/vwo-login/wrong-password.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Enter a valid email address for a registered account
    - expect: Email is entered
  3. Enter an incorrect password
    - expect: Password is entered and masked
  4. Click the 'Sign in' button
    - expect: Login request is submitted
    - expect: Error message is displayed indicating invalid credentials or incorrect password
    - expect: User remains on the login page

#### 2.6. Invalid Credentials - Unregistered Email

**File:** `tests/vwo-login/unregistered-email.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Enter an email that is not registered with VWO
    - expect: Email is entered
  3. Enter a password
    - expect: Password is entered and masked
  4. Click the 'Sign in' button
    - expect: Login request is submitted
    - expect: Error message indicates the email is not registered or invalid credentials
    - expect: User remains on the login page

### 3. Security and Password Features

**Seed:** `Lecture_playwright_AI_Agents/web.vwo/seed.spec.js`

#### 3.1. Password Visibility Toggle

**File:** `tests/vwo-login/password-visibility-toggle.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Enter a password in the password field
    - expect: Password is masked with dots/asterisks
    - expect: Password visibility toggle button is visible
  3. Click the password visibility toggle button
    - expect: Password becomes visible in plain text
    - expect: Toggle button state changes to indicate 'hide' action
  4. Click the password visibility toggle button again
    - expect: Password is masked again
    - expect: Toggle button state changes back to indicate 'show' action

#### 3.2. HTTPS Protocol Verification

**File:** `tests/vwo-login/https-check.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Page loads with HTTPS protocol
  2. Verify the page URL
    - expect: URL starts with 'https://'
    - expect: Secure lock icon is visible in browser address bar

#### 3.3. Password Not Prefilled After Page Refresh

**File:** `tests/vwo-login/no-prefill-refresh.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Enter a password in the password field
    - expect: Password is entered and masked
  3. Refresh the page using F5 or browser refresh button
    - expect: Page reloads
    - expect: Password field is empty after refresh
    - expect: Form is cleared

#### 3.4. Email Not Prefilled After Page Refresh

**File:** `tests/vwo-login/no-prefill-email-refresh.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Enter an email address in the email field
    - expect: Email is entered
  3. Refresh the page using F5 or browser refresh button
    - expect: Page reloads
    - expect: Email field is empty after refresh (or only remains if cookies allow)
    - expect: Form is cleared

### 4. UI/UX and Accessibility

**Seed:** `Lecture_playwright_AI_Agents/web.vwo/seed.spec.js`

#### 4.1. Tab Navigation Through Form Fields

**File:** `tests/vwo-login/tab-navigation.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Press Tab key to navigate from email field to password field
    - expect: Focus moves from email field to password field
    - expect: Visual focus indicator is visible on password field
  3. Press Tab key again to navigate to password visibility toggle
    - expect: Focus moves to the password visibility toggle button
    - expect: Focus indicator is visible
  4. Press Tab key to navigate to 'Forgot Password?' button
    - expect: Focus moves to 'Forgot Password?' button
    - expect: Focus indicator is visible
  5. Press Tab key to navigate to 'Remember me' checkbox
    - expect: Focus moves to 'Remember me' checkbox
    - expect: Focus indicator is visible
  6. Press Tab key to navigate to 'Sign in' button
    - expect: Focus moves to 'Sign in' button
    - expect: Focus indicator is visible

#### 4.2. Keyboard Submit - Enter Key

**File:** `tests/vwo-login/keyboard-submit.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Enter a valid email address
    - expect: Email is entered
  3. Enter a valid password in the password field
    - expect: Password is entered and masked
  4. Press Enter key while focus is on password field
    - expect: Form submission is triggered
    - expect: Login request is sent

#### 4.3. UI Elements Visibility and Layout

**File:** `tests/vwo-login/ui-elements-visibility.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is fully loaded
  2. Verify all form elements are visible
    - expect: VWO logo is visible
    - expect: Email input field is visible
    - expect: Password input field is visible
    - expect: Toggle password visibility button is visible
    - expect: 'Forgot Password?' link is visible
    - expect: 'Remember me' checkbox is visible
    - expect: 'Sign in' button is visible
  3. Verify alternative login methods are visible
    - expect: 'Sign in with Google' button is visible
    - expect: 'Sign in using SSO' text/button is visible
    - expect: 'Sign in with Passkey' option is visible
  4. Verify footer/signup links are visible
    - expect: 'New to VWO?' text is visible
    - expect: 'Start a FREE TRIAL' link is visible
    - expect: Privacy Policy link is visible
    - expect: Terms link is visible

#### 4.4. Sign in Button State and Behavior

**File:** `tests/vwo-login/signin-button-state.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
    - expect: 'Sign in' button is visible and enabled
  2. Verify button is clickable
    - expect: Button is enabled (not disabled)
    - expect: Cursor changes to pointer on hover
  3. Click the 'Sign in' button with empty form
    - expect: Validation errors appear
    - expect: Button click is processed (button doesn't freeze)

### 5. Forgot Password and Recovery

**Seed:** `Lecture_playwright_AI_Agents/web.vwo/seed.spec.js`

#### 5.1. Navigate to Forgot Password

**File:** `tests/vwo-login/forgot-password-navigation.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Verify the 'Forgot Password?' link is visible
    - expect: 'Forgot Password?' button/link is visible
    - expect: Button is clickable
  3. Click the 'Forgot Password?' button
    - expect: User is redirected to password reset/recovery page
    - expect: Page URL changes to password recovery page

#### 5.2. Forgot Password - Back to Login

**File:** `tests/vwo-login/forgot-password-back.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Click the 'Forgot Password?' button
    - expect: Redirected to password recovery page
  3. Navigate back to login page (using back button or login link)
    - expect: User returns to login page
    - expect: URL is https://app.vwo.com/#/login

### 6. Alternative Login Methods

**Seed:** `Lecture_playwright_AI_Agents/web.vwo/seed.spec.js`

#### 6.1. Google Sign-in Button Visibility

**File:** `tests/vwo-login/google-signin-visibility.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Verify the 'Sign in with Google' button is visible
    - expect: 'Sign in with Google' button is visible
    - expect: Google icon is displayed
    - expect: Button text is clear
  3. Verify the button is clickable
    - expect: Button is enabled
    - expect: Cursor changes to pointer on hover

#### 6.2. SSO Sign-in Button Visibility

**File:** `tests/vwo-login/sso-signin-visibility.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Verify the 'Sign in using SSO' button is visible
    - expect: 'Sign in using SSO' button is visible
    - expect: Button text is clear
  3. Verify the button is clickable
    - expect: Button is enabled
    - expect: Cursor changes to pointer on hover

#### 6.3. Passkey Sign-in Button Visibility

**File:** `tests/vwo-login/passkey-signin-visibility.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Verify the 'Sign in with Passkey' button is visible
    - expect: 'Sign in with Passkey' button is visible
    - expect: Passkey icon is displayed
    - expect: Button text is clear
  3. Verify the button is clickable
    - expect: Button is enabled
    - expect: Cursor changes to pointer on hover

### 7. Sign Up and External Links

**Seed:** `Lecture_playwright_AI_Agents/web.vwo/seed.spec.js`

#### 7.1. Free Trial Link Navigation

**File:** `tests/vwo-login/free-trial-link.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Verify the 'Start a FREE TRIAL' link is visible
    - expect: 'Start a FREE TRIAL' link is visible
    - expect: Link text is underlined or styled
    - expect: Cursor changes to pointer on hover
  3. Click the 'Start a FREE TRIAL' link
    - expect: User is redirected to the free trial signup page or external URL
    - expect: Link URL contains trial-related parameters

#### 7.2. Privacy Policy Link

**File:** `tests/vwo-login/privacy-policy-link.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Verify the 'Privacy policy' link is visible
    - expect: 'Privacy policy' link is visible in footer
    - expect: Link text is styled as a hyperlink
  3. Click the 'Privacy policy' link
    - expect: User is redirected to privacy policy page
    - expect: Page opens in the same or new tab

#### 7.3. Terms Link

**File:** `tests/vwo-login/terms-link.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Verify the 'Terms' link is visible
    - expect: 'Terms' link is visible in footer
    - expect: Link text is styled as a hyperlink
  3. Click the 'Terms' link
    - expect: User is redirected to terms page
    - expect: Page opens in the same or new tab
