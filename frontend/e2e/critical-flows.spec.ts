import { test, expect } from '@playwright/test';

test.describe('Critical User Journeys', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('Upload and resource management flow', async ({ page }) => {
    // Navigate to upload
    await page.click('text=Upload');
    
    // Upload a file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'test.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('test content'),
    });

    // Wait for upload to complete
    await expect(page.locator('text=Upload complete')).toBeVisible({ timeout: 10000 });

    // Navigate to resources
    await page.click('text=Resources');
    
    // Verify resource appears
    await expect(page.locator('text=test.pdf')).toBeVisible();

    // Click on resource to view details
    await page.click('text=test.pdf');
    
    // Verify detail page loads
    await expect(page.locator('role=heading[name="test.pdf"]')).toBeVisible();
  });

  test('Search and discovery flow', async ({ page }) => {
    // Use global search
    await page.click('[placeholder*="Search"]');
    await page.fill('[placeholder*="Search"]', 'machine learning');
    await page.press('[placeholder*="Search"]', 'Enter');

    // Wait for results
    await expect(page.locator('text=results')).toBeVisible({ timeout: 5000 });

    // Verify results are displayed
    const results = page.locator('[data-testid="search-result"]');
    await expect(results.first()).toBeVisible();

    // Click on a result
    await results.first().click();

    // Verify detail page loads
    await expect(page.locator('[data-testid="resource-detail"]')).toBeVisible();
  });

  test('Collection management flow', async ({ page }) => {
    // Navigate to collections
    await page.click('text=Collections');

    // Create new collection
    await page.click('text=New Collection');
    await page.fill('[placeholder*="Collection name"]', 'Test Collection');
    await page.click('text=Create');

    // Verify collection created
    await expect(page.locator('text=Test Collection')).toBeVisible();

    // Click on collection
    await page.click('text=Test Collection');

    // Verify collection detail page
    await expect(page.locator('role=heading[name="Test Collection"]')).toBeVisible();

    // Add resource to collection
    await page.click('text=Add Resources');
    await page.fill('[placeholder*="Search"]', 'test');
    await page.click('[data-testid="add-resource-button"]').first();

    // Verify resource added
    await expect(page.locator('text=Resource added')).toBeVisible();
  });

  test('Annotation workflow', async ({ page }) => {
    // Navigate to a resource
    await page.click('text=Resources');
    await page.locator('[data-testid="resource-card"]').first().click();

    // Switch to annotations tab
    await page.click('text=Annotations');

    // Create highlight
    await page.click('[data-testid="pdf-viewer"]');
    // Simulate text selection (simplified)
    await page.evaluate(() => {
      const selection = window.getSelection();
      const range = document.createRange();
      const textNode = document.querySelector('[data-testid="pdf-text"]');
      if (textNode?.firstChild) {
        range.selectNodeContents(textNode.firstChild);
        selection?.removeAllRanges();
        selection?.addRange(range);
      }
    });

    // Click highlight button
    await page.click('[data-testid="highlight-button"]');

    // Add note
    await page.fill('[placeholder*="Add a note"]', 'This is an important point');
    await page.click('text=Save');

    // Verify annotation created
    await expect(page.locator('text=This is an important point')).toBeVisible();
  });

  test('Graph exploration', async ({ page }) => {
    // Navigate to graph
    await page.click('text=Graph');

    // Wait for graph to load
    await expect(page.locator('[data-testid="graph-canvas"]')).toBeVisible({ timeout: 10000 });

    // Verify nodes are rendered
    const nodes = page.locator('[data-testid="graph-node"]');
    await expect(nodes.first()).toBeVisible();

    // Click on a node
    await nodes.first().click();

    // Verify node details appear
    await expect(page.locator('[data-testid="node-details"]')).toBeVisible();

    // Test zoom controls
    await page.click('[data-testid="zoom-in"]');
    await page.click('[data-testid="zoom-out"]');
    await page.click('[data-testid="reset-zoom"]');
  });

  test('Keyboard navigation', async ({ page }) => {
    // Test command palette
    await page.keyboard.press('Control+K');
    await expect(page.locator('[data-testid="command-palette"]')).toBeVisible();
    await page.keyboard.press('Escape');

    // Test tab navigation
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Verify focus is visible
    const focused = page.locator(':focus');
    await expect(focused).toBeVisible();
  });

  test('Accessibility compliance', async ({ page }) => {
    // Check for ARIA labels
    const buttons = page.locator('button');
    const count = await buttons.count();
    
    for (let i = 0; i < Math.min(count, 10); i++) {
      const button = buttons.nth(i);
      const ariaLabel = await button.getAttribute('aria-label');
      const text = await button.textContent();
      
      // Button should have either aria-label or text content
      expect(ariaLabel || text).toBeTruthy();
    }

    // Check for proper heading hierarchy
    const h1 = page.locator('h1');
    await expect(h1).toHaveCount(1);
  });

  test('Performance metrics', async ({ page }) => {
    // Navigate to page
    await page.goto('/');

    // Get performance metrics
    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        ttfb: navigation.responseStart - navigation.requestStart,
      };
    });

    // Verify performance budgets
    expect(metrics.ttfb).toBeLessThan(600);
    expect(metrics.domContentLoaded).toBeLessThan(2000);
  });
});
