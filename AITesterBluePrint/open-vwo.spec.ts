import { test } from '@playwright/test';

test('Open app.vwo.com', async ({ browser }) => {
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('Opening app.vwo.com...');
  await page.goto('https://app.vwo.com', { waitUntil: 'domcontentloaded' });

  console.log('Page title:', await page.title());
  console.log('Current URL:', page.url());
  
  // Keep the browser open for 10 seconds
  await page.waitForTimeout(10000);

  await context.close();
});
