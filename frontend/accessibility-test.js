/**
 * Neo Alexandria 2.0 - Automated Accessibility Testing Script
 * 
 * This script performs automated accessibility checks on the application
 * using axe-core. It can be run as part of CI/CD or manually.
 * 
 * Usage:
 *   node accessibility-test.js
 * 
 * Requirements:
 *   npm install --save-dev axe-core puppeteer
 */

const puppeteer = require('puppeteer');
const { AxePuppeteer } = require('@axe-core/puppeteer');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  baseUrl: process.env.VITE_APP_URL || 'http://localhost:5173',
  outputDir: './accessibility-reports',
  pages: [
    { name: 'Home', url: '/' },
    { name: 'Library', url: '/library' },
    { name: 'Search', url: '/search' },
    { name: 'Knowledge Graph', url: '/graph' },
    { name: 'Classification', url: '/classification' },
    { name: 'Collections', url: '/collections' },
    { name: 'Profile', url: '/profile' },
  ],
  wcagLevel: 'AA', // AA or AAA
  rules: {
    // Enable/disable specific rules
    'color-contrast': { enabled: true },
    'html-has-lang': { enabled: true },
    'label': { enabled: true },
    'button-name': { enabled: true },
    'link-name': { enabled: true },
    'image-alt': { enabled: true },
    'aria-valid-attr': { enabled: true },
    'aria-required-attr': { enabled: true },
    'landmark-one-main': { enabled: true },
    'page-has-heading-one': { enabled: true },
    'region': { enabled: true },
  }
};

// Severity levels
const SEVERITY = {
  critical: 'critical',
  serious: 'serious',
  moderate: 'moderate',
  minor: 'minor'
};

// Create output directory if it doesn't exist
if (!fs.existsSync(CONFIG.outputDir)) {
  fs.mkdirSync(CONFIG.outputDir, { recursive: true });
}

/**
 * Run accessibility tests on a single page
 */
async function testPage(browser, pageConfig) {
  const page = await browser.newPage();
  
  try {
    console.log(`\n📄 Testing: ${pageConfig.name} (${pageConfig.url})`);
    
    // Navigate to page
    await page.goto(`${CONFIG.baseUrl}${pageConfig.url}`, {
      waitUntil: 'networkidle0',
      timeout: 30000
    });
    
    // Wait for content to load
    await page.waitForTimeout(2000);
    
    // Run axe accessibility tests
    const results = await new AxePuppeteer(page)
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();
    
    // Process results
    const summary = {
      page: pageConfig.name,
      url: pageConfig.url,
      timestamp: new Date().toISOString(),
      violations: results.violations.length,
      passes: results.passes.length,
      incomplete: results.incomplete.length,
      inapplicable: results.inapplicable.length,
      violationsBySeverity: {
        critical: results.violations.filter(v => v.impact === SEVERITY.critical).length,
        serious: results.violations.filter(v => v.impact === SEVERITY.serious).length,
        moderate: results.violations.filter(v => v.impact === SEVERITY.moderate).length,
        minor: results.violations.filter(v => v.impact === SEVERITY.minor).length,
      }
    };
    
    // Log summary
    console.log(`  ✅ Passes: ${summary.passes}`);
    console.log(`  ❌ Violations: ${summary.violations}`);
    if (summary.violations > 0) {
      console.log(`     - Critical: ${summary.violationsBySeverity.critical}`);
      console.log(`     - Serious: ${summary.violationsBySeverity.serious}`);
      console.log(`     - Moderate: ${summary.violationsBySeverity.moderate}`);
      console.log(`     - Minor: ${summary.violationsBySeverity.minor}`);
    }
    console.log(`  ⚠️  Incomplete: ${summary.incomplete}`);
    
    // Save detailed results
    const reportPath = path.join(
      CONFIG.outputDir,
      `${pageConfig.name.toLowerCase().replace(/\s+/g, '-')}-report.json`
    );
    fs.writeFileSync(reportPath, JSON.stringify({
      summary,
      violations: results.violations,
      passes: results.passes,
      incomplete: results.incomplete
    }, null, 2));
    
    return summary;
    
  } catch (error) {
    console.error(`  ❌ Error testing ${pageConfig.name}:`, error.message);
    return {
      page: pageConfig.name,
      url: pageConfig.url,
      error: error.message,
      violations: 0,
      passes: 0
    };
  } finally {
    await page.close();
  }
}

