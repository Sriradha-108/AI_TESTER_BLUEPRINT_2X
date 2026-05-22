# Chapter 10: MCP Basics - Model Context Protocol

## Overview

This chapter explores the **Model Context Protocol (MCP)**, a standardized way for AI models to interact with tools and services. MCP enables AI assistants to have safe, controlled access to external systems and data sources.

## What is Model Context Protocol (MCP)?

The Model Context Protocol is an open standard that allows:
- AI models to interact with external tools and services
- Safe and controlled access to resources
- Standardized communication between AI and applications
- Easy integration of new capabilities

## Key Concepts

### MCP Server
- Exposes resources, tools, and prompts to AI clients
- Runs as a background service
- Can be local or remote
- Examples: Playwright MCP, filesystem MCP, database MCP

### MCP Client
- AI assistant or application that uses MCP services
- Sends requests to MCP servers
- Receives responses and data
- Can chain multiple tools and servers

### Resources
- Data or information exposed by an MCP server
- Can be files, databases, APIs, etc.
- Read-only or read-write depending on permissions

### Tools
- Functions that MCP servers can execute
- Called by AI clients to perform actions
- Return results to the caller

### Prompts
- Pre-configured prompts for specific use cases
- Reusable templates for AI interactions
- Can include system prompts and examples

## Playwright MCP

### What is Playwright MCP?
Playwright MCP is an MCP server that enables AI models to control web browsers through the Playwright API.

### Installation

```bash
npm install -g mcp-playwright
# or
npm install mcp-playwright
```

### Starting the Server

```bash
npx mcp-playwright
```

### Capabilities

The Playwright MCP server provides:
- **Browser Control**: Launch and manage browser instances
- **Tab Management**: Create, switch, and close browser tabs
- **Page Navigation**: Navigate to URLs and interact with pages
- **DOM Manipulation**: Query and interact with page elements
- **Screenshots & PDFs**: Capture page content
- **File Operations**: Handle downloads and uploads

## Use Cases

### 1. Automated Testing
```javascript
// AI can generate and execute test cases
- Navigate to application
- Fill forms
- Click buttons
- Verify page content
- Generate test reports
```

### 2. Web Scraping
```javascript
// AI can intelligently extract data from websites
- Navigate to pages
- Extract structured data
- Handle pagination
- Save data to files
```

### 3. User Interaction Automation
```javascript
// AI can automate routine browser tasks
- Fill out forms
- Submit applications
- Monitor pages
- Trigger workflows
```

### 4. QA and Testing
```javascript
// Integrate with QA Copilot for AI-powered QA
- Generate test scenarios
- Execute tests with Playwright
- Generate test reports
- Flag issues and bugs
```

## Example Usage

### Basic Browser Automation
```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('https://app.vwo.com');
  
  // Interact with page
  await page.click('button#login');
  
  // Take screenshot
  await page.screenshot({ path: 'screenshot.png' });
  
  await browser.close();
})();
```

### With MCP Server
```bash
# Start MCP server
npx mcp-playwright

# Use from Claude or other MCP clients
# AI can control browser through MCP protocol
```

## Configuration

### Command Line Options

```bash
npx mcp-playwright [options]

Options:
  --browser <browser>          # chrome, firefox, webkit, msedge
  --allowed-origins <origins>  # Semicolon-separated list
  --blocked-origins <origins>  # Semicolon-separated list
  --block-service-workers      # Block service workers
  --cdp-endpoint <endpoint>    # Chrome DevTools Protocol endpoint
  --caps <caps>                # Comma-separated capabilities
```

### Capabilities
- `tabs`: Tab management
- `pdf`: PDF generation
- `history`: Browser history access
- `wait`: Wait for conditions
- `files`: File operations
- `install`: Plugin installation

## Integration with AI Models

### Claude Integration
```json
{
  "tools": [
    {
      "name": "playwright-mcp",
      "version": "0.0.1",
      "command": "npx mcp-playwright"
    }
  ]
}
```

### Custom MCP Client
```javascript
const client = new MCPClient({
  servers: [
    {
      command: 'npx mcp-playwright',
      options: { headless: false }
    }
  ]
});
```

## Best Practices

### 1. Resource Management
- Always close browsers properly
- Clean up resources
- Use context managers

### 2. Timeout Handling
- Set appropriate timeouts
- Handle timeout errors gracefully
- Retry failed operations

### 3. Error Handling
- Catch navigation errors
- Handle network issues
- Log errors for debugging

### 4. Performance
- Reuse browser instances
- Use headless mode when possible
- Minimize screenshot operations

### 5. Security
- Restrict origins when needed
- Validate URLs
- Block dangerous scripts
- Use sandboxing

## Troubleshooting

### Browser Won't Launch
```bash
# Install browsers
npx playwright install chromium

# Check system dependencies
npx playwright install-deps
```

### Connection Errors
```bash
# Verify MCP server is running
ps aux | grep mcp-playwright

# Check port availability
netstat -tulpn | grep 3000
```

### Timeout Issues
- Increase timeout values
- Check network connectivity
- Verify URL accessibility

## Files in This Chapter

```
chapter_10_MCP_Basics/
├── README.md              # This file
├── Playwright_MCP/        # Playwright MCP examples
│   ├── basic-example.js
│   ├── advanced-example.js
│   └── integration-example.js
├── examples/
│   ├── web-scraping.js
│   ├── form-automation.js
│   └── screenshot-capture.js
└── docs/
    ├── mcp-protocol.md
    ├── playwright-api.md
    └── troubleshooting.md
```

## Resources

### Official Documentation
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Playwright Documentation](https://playwright.dev/)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol/)

### Related Chapters
- Chapter 9: QA Copilot - Using MCP for QA automation
- Chapter 4: AI Agents - Building intelligent agents
- Chapter 8: RAG - Retrieval Augmented Generation

## Next Steps

1. **Explore MCP Servers**: Discover other MCP server implementations
2. **Build Custom MCPs**: Create your own MCP servers
3. **Integrate with AI**: Connect MCPs to Claude or other models
4. **Advanced Automation**: Combine multiple MCPs for complex workflows

## Contributing

To contribute improvements to this chapter:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This chapter is part of AI Tester Blueprint 2.0 and is licensed under MIT.

---

**Last Updated**: May 22, 2026
**Maintained By**: AI Tester Blueprint Community
