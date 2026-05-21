[KAN-3] Login fails with valid credentials on app.vwo.com Created: 27/Apr/26 Updated: 27/Apr/26
Status: To Do
Project: Radha
Components: None
Affects versions: None
Fix versions: None
Type: Bug Priority: Medium
Reporter: Pawan Kumar Assignee: Unassigned
Resolution: Unresolved Votes: 0
Labels: None
Remaining Estimate: Not Specified
Time Spent: Not Specified
Original estimate: Not Specified
Rank: 0|i0000f:
Description
*URL:* https://app.vwo.com
*Issue:* After entering valid credentials and clicking Submit, the user is not logged in. The login page reloads or shows a generic error, and no
navigation to the dashboard occurs.
*Steps to Reproduce:*
1. Open https://app.vwo.com in a browser.
2. Enter a valid email and password.
3. Click the Submit button.
4. Observe that login does not succeed; the page remains on the login screen.
*Expected Result:* User should be authenticated and redirected to the dashboard with a valid session token.
*Actual Result:* Login fails silently; either the page reloads with the login form or shows a generic error message.
*Environment:*
Browsers: Chrome, Firefox, Edge (latest versions)
OS: Windows 11, macOS Ventura
Device: Desktop/Laptop
Network: Corporate VPN and direct ISP tested
*Impact:* Critical – all users are unable to access the application.
*Suggested Priority:* High (P1).
*Possible Causes (initial hypotheses):*
Backend authentication service returning malformed/empty response.
Session token generation failure.
Front‑end error handling silently swallowing the error.
Cookie SameSite attribute issues.
Recent deployment/feature flag regression.
*Attachments:* (Include screenshots, network capture, console logs when filing the ticket.)
Generated at Thu May 21 06:35:58 UTC 2026 by Pawan Kumar using Jira 1001.0.0-SNAPSHOT#100291-
rev:e64422fc0bca366a72ebb118f1d9c35adcf7d14e.