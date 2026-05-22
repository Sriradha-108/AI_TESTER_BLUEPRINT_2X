# Adding the Playwright MCP Server to Visual Studio Code

These notes walk through adding the official **Playwright MCP** server (`@playwright/mcp`) to VS Code so it can be used by Copilot Chat in Agent mode (or any other MCP-aware client inside VS Code).

---

## 1. Prerequisites

Make sure these are installed and on your `PATH`:

- **VS Code** `1.99` or newer (MCP support lives under Copilot Chat → Agent mode).
- **Node.js** `18+` (the MCP server runs via `npx`).
- **GitHub Copilot** + **GitHub Copilot Chat** extensions, signed in.
- Recommended: run once to pre-install browsers:
  ```bash
  npx playwright install
  ```

Verify versions:

```bash
code --version
node --version
npx --version
```

---

## 2. Enable MCP in VS Code

1. Open **Settings** (`Ctrl+,`).
2. Search for `chat.mcp.enabled` and make sure it is **checked**.
3. Open Copilot Chat (`Ctrl+Alt+I`) and switch the mode dropdown to **Agent**. MCP tools are only surfaced in Agent mode.

---

## 3. Add the Server (easy path — Command Palette)

1. Press `Ctrl+Shift+P` and run **MCP: Add Server**.
2. Pick **Command (stdio)**.
3. Enter the command:
   ```
   npx @playwright/mcp@latest
   ```
4. Give it a name, for example `playwright`.
5. Choose where to save it:
   - **Workspace** → writes to `.vscode/mcp.json` (share with the team via git).
   - **User** → writes to your global VS Code profile (only you).
6. VS Code will start the server. Open the **MCP Servers** view (Command Palette → **MCP: List Servers**) to confirm it shows as **Running**.

---

## 4. Add the Server (manual path — `mcp.json`)

If you prefer to edit the config directly, create `.vscode/mcp.json` at the workspace root:

```json
{
  "servers": {
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

On Windows, if `npx` is not resolving, use the `.cmd` shim:

```json
{
  "servers": {
    "playwright": {
      "type": "stdio",
      "command": "npx.cmd",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

Save the file. A small **Start** codelens appears above the server entry — click it (or run **MCP: Start Server**).

### Common flags

Add them inside `args` to tweak behavior:

| Flag | Purpose |
|---|---|
| `--headless` | Run the browser without a UI window. |
| `--browser=chromium` | Pick a browser: `chromium`, `firefox`, `webkit`, `msedge`. |
| `--viewport-size=1280,720` | Fix the viewport. |
| `--isolated` | Use a fresh, in-memory profile each session. |
| `--user-data-dir=<path>` | Reuse a persistent profile (handy for logged-in flows). |
| `--save-trace` | Emit a Playwright trace per session. |

Example with options:

```json
{
  "servers": {
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--browser=chromium",
        "--headless",
        "--viewport-size=1280,720"
      ]
    }
  }
}
```

---

## 5. Use It from Copilot Chat

1. Open Copilot Chat and switch to **Agent** mode.
2. Click the **Tools** icon — you should see the `playwright` server with tools like `browser_navigate`, `browser_click`, `browser_snapshot`, etc.
3. Try a prompt:
   > Open https://playwright.dev, take an accessibility snapshot, then click the "Get started" link.

VS Code will ask for permission the first time each tool is invoked. Approve once or "Always allow" per workspace.

---

## 6. Troubleshooting

- **Server keeps restarting** → open **Output** panel → channel **MCP** for stderr.
- **`npx` not found** on Windows → use `npx.cmd` (see above) or pass the full path to Node.
- **Browser launch fails** → run `npx playwright install` once to download browser binaries.
- **Tools missing in Chat** → confirm you are in **Agent** mode and `chat.mcp.enabled` is on.
- **Behind a corporate proxy** → set `HTTP_PROXY` / `HTTPS_PROXY` in the `env` block:
  ```json
  "env": {
    "HTTPS_PROXY": "http://proxy.company.local:8080"
  }
  ```

---

## 7. References

- Playwright MCP repo: <https://github.com/microsoft/playwright-mcp>
- VS Code MCP docs: <https://code.visualstudio.com/docs/copilot/chat/mcp-servers>
