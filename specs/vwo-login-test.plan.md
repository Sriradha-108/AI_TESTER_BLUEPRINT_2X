# VWO Login Page Test Plan

## Application Overview

VWO (Visual Website Optimizer) is a conversion optimization platform. The login page at app.vwo.com is the entry point for users to access their accounts. This test plan covers comprehensive testing of the login functionality including valid credentials, invalid inputs, error handling, security features, and UI interactions.

## Test Scenarios

### 1. Login Credentials - Happy Path

**Seed:** `seed.spec.ts`

#### 1.1. Valid login with correct email and password

**File:** `specs/vwo-login/valid-credentials.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
    - expect: Email input field is visible
    - expect: Password input field is visible
    - expect: Sign in button is visible
  2. Enter valid email address in the email field
    - expect: Email is entered correctly in the field
  3. Enter valid password in the password field
    - expect: Password field masks the input with bullets/dots
  4. Click the Sign In button
    - expect: Loading indicator appears
    - expect: User is redirected to the dashboard after successful authentication
    - expect: No error messages are displayed

#### 1.2. Remember me checkbox functionality

**File:** `specs/vwo-login/remember-me.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Check the 'Remember me' checkbox
    - expect: Checkbox is marked/checked
  3. Enter valid email and password
    - expect: Credentials are entered
  4. Click Sign In button
    - expect: User is logged in successfully
  5. Verify that email is pre-filled when returning to login page later
    - expect: Email address is automatically filled on returning to the login page
    - expect: Password field remains empty for security

### 2. Input Validation - Email Field

**Seed:** `seed.spec.ts`

#### 2.1. Empty email field validation

**File:** `specs/vwo-login/empty-email.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Leave email field empty and click Sign In button
    - expect: Error message appears: 'Email is required' or similar
    - expect: User remains on the login page

#### 2.2. Invalid email format validation

**File:** `specs/vwo-login/invalid-email-format.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Enter invalid email formats: 'test', 'test@', '@example.com', 'test@.com'
    - expect: Client-side validation error appears immediately
    - expect: Error message indicates invalid email format
  3. Click Sign In button with invalid email
    - expect: Form submission is prevented
    - expect: Error message is displayed: 'Please enter a valid email address'

#### 2.3. Email with whitespace handling

**File:** `specs/vwo-login/email-whitespace.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Enter email with leading/trailing spaces: '  user@example.com  '
    - expect: Email is entered
  3. Enter valid password and click Sign In
    - expect: Whitespace is automatically trimmed
    - expect: Login attempt succeeds if the trimmed email is valid

#### 2.4. Email case insensitivity

**File:** `specs/vwo-login/email-case-insensitive.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Enter email in uppercase: 'USER@EXAMPLE.COM'
    - expect: Email is entered
  3. Enter valid password and click Sign In
    - expect: Login succeeds (email comparison is case-insensitive)

### 3. Input Validation - Password Field

**Seed:** `seed.spec.ts`

#### 3.1. Empty password field validation

**File:** `specs/vwo-login/empty-password.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Enter valid email but leave password field empty
    - expect: Password field is empty
  3. Click Sign In button
    - expect: Error message appears: 'Password is required' or similar
    - expect: User remains on login page

#### 3.2. Password masking

**File:** `specs/vwo-login/password-masking.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Click on password field and type a password
    - expect: Password input is masked with dots or bullets
  3. Verify that password characters are not displayed in plain text
    - expect: Characters remain masked in the password field
    - expect: HTML input type is 'password'

#### 3.3. Show/Hide password toggle

**File:** `specs/vwo-login/show-hide-password.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Enter password in the password field
    - expect: Password is masked
  3. Click the eye icon or 'Show password' toggle button
    - expect: Password becomes visible in plain text
  4. Click the eye icon again to hide password
    - expect: Password is masked again

### 4. Authentication Errors

**Seed:** `seed.spec.ts`

#### 4.1. Incorrect password error

**File:** `specs/vwo-login/incorrect-password.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Enter valid email and incorrect password
    - expect: Credentials are entered
  3. Click Sign In button
    - expect: Error message appears: 'Invalid email or password'
    - expect: User remains on login page
    - expect: No sensitive information is leaked in error message

#### 4.2. Non-existent user email

**File:** `specs/vwo-login/nonexistent-user.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Enter email that doesn't exist: 'nonexistent@example.com'
    - expect: Email is entered
  3. Enter any password and click Sign In
    - expect: Error message appears: 'Invalid email or password'
    - expect: Error message should not indicate whether email exists

#### 4.3. Account lockout after multiple failed attempts

**File:** `specs/vwo-login/account-lockout.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Attempt login with valid email and incorrect password 5-10 times
    - expect: Each incorrect attempt shows error message
  3. After multiple failed attempts, try to login again
    - expect: Account is temporarily locked
    - expect: Message appears: 'Too many login attempts. Please try again later' or similar
    - expect: User cannot login until lock expires

