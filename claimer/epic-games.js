import { chromium } from 'playwright-chromium'; // stealth plugin needs no outdated playwright-extra
import { authenticator } from 'otplib';
import chalk from 'chalk';
import path from 'path';
import { existsSync, writeFileSync, appendFileSync } from 'fs';
import { resolve, jsonDb, datetime, stealth, filenamify, prompt, notify, html_game_list, handleSIGINT } from './src/util.js';
import { cfg } from './src/config.js';
import { randomSleep, humanLikeClick, humanLikeGoto, getEnhancedBrowserArgs, injectAntiDetection, randomScroll } from './src/anti-detection.js';

const screenshot = (...a) => resolve(cfg.dir.screenshots, 'epic-games', ...a);

// Use China region (zh-CN) for accessibility from mainland China without proxy
// Note: Game availability may differ between regions
// If you need en-US region games, you must configure PROXY_HOST in .env
const USE_CHINA_REGION = !process.env.PROXY_HOST; // Use China region only when no proxy is configured
const REGION = USE_CHINA_REGION ? 'zh-CN' : 'en-US';
const URL_CLAIM = `https://store.epicgames.com/${REGION}/free-games`;
const URL_LOGIN = `https://www.epicgames.com/id/login?lang=${REGION}&noHostRedirect=true&redirectUrl=` + URL_CLAIM;

console.log(datetime(), 'started checking epic-games');

const db = await jsonDb('epic-games.json', {});

// Try to load cookies from external file (exported from real browser)
let externalCookies = null;
// Check multiple locations for cookies.json:
// 1. claimer/data/cookies.json (standard data dir)
// 2. ../cookies.json (relative to browser dir, legacy)
const cookiePaths = [
  resolve(cfg.dir.browser, '../cookies.json'),
  path.resolve(process.cwd(), 'data', 'cookies.json'),
  path.resolve(process.cwd(), 'cookies.json')
];

for (const p of cookiePaths) {
  if (p && existsSync(p)) {
     try {
       const cookiesContent = await import('fs').then(fs => fs.promises.readFile(p, 'utf8'));
       externalCookies = JSON.parse(cookiesContent);
       console.log(`✅ Loaded ${externalCookies.length} cookies from: ${p}`);
       break; 
     } catch (e) {
       console.warn(`⚠️  Found cookies file at ${p} but failed to load:`, e.message);
     }
  }
}


if (cfg.time) console.time('startup');

// https://playwright.dev/docs/auth#multi-factor-authentication
  // Configure proxy if PROXY_HOST environment variable is set
  const proxyConfig = process.env.PROXY_HOST ? {
    server: `http://${process.env.PROXY_HOST}`,
  } : undefined;

  if (proxyConfig) {
    console.log(`Using proxy (${proxyConfig.server}) to access ${REGION} region`);
  } else {
    console.log(`Accessing ${REGION} region without proxy`);
  }

  const context = await chromium.launchPersistentContext(cfg.dir.browser, {
    headless: !!cfg.headless,
    viewport: { width: cfg.width, height: cfg.height },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36', // Updated to recent Chrome version
    locale: REGION,
    proxy: proxyConfig,
    recordVideo: cfg.record ? { dir: 'data/record/', size: { width: cfg.width, height: cfg.height } } : undefined,
    recordHar: cfg.record ? { path: `data/record/eg-${filenamify(datetime())}.har` } : undefined,
    handleSIGINT: false,
    args: getEnhancedBrowserArgs(),
    ignoreDefaultArgs: ['--enable-automation'], // Crucial: removes "Chrome is being controlled by automated test software" bar
  });

handleSIGINT(context);

// Without stealth plugin, the website shows an hcaptcha on login with username/password and in the last step of claiming a game. It may have other heuristics like unsuccessful logins as well. After <6h (TBD) it resets to no captcha again. Getting a new IP also resets.
await stealth(context);

if (!cfg.debug) context.setDefaultTimeout(cfg.timeout);

const page = context.pages().length ? context.pages()[0] : await context.newPage(); // should always exist
await page.setViewportSize({ width: cfg.width, height: cfg.height }); // TODO workaround for https://github.com/vogler/free-games-claimer/issues/277 until Playwright fixes it

// Inject anti-detection scripts
// await injectAntiDetection(page); // Removed manual injection to avoid conflicts with stealth plugin and detection


