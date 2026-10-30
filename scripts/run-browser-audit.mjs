import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);
const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const BASE_URL = 'http://localhost:4173';

const ROUTES = [
  {
    path: '/',
    expectedTitle: 'PipeBot | Intelligent Pipeline Inspection',
    expectedContent: 'Intelligent Inspection Inside Every Pipeline',
  },
  {
    path: '/privacy',
    expectedTitle: 'PipeBot | Privacy Policy (Draft)',
    expectedContent: 'Privacy Policy & Data Architecture Draft',
  },
  {
    path: '/terms',
    expectedTitle: 'PipeBot | Terms of Use (Draft)',
    expectedContent: 'Terms of Use & Prototype Disclaimers',
  },
  {
    path: '/dashboard',
    expectedTitle: 'PipeBot | Console Overview',
    expectedContent: 'Subsystem Link Matrix',
  },
  {
    path: '/dashboard/inspection',
    expectedTitle: 'PipeBot | Live Inspection',
    expectedContent: 'Real-Time Detections',
  },
  {
    path: '/dashboard/vehicle',
    expectedTitle: 'PipeBot | Vehicle Control',
    expectedContent: 'Propulsion Direction Control',
  },
  {
    path: '/dashboard/telemetry',
    expectedTitle: 'PipeBot | Odometry & Telemetry',
    expectedContent: 'Linear Traversal (Distance vs. Time)',
  },
  {
    path: '/dashboard/defects',
    expectedTitle: 'PipeBot | Defect Registry',
    expectedContent: 'YOLO Target Anomaly Registry',
  },
  {
    path: '/dashboard/history',
    expectedTitle: 'PipeBot | Inspection History',
    expectedContent: 'Mission Log History',
  },
  {
    path: '/dashboard/reports',
    expectedTitle: 'PipeBot | Inspection Reports',
    expectedContent: 'Generated Engineering Reports',
  },
  {
    path: '/dashboard/settings',
    expectedTitle: 'PipeBot | System Settings',
    expectedContent: 'Hardware Configuration Registry',
  },
];

const VIEWPORTS = [
  { name: 'Desktop (1440x900)', width: 1440, height: 900 },
  { name: 'Laptop (1366x768)', width: 1366, height: 768 },
  { name: 'Tablet (768x1024)', width: 768, height: 1024 },
  { name: 'Mobile (390x844)', width: 390, height: 844 },
  { name: 'Small mobile (360x800)', width: 360, height: 800 },
];

async function runBrowserAudit() {
  console.log('Starting Browser-Level Audit with Real Chrome Headless Engine...');
  console.log(`Target Preview Server: ${BASE_URL}\n`);

  let passedRoutes = 0;

  // 1. Audit Every Route
  for (const route of ROUTES) {
    const url = `${BASE_URL}${route.path}`;
    try {
      const { stdout } = await execFileAsync(
        CHROME_PATH,
        [
          '--headless=new',
          '--disable-gpu',
          '--no-sandbox',
          '--virtual-time-budget=2000',
          '--dump-dom',
          url,
        ],
        { timeout: 15000 }
      );

      const decodedStdout = stdout.replaceAll('&amp;', '&');
      const containsContent = decodedStdout.includes(route.expectedContent);
      const titleMatch = stdout.match(/<title>([^<]+)<\/title>/i);
      const actualTitle = titleMatch ? titleMatch[1].trim().replaceAll('&amp;', '&') : 'Unknown';

      if (containsContent && actualTitle === route.expectedTitle) {
        console.log(`[PASS] Route: ${route.path.padEnd(24)} | Title: ${actualTitle}`);
        passedRoutes++;
      } else {
        console.error(`[FAIL] Route: ${route.path}`);
        console.error(`       Expected title: "${route.expectedTitle}", got: "${actualTitle}"`);
        console.error(`       Found content "${route.expectedContent}": ${containsContent}`);
      }
    } catch (err) {
      console.error(`[ERROR] Failed to audit ${route.path}:`, err.message);
    }
  }

  console.log(`\nRoute Verification: ${passedRoutes}/${ROUTES.length} passed.\n`);

  // 2. Audit Viewports on Dashboard
  console.log('Testing Target Responsive Viewports on Chrome Engine...');
  let passedViewports = 0;
  for (const vp of VIEWPORTS) {
    try {
      const { stdout } = await execFileAsync(
        CHROME_PATH,
        [
          '--headless=new',
          '--disable-gpu',
          '--no-sandbox',
          '--virtual-time-budget=2000',
          `--window-size=${vp.width},${vp.height}`,
          '--dump-dom',
          `${BASE_URL}/dashboard`,
        ],
        { timeout: 15000 }
      );

      if (stdout.includes('Subsystem Link Matrix')) {
        console.log(`[PASS] Viewport: ${vp.name.padEnd(25)} | Window: ${vp.width}x${vp.height} | Rendered OK`);
        passedViewports++;
      } else {
        console.error(`[FAIL] Viewport ${vp.name} failed to render main content.`);
      }
    } catch (err) {
      console.error(`[ERROR] Viewport ${vp.name} error:`, err.message);
    }
  }

  console.log(`\nViewport Verification: ${passedViewports}/${VIEWPORTS.length} passed.`);

  if (passedRoutes === ROUTES.length && passedViewports === VIEWPORTS.length) {
    console.log('\n========================================================');
    console.log('ALL BROWSER-LEVEL QA CHECKS PASSED WITH 100% SUCCESS.');
    console.log('========================================================\n');
    process.exit(0);
  } else {
    console.error('\nSOME BROWSER-LEVEL QA CHECKS FAILED.');
    process.exit(1);
  }
}

runBrowserAudit().catch((err) => {
  console.error('Fatal audit failure:', err);
  process.exit(1);
});