#### 4.4. Session timeout during login

**File:** `specs/vwo-login/session-timeout.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Wait for longer than the session timeout period (typically 15-30 minutes) without action
    - expect: Session expires
  3. Attempt any action or try to submit the form
    - expect: User may need to refresh or re-enter credentials
    - expect: Error message indicates session expiration if applicable

### 5. UI and Navigation

**Seed:** `seed.spec.ts`

#### 5.1. Forgot password link functionality

**File:** `specs/vwo-login/forgot-password.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
    - expect: 'Forgot Password' link is visible
  2. Click on 'Forgot Password' link
    - expect: User is navigated to password recovery page
    - expect: URL changes appropriately
  3. Verify the password recovery page has email input field
    - expect: Email field is present
    - expect: Reset/Send button is visible

#### 5.2. Sign up link navigation

**File:** `specs/vwo-login/signup-link.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
    - expect: 'Sign Up' or 'Create Account' link is visible
  2. Click on 'Sign Up' link
    - expect: User is navigated to registration/signup page
    - expect: URL changes to signup page

#### 5.3. Form responsiveness - Mobile view

**File:** `specs/vwo-login/responsive-mobile.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com on a mobile device or resize to mobile viewport (375x667)
    - expect: Login form is responsive and visible
    - expect: No horizontal scroll is required
    - expect: All fields and buttons are accessible
  2. Verify input fields are properly sized for touch interaction
    - expect: Input fields have adequate height/padding for touch
    - expect: Buttons are easily clickable
  3. Test form submission on mobile
    - expect: Form can be submitted successfully on mobile

#### 5.4. Form responsiveness - Tablet view

**File:** `specs/vwo-login/responsive-tablet.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com on tablet or resize to tablet viewport (768x1024)
    - expect: Login form adapts to tablet size
    - expect: Form is centered and properly spaced
  2. Verify all form elements are visible and accessible
    - expect: No elements are cut off
    - expect: Layout is appropriate for tablet

#### 5.5. Tab navigation through form fields

**File:** `specs/vwo-login/tab-navigation.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page is displayed
  2. Press Tab key to navigate from email field to password field
    - expect: Focus moves to password field
    - expect: Visual focus indicator is visible
  3. Press Tab again to navigate to the Sign In button
    - expect: Focus moves to Sign In button
  4. Press Enter on the focused Sign In button
    - expect: Form is submitted

#### 5.6. Keyboard navigation - Enter key submission

**File:** `specs/vwo-login/enter-key-submit.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com and enter valid credentials
    - expect: Email and password are filled
  2. Press Enter key after entering both fields
    - expect: Form is submitted automatically
    - expect: User is logged in if credentials are valid

### 6. Security Features

**Seed:** `seed.spec.ts`

#### 6.1. HTTPS protocol enforcement

**File:** `specs/vwo-login/https-protocol.spec.ts`

**Steps:**
  1. Navigate to the login page
    - expect: URL uses HTTPS protocol (https://)
    - expect: No warning or security error is displayed
    - expect: Browser shows secure connection indicator

#### 6.2. No password pre-filling on page refresh

**File:** `specs/vwo-login/no-password-prefill.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com and enter credentials
    - expect: Email and password are entered
  2. Refresh the page without submitting
    - expect: Password field is empty after refresh
    - expect: Email might remain (depends on browser autocomplete)

#### 6.3. No sensitive data in URL

**File:** `specs/vwo-login/no-sensitive-url-data.spec.ts`

**Steps:**
  1. Enter email and password and submit the form
    - expect: URL does not contain email or password
    - expect: No GET parameters contain sensitive information

#### 6.4. CSRF token presence and validation

**File:** `specs/vwo-login/csrf-protection.spec.ts`

**Steps:**
  1. Inspect the login form HTML
    - expect: CSRF token or similar protection mechanism is present in form
  2. Verify CSRF token is sent with login request
    - expect: POST request includes CSRF token
    - expect: Token changes on each page load

### 7. Social Login / Third-party Integration

**Seed:** `seed.spec.ts`

#### 7.1. Google login button availability and functionality

**File:** `specs/vwo-login/google-login.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: 'Sign in with Google' button is visible or link is present
  2. Click on 'Sign in with Google' button
    - expect: Redirected to Google authentication page
    - expect: URL changes to Google login

#### 7.2. Microsoft/SSO login button functionality

**File:** `specs/vwo-login/microsoft-login.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: 'Sign in with Microsoft' or similar button is visible
  2. Click on the Microsoft/SSO login button
    - expect: Redirected to Microsoft authentication or SSO page

### 8. Two-Factor Authentication (2FA)

**Seed:** `seed.spec.ts`

#### 8.1. 2FA prompt after valid credentials