// some debug info about the page (screen dimensions, user agent, platform)
// eslint-disable-next-line no-undef
if (cfg.debug) console.debug(await page.evaluate(() => [(({ width, height, availWidth, availHeight }) => ({ width, height, availWidth, availHeight }))(window.screen), navigator.userAgent, navigator.platform, navigator.vendor])); // deconstruct screen needed since `window.screen` prints {}, `window.screen.toString()` '[object Screen]', and can't use some pick function without defining it on `page`
if (cfg.debug_network) {
  // const filter = _ => true;
  const filter = r => r.url().includes('store.epicgames.com');
  page.on('request', request => filter(request) && console.log('>>', request.method(), request.url()));
  page.on('response', response => filter(response) && console.log('<<', response.status(), response.url()));
}

const notify_games = [];
let user;

try {
  // Load external cookies if available (from real browser)
  if (externalCookies) {
    console.log('🔑 Loading cookies from real browser session...');
    await context.addCookies(externalCookies);
    await randomSleep(1000, 2000);
  }

  // IMPORTANT: Start from login page directly if not logged in yet
  // This is more natural than visiting the store first without auth
  console.log('Checking if already logged in...');

  // User suggested always starting from the login URL to avoid anti-crawler issues
  // If we have cookies, this will redirect to the claim page automatically
  console.log('Visiting login page to ensure valid session...');
  await randomSleep(2000, 4000);
  await page.goto(URL_LOGIN, { waitUntil: 'load', timeout: 60000 });
  await randomSleep(3000, 5000);

  /*
  // First check if we have existing cookies (from previous successful login)
  const cookies = await context.cookies();
  const hasAuthCookies = cookies.some(c => c.name.includes('EPIC') || c.name.includes('eg-auth'));

  if (hasAuthCookies) {
    console.log('Found existing auth cookies, visiting store page...');
    // Add random delay before first page load
    await randomSleep(2000, 4000);
    // Use 'load' instead of 'domcontentloaded' to wait for all resources including Cloudflare scripts
    await page.goto(URL_CLAIM, { waitUntil: 'load', timeout: 60000 });
    // Wait after initial page load - longer delay to let Cloudflare scripts execute
    await randomSleep(3000, 5000);
  }
  */

  // Now set cookies AFTER visiting the page naturally
  await context.addCookies([
    { name: 'OptanonAlertBoxClosed', value: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), domain: '.epicgames.com', path: '/' },
    { name: 'HasAcceptedAgeGates', value: 'USK:9007199254740991,general:18,EPIC SUGGESTED RATING:18', domain: 'store.epicgames.com', path: '/' },
  ]);

  if (cfg.time) console.timeEnd('startup');
  if (cfg.time) console.time('login');

  // Check login status
  let isLoggedIn = false;
  try {
    // Try to detect login status from navigation element
    // This works on both store page (if redirected) and potentially login page
    const nav = page.locator('egs-navigation');
    if (await nav.count() > 0) {
      const isLoggedAttr = await nav.getAttribute('isloggedin', { timeout: 5000 });
      isLoggedIn = isLoggedAttr == 'true';
      if (!isLoggedIn) {
        console.log(`Login check failed: egs-navigation found but isloggedin="${isLoggedAttr}"`);
      }
    } else {
      console.log('Login check failed: egs-navigation element not found');
    }
  } catch (e) {
    console.log('Could not determine login status, will try to login...');
  }

  while (!isLoggedIn) {
    // If external cookies were loaded but login failed, do not attempt to login again
    if (externalCookies) {
       console.error('❌ External cookies loaded but session is invalid/expired.');
       console.error('Please update claimer/data/cookies.json with fresh cookies from your browser.');
       process.exit(1);
    }
    
    console.error('Not signed in anymore. Please login in the browser or here in the terminal.');
    if (cfg.novnc_port) console.info(`Open http://localhost:${cfg.novnc_port} to login inside the docker container.`);
    if (!cfg.debug) context.setDefaultTimeout(cfg.login_timeout); // give user some extra time to log in
    console.info(`Login timeout is ${cfg.login_timeout / 1000} seconds!`);
    // Add delay before navigating to login page
    await randomSleep(2000, 3000);
    // Use 'load' to wait for all Cloudflare scripts
    await page.goto(URL_LOGIN, { waitUntil: 'load', timeout: 90000 });
    if (cfg.eg_email && cfg.eg_password) console.info('Using email and password from environment.');
    else console.info('Press ESC to skip the prompts if you want to login in the browser (not possible in headless mode).');
    const notifyBrowserLogin = async () => {
      console.log('Waiting for you to login in the browser.');
      await notify('epic-games: no longer signed in and not enough options set for automatic login.');
      if (cfg.headless) {
        console.log('Run `SHOW=1 node epic-games` to login in the opened browser.');
        await context.close(); // finishes potential recording
        process.exit(1);
      }
    };
    const email = cfg.eg_email || await prompt({ message: 'Enter email' });
    if (!email) await notifyBrowserLogin();
    else {
      // Click "Sign in with Epic Games" button if it exists (supports both English and Chinese)
      // English: "Sign in with Epic Games", Chinese: "登录"
      const signInBtn = page.locator('button:has-text("Sign in with Epic Games"), button:has-text("登录")');
      if (await signInBtn.count() > 0) {
        console.log('  Clicking sign in button...');
        await signInBtn.first().click();
        await randomSleep(1000, 2000);
      }
      page.waitForSelector('.h_captcha_challenge iframe').then(async () => {
        console.error('Got a captcha during login (likely due to too many attempts)! You may solve it in the browser, get a new IP or try again in a few hours.');
        await notify('epic-games: got captcha during login. Please check.');
      }).catch(_ => { });
      page.waitForSelector('p:has-text("Incorrect response.")').then(async () => {
        console.error('Incorrect response for captcha!');
      }).catch(_ => { });
      await page.fill('#email', email);
      // await page.click('button[type="submit"]'); login was split in two steps for some time, now email and password are on the same form again
      const password = email && (cfg.eg_password || await prompt({ type: 'password', message: 'Enter password' }));
      if (!password) await notifyBrowserLogin();
      else {
        await page.fill('#password', password);
        await page.click('button[type="submit"]');
      }
      const error = page.locator('#form-error-message');
      error.waitFor().then(async () => {
        console.error('Login error:', await error.innerText());
        console.log('Please login in the browser!');
      }).catch(_ => { });
      // handle MFA, but don't await it
      page.waitForURL('**/id/login/mfa**').then(async () => {
        console.log('Enter the security code to continue - This appears to be a new device, browser or location. A security code has been sent to your email address at ...');
        // TODO locator for text (email or app?)
        const otp = cfg.eg_otpkey && authenticator.generate(cfg.eg_otpkey) || await prompt({ type: 'text', message: 'Enter two-factor sign in code', validate: n => n.toString().length == 6 || 'The code must be 6 digits!' }); // can't use type: 'number' since it strips away leading zeros and codes sometimes have them
        await page.locator('input[name="code-input-0"]').pressSequentially(otp.toString());
        await page.click('button[type="submit"]');
      }).catch(_ => { });
    }
    await page.waitForURL(URL_CLAIM);
    if (!cfg.debug) context.setDefaultTimeout(cfg.timeout);

    // Check if now logged in
    try {
      isLoggedIn = await page.locator('egs-navigation').getAttribute('isloggedin', { timeout: 5000 }) == 'true';
    } catch (e) {
      console.error('Failed to verify login status after login attempt');
      isLoggedIn = false;
    }
  }
  user = await page.locator('egs-navigation').getAttribute('displayname'); // 'null' if !isloggedin
  console.log(`Signed in as ${user}`);
  db.data[user] ||= {};
  if (cfg.time) console.timeEnd('login');
  if (cfg.time) console.time('claim all games');

  // Detect free games - support both English and Chinese text
  // English: "Free Now", Chinese: "现在免费"
  const game_loc = page.locator('a:has(span:text-is("Free Now")), a:has(span:text-is("现在免费"))');
  await game_loc.last().waitFor().catch(_ => {
    // rarely there are no free games available -> catch Timeout
    // TODO would be better to wait for alternative like 'coming soon' instead of waiting for timeout
    // see https://github.com/vogler/free-games-claimer/issues/210#issuecomment-1727420943
    console.error('Seems like currently there are no free games available in your region...');
    // urls below should then be an empty list
  });
  // clicking on `game_sel` sometimes led to a 404, see https://github.com/vogler/free-games-claimer/issues/25
  // debug showed that in those cases the href was still correct, so we `goto` the urls instead of clicking.
  // Alternative: parse the json loaded to build the page https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions
  // i.e. filter data.Catalog.searchStore.elements for .promotions.promotionalOffers being set and build URL with .catalogNs.mappings[0].pageSlug or .urlSlug if not set to some wrong id like it was the case for spirit-of-the-north-f58a66 - this is also what's done here: https://github.com/claabs/epicgames-freegames-node/blob/938a9653ffd08b8284ea32cf01ac8727d25c5d4c/src/puppet/free-games.ts#L138-L213
  const urlSlugs = await Promise.all((await game_loc.elementHandles()).map(a => a.getAttribute('href')));
  const urls = urlSlugs.map(s => 'https://store.epicgames.com' + s);
  console.log('Free games:', urls);

  for (const url of urls) {
    if (cfg.time) console.time('claim game');

    // Add random delay before navigating to each game page
    await randomSleep(3000, 6000);
    // Use 'load' to ensure all Cloudflare scripts execute
    await page.goto(url, { waitUntil: 'load', timeout: 90000 });

    // Wait a bit after page load to appear more human and let Cloudflare scripts finish
    await randomSleep(3000, 5000);

    // Simulate random scroll
    await randomScroll(page);

    // Check for Cloudflare challenge
    const pageTitle = await page.title();
    if (pageTitle.includes('Just a moment') || await page.locator('text=One more step').count() > 0) {
      console.error('⚠️  Cloudflare security check detected!');
      console.error('This happens when Epic Games detects automated access.');
      console.error('Possible solutions:');
      console.error('  1. Wait a few hours before trying again');
      console.error('  2. Manually visit the game page in a browser to complete the check');
      console.error('  3. Clear browser data: rm -rf claimer/data/browser');
      await page.screenshot({ path: screenshot('cloudflare-challenge.png'), fullPage: true });
      console.error('Screenshot saved to:', screenshot('cloudflare-challenge.png'));
      throw new Error('Cloudflare security check blocking access');
    }

    // Support both English and Chinese button text
    // English: "Get", "In Library", "Requires Base Game"
    // Chinese: "获取", "在游戏库中", "需要主游戏"
    const purchaseBtn = page.locator('button[data-testid="purchase-cta-button"]').first();
    // Wait for button to have text (not empty)
    try {
      await purchaseBtn.waitFor();
    } catch (e) {
      console.error('Failed to find purchase button, taking screenshot for debugging...');
      await page.screenshot({ path: screenshot('error-no-purchase-btn.png'), fullPage: true });
      console.error('Screenshot saved to:', screenshot('error-no-purchase-btn.png'));

      // Check again for Cloudflare after timeout
      if (pageTitle.includes('Just a moment') || await page.locator('text=One more step').count() > 0) {
        console.error('⚠️  Still blocked by Cloudflare security check');
      }

      throw e;
    }
    const btnText = (await purchaseBtn.innerText()).toLowerCase(); // barrier to block until page is loaded

    // click Continue if 'This game contains mature content recommended only for ages 18+'
    // Support Chinese: "继续"
    const continueBtn = page.locator('button:has-text("Continue"), button:has-text("继续")');
    if (await continueBtn.count() > 0) {
      console.log('  This game contains mature content recommended only for ages 18+');
      if (await page.locator('[data-testid="AgeSelect"]').count()) {
        console.error('  Got "To continue, please provide your date of birth" - This shouldn\'t happen due to cookie set above. Please report to https://github.com/vogler/free-games-claimer/issues/275');
        await page.locator('#month_toggle').click();
        await page.locator('#month_menu li:has-text("01")').click();
        await page.locator('#day_toggle').click();
        await page.locator('#day_menu li:has-text("01")').click();
        await page.locator('#year_toggle').click();
        await page.locator('#year_menu li:has-text("1987")').click();
      }
      await continueBtn.click({ delay: 111 });
      await page.waitForTimeout(2000);
    }

    let title;
    let bundle_includes;
    if (await page.locator('span:text-is("About Bundle")').count()) {
      title = (await page.locator('span:has-text("Buy"):left-of([data-testid="purchase-cta-button"])').first().innerText()).replace('Buy ', '');
      // h1 first didn't exist for bundles but now it does... However h1 would e.g. be 'Fallout® Classic Collection' instead of 'Fallout Classic Collection'
      try {
        bundle_includes = await Promise.all((await page.locator('.product-card-top-row h5').all()).map(b => b.innerText()));
      } catch (e) {
        console.error('Failed to get "Bundle Includes":', e);
      }
    } else {
      title = await page.locator('h1').first().innerText();
    }
    const game_id = page.url().split('/').pop();
    const existedInDb = db.data[user][game_id];
    db.data[user][game_id] ||= { title, time: datetime(), url: page.url() }; // this will be set on the initial run only!
    console.log('Current free game:', chalk.blue(title));
    if (bundle_includes) console.log('  This bundle includes:', bundle_includes);
    const notify_game = { title, url, status: 'failed' };
    notify_games.push(notify_game); // status is updated below

    // Support both English and Chinese button text
    if (btnText == 'in library' || btnText == '在游戏库中') {
      console.log('  Already in library! Nothing to claim.');
      if (!existedInDb) await notify(`Game already in library: ${url}`);
      notify_game.status = 'existed';
      db.data[user][game_id].status ||= 'existed'; // does not overwrite claimed or failed
      if (db.data[user][game_id].status.startsWith('failed')) db.data[user][game_id].status = 'manual'; // was failed but now it's claimed
    } else if (btnText == 'requires base game' || btnText == '需要主游戏' || btnText.includes('需要')) {
      console.log('  Requires base game! Nothing to claim.');
      notify_game.status = 'requires base game';
      db.data[user][game_id].status ||= 'failed:requires-base-game';
      // TODO claim base game if it is free
      const baseUrl = 'https://store.epicgames.com' + await page.locator('a:has-text("Overview")').getAttribute('href');
      console.log('  Base game:', baseUrl);
      // await page.click('a:has-text("Overview")');
      // TODO handle this via function call for base game above since this will never terminate if DRYRUN=1
      urls.push(baseUrl); // add base game to the list of games to claim
      urls.push(url); // add add-on itself again
    } else { // GET / 获取
      console.log('  Not in library yet! Click', btnText);
      // Add random delay before clicking to appear more human
      await randomSleep(1000, 2000);
      await humanLikeClick(page, purchaseBtn); // Use human-like click instead of direct click

      // click Continue if 'Device not supported. This product is not compatible with your current device.' - avoided by Windows userAgent?
      // Support Chinese: "继续"
      page.click('button:has-text("Continue"), button:has-text("继续")').catch(_ => { }); // needed since change from Chromium to Firefox?

      // click 'Yes, buy now' if 'This edition contains something you already have. Still interested?'
      // Support Chinese: "是的，立即购买"
      page.click('button:has-text("Yes, buy now"), button:has-text("是的，立即购买")').catch(_ => { });

      // Accept End User License Agreement (only needed once)
      // Support Chinese: "最终用户许可协议"
      page.locator(':has-text("end user license agreement"), :has-text("最终用户许可协议")').waitFor().then(async () => {
        console.log('  Accept End User License Agreement (only needed once)');
        console.log(page.innerHTML);
        console.log('Please report the HTML above here: https://github.com/vogler/free-games-claimer/issues/371');
        await page.locator('input#agree').check(); // TODO Bundle: got stuck here; likely unrelated to bundle and locator just changed: https://github.com/vogler/free-games-claimer/issues/371
        await page.locator('button:has-text("Accept"), button:has-text("接受")').click();
      }).catch(_ => { });

      // it then creates an iframe for the purchase
      await page.waitForSelector('#webPurchaseContainer iframe'); // TODO needed?
      const iframe = page.frameLocator('#webPurchaseContainer iframe');
      // skip game if unavailable in region, https://github.com/vogler/free-games-claimer/issues/46 TODO check games for account's region
      // Support Chinese: "在您所在的地区不可用"
      if (await iframe.locator(':has-text("unavailable in your region"), :has-text("在您所在的地区不可用")').count() > 0) {
        console.error('  This product is unavailable in your region!');
        db.data[user][game_id].status = notify_game.status = 'unavailable-in-region';
        if (cfg.time) console.timeEnd('claim game');
        continue;
      }

      iframe.locator('.payment-pin-code').waitFor().then(async () => {
        if (!cfg.eg_parentalpin) {
          console.error('  EG_PARENTALPIN not set. Need to enter Parental Control PIN manually.');
          notify('epic-games: EG_PARENTALPIN not set. Need to enter Parental Control PIN manually.');
        }
        await iframe.locator('input.payment-pin-code__input').first().pressSequentially(cfg.eg_parentalpin);
        await iframe.locator('button:has-text("Continue")').click({ delay: 11 });
      }).catch(_ => { });

      if (cfg.debug) await page.pause();
      if (cfg.dryrun) {
        console.log('  DRYRUN=1 -> Skip order!');
        notify_game.status = 'skipped';
        if (cfg.time) console.timeEnd('claim game');
        continue;
      }

      // Playwright clicked before button was ready to handle event, https://github.com/vogler/free-games-claimer/issues/84#issuecomment-1474346591
      // Add random delay before clicking Place Order
      await randomSleep(1500, 3000);
      // Support both English and Chinese: "Place Order" / "下订单"
      const placeOrderBtn = iframe.locator('button:has-text("Place Order"):not(:has(.payment-loading--loading)), button:has-text("下订单"):not(:has(.payment-loading--loading))');
      await placeOrderBtn.click({ delay: 11 });

      // I Agree button is only shown for EU accounts! https://github.com/vogler/free-games-claimer/pull/7#issuecomment-1038964872
      // Support Chinese: "我接受"
      const btnAgree = iframe.locator('button:has-text("I Accept"), button:has-text("我接受")');
      btnAgree.waitFor().then(() => btnAgree.click()).catch(_ => { }); // EU: wait for and click 'I Agree'
      try {
        // context.setDefaultTimeout(100 * 1000); // give time to solve captcha, iframe goes blank after 60s?
        const captcha = iframe.locator('#h_captcha_challenge_checkout_free_prod iframe');
        captcha.waitFor().then(async () => { // don't await, since element may not be shown
          // console.info('  Got hcaptcha challenge! NopeCHA extension will likely solve it.')
          console.error('  Got hcaptcha challenge! Lost trust due to too many login attempts? You can solve the captcha in the browser or get a new IP address.');
          // await notify(`epic-games: got captcha challenge right before claim of <a href="${url}">${title}</a>. Use VNC to solve it manually.`); // TODO not all apprise services understand HTML: https://github.com/vogler/free-games-claimer/pull/417
          await notify(`epic-games: got captcha challenge for.\nGame link: ${url}`);
          // TODO could even create purchase URL, see https://github.com/vogler/free-games-claimer/pull/130
          // await page.waitForTimeout(2000);
          // const p = path.resolve(cfg.dir.screenshots, 'epic-games', 'captcha', `${filenamify(datetime())}.png`);
          // await captcha.screenshot({ path: p });
          // console.info('  Saved a screenshot of hcaptcha challenge to', p);
          // console.error('  Got hcaptcha challenge. To avoid it, get a link from https://www.hcaptcha.com/accessibility'); // TODO save this link in config and visit it daily to set accessibility cookie to avoid captcha challenge?
        }).catch(_ => { }); // may time out if not shown
        iframe.locator('.payment__errors:has-text("Failed to challenge captcha, please try again later.")').waitFor().then(async () => {
          console.error('  Failed to challenge captcha, please try again later.');
          await notify('epic-games: failed to challenge captcha. Please check.');
        }).catch(_ => { });
        await page.locator('text=Thanks for your order!').waitFor({ state: 'attached' }); // TODO Bundle: got stuck here, but normal game now as well
        db.data[user][game_id].status = 'claimed';
        db.data[user][game_id].time = datetime(); // claimed time overwrites failed/dryrun time
        console.log('  Claimed successfully!');
        // context.setDefaultTimeout(cfg.timeout);
      } catch (e) {
        console.log(e);
        // console.error('  Failed to claim! Try again if NopeCHA timed out. Click the extension to see if you ran out of credits (refill after 24h). To avoid captchas try to get a new IP or set a cookie from https://www.hcaptcha.com/accessibility');
        console.error('  Failed to claim! To avoid captchas try to get a new IP address.');
        const p = screenshot('failed', `${game_id}_${filenamify(datetime())}.png`);
        await page.screenshot({ path: p, fullPage: true });
        db.data[user][game_id].status = 'failed';
      }
      notify_game.status = db.data[user][game_id].status; // claimed or failed

      const p = screenshot(`${game_id}.png`);
      if (!existsSync(p)) await page.screenshot({ path: p, fullPage: false }); // fullPage is quite long...
    }
    if (cfg.time) console.timeEnd('claim game');
  }
  if (cfg.time) console.timeEnd('claim all games');
} catch (error) {
  process.exitCode ||= 1;
  console.error('--- Exception:');
  console.error(error); // .toString()?
  if (error.message && process.exitCode != 130) notify(`epic-games failed: ${error.message.split('\n')[0]}`);
} finally {
  await db.write(); // write out json db
  if (notify_games.filter(g => g.status == 'claimed' || g.status == 'failed').length) { // don't notify if all have status 'existed', 'manual', 'requires base game', 'unavailable-in-region', 'skipped'
    notify(`epic-games (${user}):<br>${html_game_list(notify_games)}`);
  }
}
if (cfg.debug) writeFileSync(path.resolve(cfg.dir.browser, 'cookies.json'), JSON.stringify(await context.cookies()));
if (page.video()) console.log('Recorded video:', await page.video().path());
await context.close();
