const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file:///home/user/Tera-results/results.html');
  await p.pdf({ path: '/home/user/Tera-results/Netley-SC-Tera-Results-2026-10-31.pdf', format: 'A4', printBackground: true, preferCSSPageSize: true });
  await p.screenshot({ path: '/tmp/claude-0/-home-user-Tera-results/202fa9c7-0e0a-576f-826a-b7e5f67906d9/scratchpad/preview.png', fullPage: true });
  await b.close();
})();
