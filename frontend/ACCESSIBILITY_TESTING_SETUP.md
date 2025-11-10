# Accessibility Testing Setup Guide

This guide explains how to set up and run accessibility tests for the Neo Alexandria 2.0 frontend application.

## Overview

The application includes comprehensive accessibility testing tools:

1. **Automated Testing** - Using axe-core and Puppeteer
2. **Manual Testing** - Screen reader testing with NVDA and VoiceOver
3. **Browser Extensions** - axe DevTools, WAVE, Lighthouse

---

## Automated Testing

### Prerequisites

Install the required dependencies:

```bash
npm install --save-dev @axe-core/puppeteer puppeteer
```

### Running Automated Tests

1. **Start the development server**:
   ```bash
   npm run dev
   ```

2. **In a new terminal, run the accessibility tests**:
   ```bash
   node accessibility-test.js
   ```

3. **View the results**:
   - HTML report: `accessibility-reports/index.html`
   - Detailed JSON reports: `accessibility-reports/*.json`

### Configuration

Edit `accessibility-test.js` to customize:

- **Base URL**: Change `CONFIG.baseUrl` to test different environments
- **Pages**: Add/remove pages in `CONFIG.pages` array
- **WCAG Level**: Set `CONFIG.wcagLevel` to 'AA' or 'AAA'
- **Rules**: Enable/disable specific accessibility rules

### CI/CD Integration

Add to your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run Accessibility Tests
  run: |
    npm run dev &
    sleep 10
    node accessibility-test.js
```

---

## Manual Screen Reader Testing

### NVDA (Windows)

#### Installation

1. Download from [nvaccess.org](https://www.nvaccess.org/download/)
2. Run installer and follow setup wizard
3. Restart computer (optional but recommended)

#### Quick Start

1. **Start NVDA**: `Ctrl + Alt + N`
2. **Open application** in Firefox or Chrome
3. **Navigate with**:
   - `Tab` - Next element
   - `Shift + Tab` - Previous element
   - `H` - Next heading
   - `K` - Next link
   - `B` - Next button
   - `F` - Next form field

4. **Stop reading**: `Ctrl`

#### Detailed Testing

See [SCREEN_READER_TESTING.md](./SCREEN_READER_TESTING.md) for comprehensive test scenarios.

### VoiceOver (macOS)

#### Activation

1. **Enable VoiceOver**: `Cmd + F5`
2. **Open application** in Safari
3. **Navigate with**:
   - `VO + Right Arrow` - Next element (VO = Ctrl + Option)
   - `VO + Left Arrow` - Previous element
   - `VO + Cmd + H` - Next heading
   - `VO + Cmd + L` - Next link

4. **Stop reading**: `Ctrl`

#### Detailed Testing

See [SCREEN_READER_TESTING.md](./SCREEN_READER_TESTING.md) for comprehensive test scenarios.

### Quick Checklist

Use [SCREEN_READER_TEST_CHECKLIST.md](./SCREEN_READER_TEST_CHECKLIST.md) for rapid testing sessions.

### Documenting Results

Use [SCREEN_READER_TEST_RESULTS_TEMPLATE.md](./SCREEN_READER_TEST_RESULTS_TEMPLATE.md) to document your findings.

---

## Browser Extensions

### axe DevTools

1. **Install**: [Chrome](https://chrome.google.com/webstore/detail/axe-devtools-web-accessib/lhdoppojpmngadmnindnejefpokejbdd) | [Firefox](https://addons.mozilla.org/en-US/firefox/addon/axe-devtools/)
2. **Open DevTools**: `F12`
3. **Navigate to axe DevTools tab**
4. **Click "Scan ALL of my page"**
5. **Review issues** by severity

### WAVE

1. **Install**: [Chrome](https://chrome.google.com/webstore/detail/wave-evaluation-tool/jbbplnpkjmmeebjpijfedlgcdilocofh) | [Firefox](https://addons.mozilla.org/en-US/firefox/addon/wave-accessibility-tool/)
2. **Click WAVE icon** in browser toolbar
3. **Review** color-coded issues on page
4. **Check** summary panel for details

### Lighthouse

1. **Open DevTools**: `F12`
2. **Navigate to Lighthouse tab**
3. **Select "Accessibility" category**
4. **Click "Generate report"**
5. **Review** score and recommendations

---

## Testing Workflow

### Development Phase

1. **During development**:
   - Use axe DevTools to check each component
   - Test keyboard navigation continuously
   - Verify focus indicators are visible

2. **Before committing**:
   - Run automated tests: `node accessibility-test.js`
   - Fix any critical or serious issues
   - Document any known issues

### Pre-Release Testing

1. **Automated testing**:
   - Run full test suite
   - Generate reports
   - Review all violations

2. **Manual testing**:
   - Complete screen reader testing (NVDA + VoiceOver)
   - Test all critical user flows
   - Document results

3. **Browser extension testing**:
   - Run axe DevTools on all pages
   - Run WAVE on all pages
   - Run Lighthouse accessibility audit

### Continuous Testing

1. **Weekly**:
   - Run automated tests
   - Spot-check with screen reader

2. **Monthly**:
   - Full screen reader testing session
   - Review and update test documentation

3. **Per release**:
   - Complete accessibility audit
   - Document compliance level
   - Update accessibility statement

---

## Common Issues and Fixes

### Issue: Missing ARIA Labels

**Detection**: Automated tests report "button-name" or "link-name" violations

**Fix**:
```jsx
// Before
<button><Icon /></button>