/**
 * Generate HTML report
 */
function generateHtmlReport(results) {
  const totalViolations = results.reduce((sum, r) => sum + r.violations, 0);
  const totalPasses = results.reduce((sum, r) => sum + r.passes, 0);
  const criticalIssues = results.reduce((sum, r) => 
    sum + (r.violationsBySeverity?.critical || 0), 0);
  const seriousIssues = results.reduce((sum, r) => 
    sum + (r.violationsBySeverity?.serious || 0), 0);
  
  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Accessibility Test Report - Neo Alexandria 2.0</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      line-height: 1.6;
      color: #333;
      background: #f5f5f5;
      padding: 20px;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      padding: 40px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
      color: #2c3e50;
      margin-bottom: 10px;
      font-size: 32px;
    }
    .timestamp {
      color: #7f8c8d;
      margin-bottom: 30px;
    }
    .summary {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-bottom: 40px;
    }
    .summary-card {
      padding: 20px;
      border-radius: 8px;
      text-align: center;
    }
    .summary-card.passes {
      background: #d4edda;
      border: 2px solid #28a745;
    }
    .summary-card.violations {
      background: #f8d7da;
      border: 2px solid #dc3545;
    }
    .summary-card.critical {
      background: #721c24;
      color: white;
      border: 2px solid #491217;
    }
    .summary-card.serious {
      background: #f8d7da;
      border: 2px solid #dc3545;
    }
    .summary-card h2 {
      font-size: 36px;
      margin-bottom: 5px;
    }
    .summary-card p {
      font-size: 14px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .page-results {
      margin-bottom: 30px;
    }
    .page-header {
      background: #ecf0f1;
      padding: 15px 20px;
      border-radius: 8px;
      margin-bottom: 15px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .page-header h3 {
      color: #2c3e50;
      font-size: 20px;
    }
    .page-header .url {
      color: #7f8c8d;
      font-size: 14px;
    }
    .page-stats {
      display: flex;
      gap: 20px;
      padding: 0 20px;
      margin-bottom: 15px;
    }
    .stat {
      display: flex;
      align-items: center;
      gap: 5px;
    }
    .stat.pass { color: #28a745; }
    .stat.fail { color: #dc3545; }
    .stat.warn { color: #ffc107; }
    .badge {
      display: inline-block;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: bold;
      text-transform: uppercase;
    }
    .badge.critical {
      background: #721c24;
      color: white;
    }
    .badge.serious {
      background: #dc3545;
      color: white;
    }
    .badge.moderate {
      background: #ffc107;
      color: #000;
    }
    .badge.minor {
      background: #17a2b8;
      color: white;
    }
    .status {
      display: inline-block;
      padding: 8px 16px;
      border-radius: 20px;
      font-weight: bold;
      font-size: 18px;
      margin-top: 20px;
    }
    .status.pass {
      background: #28a745;
      color: white;
    }
    .status.fail {
      background: #dc3545;
      color: white;
    }
    .footer {
      margin-top: 40px;
      padding-top: 20px;
      border-top: 1px solid #ecf0f1;
      text-align: center;
      color: #7f8c8d;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>🔍 Accessibility Test Report</h1>
    <p class="timestamp">Generated: ${new Date().toLocaleString()}</p>
    
    <div class="summary">
      <div class="summary-card passes">
        <h2>${totalPasses}</h2>
        <p>Passes</p>
      </div>
      <div class="summary-card violations">
        <h2>${totalViolations}</h2>
        <p>Violations</p>
      </div>
      <div class="summary-card critical">
        <h2>${criticalIssues}</h2>
        <p>Critical</p>
      </div>
      <div class="summary-card serious">
        <h2>${seriousIssues}</h2>
        <p>Serious</p>
      </div>
    </div>
    
    <h2>Page Results</h2>
    ${results.map(result => `
      <div class="page-results">
        <div class="page-header">
          <div>
            <h3>${result.page}</h3>
            <span class="url">${result.url}</span>
          </div>
        </div>
        <div class="page-stats">
          <span class="stat pass">✅ ${result.passes} passes</span>
          <span class="stat fail">❌ ${result.violations} violations</span>
          ${result.violationsBySeverity ? `
            ${result.violationsBySeverity.critical > 0 ? 
              `<span class="badge critical">${result.violationsBySeverity.critical} Critical</span>` : ''}
            ${result.violationsBySeverity.serious > 0 ? 
              `<span class="badge serious">${result.violationsBySeverity.serious} Serious</span>` : ''}
            ${result.violationsBySeverity.moderate > 0 ? 
              `<span class="badge moderate">${result.violationsBySeverity.moderate} Moderate</span>` : ''}
            ${result.violationsBySeverity.minor > 0 ? 
              `<span class="badge minor">${result.violationsBySeverity.minor} Minor</span>` : ''}
          ` : ''}
        </div>
      </div>
    `).join('')}
    
    <div style="text-align: center;">
      ${criticalIssues === 0 && seriousIssues === 0 ? 
        '<span class="status pass">✅ PASSED - No Critical or Serious Issues</span>' :
        '<span class="status fail">❌ FAILED - Critical or Serious Issues Found</span>'}
    </div>
    
    <div class="footer">
      <p>Neo Alexandria 2.0 - Automated Accessibility Testing</p>
      <p>Powered by axe-core | WCAG 2.1 Level ${CONFIG.wcagLevel}</p>
      <p>For detailed results, see individual JSON reports in the accessibility-reports directory</p>
    </div>
  </div>
</body>
</html>
  `;
  
  const reportPath = path.join(CONFIG.outputDir, 'index.html');
  fs.writeFileSync(reportPath, html);
  console.log(`\n📊 HTML report generated: ${reportPath}`);
}

/**
 * Main test runner
 */
async function runTests() {
  console.log('🚀 Starting Accessibility Tests...');
  console.log(`📍 Base URL: ${CONFIG.baseUrl}`);
  console.log(`📋 Testing ${CONFIG.pages.length} pages`);
  console.log(`📊 WCAG Level: ${CONFIG.wcagLevel}`);
  
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const results = [];
    
    // Test each page
    for (const pageConfig of CONFIG.pages) {
      const result = await testPage(browser, pageConfig);
      results.push(result);
    }
    
    // Generate reports
    generateHtmlReport(results);
    
    // Calculate overall results
    const totalViolations = results.reduce((sum, r) => sum + r.violations, 0);
    const criticalIssues = results.reduce((sum, r) => 
      sum + (r.violationsBySeverity?.critical || 0), 0);
    const seriousIssues = results.reduce((sum, r) => 
      sum + (r.violationsBySeverity?.serious || 0), 0);
    
    console.log('\n' + '='.repeat(60));
    console.log('📊 OVERALL RESULTS');
    console.log('='.repeat(60));
    console.log(`Total Violations: ${totalViolations}`);
    console.log(`Critical Issues: ${criticalIssues}`);
    console.log(`Serious Issues: ${seriousIssues}`);
    
    if (criticalIssues === 0 && seriousIssues === 0) {
      console.log('\n✅ PASSED - No critical or serious accessibility issues found!');
      process.exit(0);
    } else {
      console.log('\n❌ FAILED - Critical or serious accessibility issues found!');
      console.log('Please review the detailed reports and fix the issues.');
      process.exit(1);
    }
    
  } catch (error) {
    console.error('\n❌ Test execution failed:', error);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

// Run tests
runTests().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
