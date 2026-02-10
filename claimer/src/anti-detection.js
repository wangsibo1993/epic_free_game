/**
 * Anti-detection utilities to make automation more human-like
 */

/**
 * Generate a random delay between min and max milliseconds
 * @param {number} min - Minimum delay in milliseconds
 * @param {number} max - Maximum delay in milliseconds
 * @returns {number} Random delay in milliseconds
 */
export function randomDelay(min = 1000, max = 3000) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Sleep for a random amount of time
 * @param {number} min - Minimum delay in milliseconds (default: 1000ms)
 * @param {number} max - Maximum delay in milliseconds (default: 3000ms)
 */
export async function randomSleep(min = 1000, max = 3000) {
  const delay = randomDelay(min, max);
  console.log(`  ⏱️  Waiting ${delay}ms to appear more human-like...`);
  await new Promise(resolve => setTimeout(resolve, delay));
}

/**
 * Simulate human-like mouse movements before clicking
 * @param {import('playwright-chromium').Page} page - Playwright page object
 * @param {import('playwright-chromium').Locator} element - Element to click
 */
export async function humanLikeClick(page, element) {
  // Get element position
  const box = await element.boundingBox();
  if (!box) {
    console.log('  ⚠️  Element not visible, clicking directly...');
    await element.click();
    return;
  }

  // Move mouse to a random point near the element first
  const nearX = box.x + box.width / 2 + (Math.random() - 0.5) * 100;
  const nearY = box.y + box.height / 2 + (Math.random() - 0.5) * 100;
  await page.mouse.move(nearX, nearY);
  await randomSleep(100, 300);

  // Move to the element center (with slight randomness)
  const targetX = box.x + box.width / 2 + (Math.random() - 0.5) * 10;
  const targetY = box.y + box.height / 2 + (Math.random() - 0.5) * 10;
  await page.mouse.move(targetX, targetY);
  await randomSleep(100, 300);

  // Click with random delay
  await element.click({ delay: randomDelay(50, 150) });
}

/**
 * Simulate human-like typing
 * @param {import('playwright-chromium').Locator} element - Input element
 * @param {string} text - Text to type
 */
export async function humanLikeType(element, text) {
  // Type with random delays between keystrokes
  for (const char of text) {
    await element.pressSequentially(char, { delay: randomDelay(80, 200) });
  }
}

/**
 * Simulate random scroll to appear more human
 * @param {import('playwright-chromium').Page} page - Playwright page object
 */
export async function randomScroll(page) {
  const scrollAmount = Math.floor(Math.random() * 300) + 100;
  await page.mouse.wheel(0, scrollAmount);
  await randomSleep(500, 1000);
}

/**
 * Add random delays before page navigation
 * @param {import('playwright-chromium').Page} page - Playwright page object
 * @param {string} url - URL to navigate to
 * @param {object} options - Navigation options
 */
export async function humanLikeGoto(page, url, options = {}) {
  await randomSleep(2000, 4000); // Wait before navigation
  await page.goto(url, options);
  await randomSleep(1000, 2000); // Wait after page load
}

/**
 * Enhanced browser launch options with better anti-detection
 */
export function getEnhancedBrowserArgs() {
  return [
    '--disable-blink-features=AutomationControlled',
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-infobars',
    '--ignore-certificate-errors',
    '--ignore-certificate-errors-spki-list',
    '--disable-features=IsolateOrigins,site-per-process',
    '--disable-features=ScriptStreaming',
    '--disable-notifications',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',
    '--enable-features=NetworkService,NetworkServiceInProcess',
  ];
}

/**
 * Inject scripts to hide automation signals
 * @param {import('playwright-chromium').Page} page - Playwright page object
 */
export async function injectAntiDetection(page) {
  // Manual injection removed to avoid conflicts with stealth plugin
  /*
  await page.addInitScript(() => {
    // Override navigator.webdriver
    Object.defineProperty(navigator, 'webdriver', {
      get: () => false,
    });

    // Add Chrome runtime
    window.chrome = {
      runtime: {},
    };

    // Mock plugins
    Object.defineProperty(navigator, 'plugins', {
      get: () => [1, 2, 3, 4, 5],
    });

    // Mock languages
    Object.defineProperty(navigator, 'languages', {
      get: () => ['en-US', 'en'],
    });

    // Mock permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
      parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
    );
  });
  */
}

/**
 * Wait for a random amount of time before retrying on error
 * @param {number} attemptNumber - Current attempt number (for exponential backoff)
 */
export async function exponentialBackoff(attemptNumber) {
  const baseDelay = 2000;
  const maxDelay = 30000;
  const delay = Math.min(baseDelay * Math.pow(2, attemptNumber) + randomDelay(0, 1000), maxDelay);
  console.log(`  ⏳ Attempt ${attemptNumber} failed, waiting ${delay}ms before retry...`);
  await new Promise(resolve => setTimeout(resolve, delay));
}
