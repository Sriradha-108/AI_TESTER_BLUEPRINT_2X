# Project 1 – VWO Login Test Suite

> Playwright-CLI recorded → refined into a production-ready POM test suite.

## 📁 Project Structure

```
Project_1_vwo_Login/
├── pages/
│   └── LoginPage.ts          # Page Object Model for VWO login page
├── test-data/
│   └── loginData.ts          # Centralised credentials & expected errors
├── tests/
│   └── vwo-login.spec.ts     # 9 test cases (smoke + negative + data-driven)
├── test-results/
│   └── screenshots/          # Auto-captured on failure
├── playwright-report/        # HTML report (after test run)
├── playwright.config.ts      # Playwright configuration
├── tsconfig.json             # TypeScript config
├── .env.example              # Credentials template
└── package.json
```

## 🧪 Test Cases

| ID     | Suite            | Description                                          |
|--------|------------------|------------------------------------------------------|
| TC-01  | Smoke            | Login page loads with all required elements          |
| TC-02  | Negative         | Error notification for invalid email + password      |
| TC-03  | Negative         | Error message text matches expected string           |
| TC-04  | Negative         | Error shown for empty email field                    |
| TC-05  | Negative         | Error shown for empty password field                 |
| TC-06  | Smoke            | Password field masks entered characters              |
| TC-07  | Navigation       | Forgot Password link navigates correctly             |
| TC-08  | Smoke            | Sign in with Google button is visible                |
| TC-09  | Data-Driven      | Multiple invalid credential combinations blocked     |

## 🚀 Quick Start

### 1. Install dependencies
```bash
npm install
```

### 2. Install Playwright browsers
```bash
npx playwright install --with-deps chromium
```

### 3. Run all tests (headed)
```bash
npm run test:headed
```

### 4. Run all tests (headless / CI)
```bash
npm test
```

### 5. Open HTML report
```bash
npm run test:report
```

### 6. Debug a single test
```bash
npm run test:debug
```

## ⚙️ Configuration

- **Base URL**: `https://app.vwo.com`
- **Browsers**: Chromium, Firefox
- **Retries**: 0 locally / 1 on CI
- **Screenshots**: On failure only
- **Video**: Retained on failure

## 🔐 Credentials

For negative tests, fake credentials are used from `test-data/loginData.ts`.  
For valid login tests, copy `.env.example` → `.env` and fill in real credentials.

## 🛠️ How It Was Built

1. **Recorded** with `playwright-cli codegen https://app.vwo.com/#/login`
2. **Inspected** live DOM to confirm element IDs (`#login-username`, `#login-password`, `#js-login-btn`, `#js-notification-box-msg`)
3. **Refactored** raw recording into:
   - `LoginPage.ts` — Page Object Model
   - `loginData.ts` — Centralised test data
   - `vwo-login.spec.ts` — Structured spec with `describe` suites
