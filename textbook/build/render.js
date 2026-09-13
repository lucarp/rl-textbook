#!/usr/bin/env node
/* Render book.html to PDF via CDP, waiting for Paged.js to finish.
   Usage: node render.js <abs-html-path> <abs-pdf-path>
   Requires chrome-remote-interface (see textbook/build/README note in build.py). */
const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const MODULE_DIR = process.env.CRI_DIR || __dirname;
let CDP;
try { CDP = require('chrome-remote-interface'); }
catch { CDP = require(path.join(MODULE_DIR, 'node_modules', 'chrome-remote-interface')); }

const [html, pdfOut] = process.argv.slice(2);
const PORT = 9223;

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
  const profile = fs.mkdtempSync('/tmp/chrome-render-');
  const chrome = spawn('google-chrome', [
    '--headless', '--disable-gpu', '--no-sandbox',
    `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`,
    '--hide-scrollbars', 'about:blank',
  ], { stdio: 'ignore' });

  let client;
  for (let i = 0; i < 30; i++) {
    await sleep(500);
    try { client = await CDP({ port: PORT }); break; } catch { /* retry */ }
  }
  if (!client) { chrome.kill(); throw new Error('could not connect to chrome'); }

  const { Page, Runtime } = client;
  await Page.enable(); await Runtime.enable();
  await Page.navigate({ url: 'file://' + html });

  let done = false;
  for (let i = 0; i < 600; i++) {
    await sleep(1000);
    const r = await Runtime.evaluate({ expression: 'window.__PAGED_DONE__ === true' });
    if (r.result && r.result.value === true) { done = true; break; }
    if (i % 15 === 14) {
      const p = await Runtime.evaluate({ expression: "document.querySelectorAll('.pagedjs_page').length" });
      console.log(`  ...paginating (${p.result.value || 0} pages so far)`);
    }
  }
  if (!done) { chrome.kill(); throw new Error('pagination did not finish in 10 min'); }

  const pages = await Runtime.evaluate({ expression: "document.querySelectorAll('.pagedjs_page').length" });
  console.log(`pagination complete: ${pages.result.value} pages`);
  const pdf = await Page.printToPDF({ preferCSSPageSize: true, printBackground: true });
  fs.writeFileSync(pdfOut, Buffer.from(pdf.data, 'base64'));
  await client.close();
  chrome.kill();
  await sleep(1500);
  try { execSync(`rm -rf ${profile}`); } catch { /* best-effort cleanup */ }
}

main().catch(e => { console.error(e.message); process.exit(1); });