// After
<button aria-label="Close modal"><Icon /></button>
```

### Issue: Form Inputs Without Labels

**Detection**: Automated tests report "label" violations

**Fix**:
```jsx
// Before
<input type="text" placeholder="Search" />

// After
<label htmlFor="search">Search</label>
<input id="search" type="text" placeholder="Search" />
```

### Issue: Low Color Contrast

**Detection**: Automated tests report "color-contrast" violations

**Fix**:
- Use color contrast checker tool
- Ensure minimum 4.5:1 ratio for normal text
- Ensure minimum 3:1 ratio for large text

### Issue: Missing Alt Text

**Detection**: Automated tests report "image-alt" violations

**Fix**:
```jsx
// Before
<img src="logo.png" />

// After - Informative image
<img src="logo.png" alt="Neo Alexandria logo" />

// After - Decorative image
<img src="decoration.png" alt="" aria-hidden="true" />
```

### Issue: Keyboard Trap

**Detection**: Manual testing - cannot Tab out of component

**Fix**:
- Implement proper focus management
- Ensure Escape key closes modals
- Return focus to trigger element

### Issue: Dynamic Content Not Announced

**Detection**: Screen reader doesn't announce updates

**Fix**:
```jsx
// Add live region
<div role="status" aria-live="polite" aria-atomic="true">
  {statusMessage}
</div>

// For critical alerts
<div role="alert">
  {errorMessage}
</div>
```

---

## Accessibility Checklist

### Before Each Release

- [ ] All automated tests pass
- [ ] No critical or serious violations
- [ ] Screen reader testing completed (NVDA + VoiceOver)
- [ ] All forms tested with screen reader
- [ ] All modals tested with screen reader
- [ ] Keyboard navigation works throughout
- [ ] Focus indicators visible on all elements
- [ ] Color contrast meets WCAG AA standards
- [ ] All images have appropriate alt text
- [ ] All buttons and links have accessible names
- [ ] Loading states announced properly
- [ ] Error messages announced properly
- [ ] Success messages announced properly
- [ ] Documentation updated

---

## Resources

### Documentation
- [ACCESSIBILITY.md](./ACCESSIBILITY.md) - Main accessibility documentation
- [SCREEN_READER_TESTING.md](./SCREEN_READER_TESTING.md) - Detailed screen reader testing guide
- [SCREEN_READER_TEST_CHECKLIST.md](./SCREEN_READER_TEST_CHECKLIST.md) - Quick testing checklist
- [SCREEN_READER_TEST_RESULTS_TEMPLATE.md](./SCREEN_READER_TEST_RESULTS_TEMPLATE.md) - Results template

### External Resources
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Resources](https://webaim.org/resources/)
- [axe-core Documentation](https://github.com/dequelabs/axe-core)
- [NVDA User Guide](https://www.nvaccess.org/files/nvda/documentation/userGuide.html)
- [VoiceOver User Guide](https://support.apple.com/guide/voiceover/welcome/mac)

### Tools
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WAVE](https://wave.webaim.org/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [Color Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [NVDA](https://www.nvaccess.org/)

---

## Support

For accessibility questions or issues:

1. Review the documentation in this directory
2. Check the [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
3. Consult the [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
4. Contact the development team

---

## Compliance Statement

Neo Alexandria 2.0 aims to meet WCAG 2.1 Level AA compliance. We continuously test and improve accessibility to ensure all users can effectively use the application.

Last Updated: [Current Date]
