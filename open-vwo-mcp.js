const { chromium } = require('playwright');

(async () => {
  console.log('🚀 Starting Playwright browser...');
  
  // Launch browser
  const browser = await chromium.launch({ 
    headless: false,  // Show the browser window
  });

  console.log('✅ Browser launched!');

  // Create a new page
  const page = await browser.newPage();
  console.log('📄 New page created');

  // Navigate to app.vwo.com
  console.log('🌐 Navigating to https://app.vwo.com...');
  try {
    await page.goto('https://app.vwo.com', { waitUntil: 'domcontentloaded', timeout: 30000 });
    console.log('✅ Successfully opened app.vwo.com');
    console.log(`📍 Current URL: ${page.url()}`);
    console.log(`📌 Page Title: ${await page.title()}`);
  } catch (error) {
    console.error('❌ Error navigating to page:', error.message);
  }

  // Keep browser open for 15 seconds
  console.log('⏳ Browser will stay open for 15 seconds...');
  await new Promise(resolve => setTimeout(resolve, 15000));

  // Close browser
  await browser.close();
  console.log('🔒 Browser closed');
})();
