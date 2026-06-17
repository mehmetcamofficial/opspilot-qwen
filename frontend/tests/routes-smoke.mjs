const baseUrl = process.env.ROUTES_SMOKE_URL || "http://localhost:3001";

const routes = [
  { path: "/", expectedText: "AI incident operations," },
  { path: "/dashboard", expectedText: "Command Center" },
  { path: "/simulation", expectedText: "Simulation Lab" },
  { path: "/status", expectedText: "Public status" },
  { path: "/architecture", expectedText: "System architecture" },
  { path: "/admin", expectedText: "Governance Console" },
  { path: "/knowledge-graph", expectedText: "Reasoning Graph" },
];

async function loadPuppeteer() {
  try {
    return await import("puppeteer");
  } catch {
    throw new Error("Route smoke test requires Puppeteer. Run the root install before this check.");
  }
}

function isIgnorableConsoleError(message) {
  return message.includes("/_next/webpack-hmr");
}

const puppeteer = await loadPuppeteer();
const browser = await puppeteer.default.launch({
  headless: "new",
  args: ["--no-sandbox", "--disable-setuid-sandbox"],
});

try {
  const page = await browser.newPage();
  const consoleErrors = [];

  page.on("console", (message) => {
    if (message.type() === "error" && !isIgnorableConsoleError(message.text())) {
      consoleErrors.push(message.text());
    }
  });

  page.on("pageerror", (error) => {
    consoleErrors.push(error.message);
  });

  for (const route of routes) {
    const response = await page.goto(new URL(route.path, baseUrl).toString(), { waitUntil: "networkidle2" });
    const status = response?.status();

    if (status !== 200) {
      throw new Error(`${route.path} returned ${status || "no response"} instead of 200.`);
    }

    const hasExpectedText = await page.evaluate(
      (expectedText) => document.body.innerText.includes(expectedText),
      route.expectedText
    );

    if (!hasExpectedText) {
      throw new Error(`${route.path} did not render expected text: ${route.expectedText}`);
    }
  }

  if (consoleErrors.length > 0) {
    throw new Error(`Browser console errors found:\n${consoleErrors.join("\n")}`);
  }

  console.log(`Route smoke test passed for ${routes.length} routes.`);
} finally {
  await browser.close();
}