**File:** `specs/vwo-login/2fa-prompt.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com and enter valid credentials for account with 2FA enabled
    - expect: Email and password are entered
  2. Click Sign In button
    - expect: User is taken to 2FA verification page
    - expect: Message appears: 'Enter verification code from your authenticator app' or similar
  3. Enter valid 2FA code
    - expect: 2FA code input accepts 6-digit or appropriate code
    - expect: User is logged in after verification

#### 8.2. 2FA backup codes

**File:** `specs/vwo-login/2fa-backup-codes.spec.ts`

**Steps:**
  1. Navigate to 2FA verification page after entering valid credentials
    - expect: 2FA verification page is displayed
  2. Look for 'Use backup code' or similar option
    - expect: Option to use backup code is available
  3. Click on backup code option and enter valid backup code
    - expect: User is logged in using backup code

### 9. Branding and Visual Elements

**Seed:** `seed.spec.ts`

#### 9.1. VWO logo and branding presence

**File:** `specs/vwo-login/logo-branding.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com/login
    - expect: VWO logo is visible at the top of the page
    - expect: Logo links back to VWO homepage
  2. Click on the logo
    - expect: Logo is clickable
    - expect: Navigates to VWO homepage or main site

#### 9.2. Page title and metadata

**File:** `specs/vwo-login/page-metadata.spec.ts`

**Steps:**
  1. Check the browser tab/page title
    - expect: Title contains 'Login' or 'Sign In' and VWO branding
  2. Inspect page meta tags
    - expect: Meta description is present and descriptive

#### 9.3. Theme consistency - Dark/Light mode

**File:** `specs/vwo-login/theme-consistency.spec.ts`

**Steps:**
  1. Navigate to https://app.vwo.com
    - expect: Login page theme is consistent with VWO branding
  2. Check if dark mode toggle is available
    - expect: If available, dark mode toggle works correctly
    - expect: Theme preference is respected

### 10. Error Handling and Edge Cases

**Seed:** `seed.spec.ts`

#### 10.1. Network error during login attempt

**File:** `specs/vwo-login/network-error.spec.ts`

**Steps:**
  1. Open browser DevTools and throttle network to Offline
    - expect: Network is throttled to offline
  2. Enter valid credentials and attempt login
    - expect: Error message appears: 'Connection error' or 'Unable to connect'
    - expect: User can retry after restoring connection

#### 10.2. Server error response during login

**File:** `specs/vwo-login/server-error.spec.ts`

**Steps:**
  1. Mock server to return 500 error on login attempt
    - expect: Server error is handled gracefully
  2. Attempt login with valid credentials
    - expect: Error message appears: 'Server error. Please try again later'
    - expect: User remains on login page and can retry

#### 10.3. Very long email address input

**File:** `specs/vwo-login/long-email.spec.ts`

**Steps:**
  1. Enter extremely long email address (255+ characters)
    - expect: Input is handled without breaking the form
  2. Attempt submission
    - expect: Either accepted (if valid) or error message appears

#### 10.4. Special characters in email field

**File:** `specs/vwo-login/special-characters-email.spec.ts`

**Steps:**
  1. Enter email with valid special characters: user+tag@example.com
    - expect: Email is accepted
  2. Enter invalid special characters: user<>@example.com
    - expect: Error message indicates invalid format

#### 10.5. SQL injection attempt in login fields

**File:** `specs/vwo-login/sql-injection.spec.ts`

**Steps:**
  1. Enter SQL injection payload in email: admin' OR '1'='1
    - expect: Input is properly escaped or rejected
    - expect: No database error is exposed
  2. Attempt login
    - expect: Attack is prevented
    - expect: Standard login error appears

### 11. Accessibility

**Seed:** `seed.spec.ts`

#### 11.1. Form labels and accessibility attributes

**File:** `specs/vwo-login/form-labels.spec.ts`

**Steps:**
  1. Inspect the login form HTML
    - expect: Email field has associated label element
    - expect: Password field has associated label element
    - expect: Form elements have proper id and for attributes
  2. Use screen reader to verify form structure
    - expect: Screen reader announces field labels correctly

#### 11.2. Color contrast for readability

**File:** `specs/vwo-login/color-contrast.spec.ts`

**Steps:**
  1. Use accessibility checker tool (Axe, WAVE, etc.)
    - expect: Text and input fields meet WCAG AA contrast ratio (4.5:1 for text)

#### 11.3. Keyboard accessibility

**File:** `specs/vwo-login/keyboard-accessibility.spec.ts`

**Steps:**
  1. Navigate login page using only keyboard (no mouse)
    - expect: All form elements are reachable via Tab key
    - expect: Focus is visible on each element
  2. Complete login using only keyboard
    - expect: Form can be submitted entirely with keyboard
    - expect: No keyboard traps exist
