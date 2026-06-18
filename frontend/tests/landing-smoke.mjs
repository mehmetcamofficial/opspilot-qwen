const baseUrl = process.env.LANDING_SMOKE_URL || "http://localhost:3001";

async function loadPuppeteer() {
  try {
    return await import("puppeteer");
  } catch {
    throw new Error("Landing smoke test requires Puppeteer. Install it before running this check.");
  }
}

async function assertPageHasText(page, text) {
  const found = await page.evaluate((expectedText) => document.body.innerText.includes(expectedText), text);
  if (!found) {
    throw new Error(`Expected landing page text was not found: ${text}`);
  }
}

const puppeteer = await loadPuppeteer();
const browser = await puppeteer.default.launch({
  headless: "new",
  args: [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding",
    "--disable-backgrounding-occluded-windows",
  ],
});

try {
  const page = await browser.newPage();
  const consoleErrors = [];

  page.on("console", (message) => {
    if (message.type() === "error") {
      consoleErrors.push(message.text());
    }
  });
  page.on("pageerror", (error) => {
    consoleErrors.push(error.message);
  });

  await page.goto(baseUrl, { waitUntil: "networkidle2" });
  await assertPageHasText(page, "AI incident operations,");
  await assertPageHasText(page, "Live incident command");
  await assertPageHasText(page, "Incidents do not wait. Your tools should not either.");
  await assertPageHasText(page, "Platform Engineers");

  await page.click('button[aria-label="Toggle language"]');
  await page.waitForFunction(() => document.body.innerText.includes("Yapay zeka olay operasyonları,"));
  await page.waitForFunction(() => document.body.innerText.includes("Olaylar beklemez. Araçlarınız da beklememeli."));
  await page.click('button[aria-label="Toggle language"]');
  await page.waitForFunction(() => document.body.innerText.includes("AI incident operations,"));

  await page.evaluate(() => {
    const dashboardLink = Array.from(document.querySelectorAll('a[href="/dashboard"]')).find((link) =>
      link.textContent?.includes("Open Command Center")
    );
    if (!(dashboardLink instanceof HTMLElement)) {
      throw new Error("Open Command Center link was not found.");
    }
    dashboardLink.click();
  });
  await page.waitForFunction(() => window.location.pathname === "/dashboard");

  const blockingErrors = consoleErrors.filter((message) => !message.includes("/_next/webpack-hmr"));
  if (blockingErrors.length > 0) {
    throw new Error(`Browser console errors found:\n${blockingErrors.join("\n")}`);
  }

  console.log("Landing smoke test passed.");
} finally {
  await browser.close();
}
