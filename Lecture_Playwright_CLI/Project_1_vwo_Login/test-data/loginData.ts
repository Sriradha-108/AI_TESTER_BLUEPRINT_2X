/**
 * Test Data: VWO Login Scenarios
 * Centralised data store — swap credentials without touching test logic.
 */

export const VALID_CREDENTIALS = {
  email: process.env.VWO_EMAIL ?? 'your-real-email@example.com',
  password: process.env.VWO_PASSWORD ?? 'your-real-password',
};

export const INVALID_CREDENTIALS = {
  wrongEmailWrongPass: {
    email: 'invalid_user@notadomain.xyz',
    password: 'WrongP@ssw0rd!99',
    description: 'invalid email + invalid password',
  },
  emptyEmail: {
    email: '',
    password: 'SomePassword123!',
    description: 'empty email + valid-format password',
  },
  emptyPassword: {
    email: 'someone@example.com',
    password: '',
    description: 'valid-format email + empty password',
  },
  sqlInjection: {
    email: "' OR '1'='1",
    password: "' OR '1'='1",
    description: 'SQL injection attempt in both fields',
  },
  xssAttempt: {
    email: '<script>alert(1)</script>@test.com',
    password: '<script>alert(1)</script>',
    description: 'XSS payload in both fields',
  },
};

export const EXPECTED_ERRORS = {
  invalidCredentials:
    'Your email, password, IP address or location did not match',
};
