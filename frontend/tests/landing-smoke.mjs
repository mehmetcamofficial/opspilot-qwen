const baseUrl = process.env.LANDING_SMOKE_URL || "http://localhost:3001";
const stepLabels = ["Alert intake", "Evidence correlation", "Safety gate", "Recovery verified"];

function sleep(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function loadPuppeteer() {
  try {
    return await import("puppeteer");
  } catch {
    throw new Error("Landing smoke test requires Puppeteer. Install it before running this check.");
  }
}

async function activeStepLabel(page) {
  return page.evaluate((labels) => {
    const activeButton = Array.from(document.querySelectorAll("button")).find((button) => {
      const text = button.textContent || "";
      return button.className.includes("bg-cyan-300") && labels.some((label) => text.includes(label));
    });

    return labels.find((label) => activeButton?.textContent?.includes(label)) || null;
  }, stepLabels);
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
  await assertPageHasText(page, "Live command flow");

  const observedSteps = new Set();
  for (let attempt = 0; attempt < 8; attempt += 1) {
    const label = await activeStepLabel(page);
    if (label) {
      observedSteps.add(label);
    }
    await sleep(1100);
  }

  if (observedSteps.size < 3) {
    throw new Error(`Live command flow did not advance through enough steps. Observed=${Array.from(observedSteps).join(", ")}`);
  }

  await page.click('button[aria-label="Toggle language"]');
  await page.waitForFunction(() => document.body.innerText.includes("Yapay zeka olay operasyonları,"));
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
