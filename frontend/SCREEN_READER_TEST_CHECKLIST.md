# Screen Reader Testing - Quick Checklist

This is a condensed checklist for quick screen reader testing sessions. For detailed instructions, see [SCREEN_READER_TESTING.md](./SCREEN_READER_TESTING.md).

## Pre-Test Setup

- [ ] Screen reader installed and running (NVDA/VoiceOver)
- [ ] Browser opened (Firefox/Chrome for NVDA, Safari for VoiceOver)
- [ ] Application loaded at homepage
- [ ] Volume at comfortable level
- [ ] Notepad ready for documenting issues

---

## Critical Path Tests (30 minutes)

### 1. Navigation & Skip Links (5 min)
- [ ] Tab to first element - skip link appears
- [ ] Skip to main content works
- [ ] Skip to navigation works
- [ ] All nav links announce correctly
- [ ] Current page indicated
- [ ] Mobile menu works (if applicable)

### 2. Search Flow (5 min)
- [ ] Search input labeled correctly
- [ ] Autocomplete suggestions announced
- [ ] Search results count announced
- [ ] Results are accessible
- [ ] Filters work and announce changes

### 3. Resource Management (10 min)
- [ ] Library page loads with announcement
- [ ] Resource cards announce all info
- [ ] Resource selection works
- [ ] Bulk actions accessible
- [ ] Upload modal accessible
- [ ] Upload progress announced
- [ ] Resource detail page complete

### 4. Forms & Validation (5 min)
- [ ] All inputs have labels
- [ ] Required fields indicated
- [ ] Error messages announced immediately
- [ ] Errors associated with fields
- [ ] Success messages announced
- [ ] Form submission works

### 5. Interactive Components (5 min)
- [ ] Modals announce and trap focus
- [ ] Buttons have clear labels
- [ ] Dropdowns accessible
- [ ] Checkboxes announce state
- [ ] Loading states announced
- [ ] Toasts/notifications announced

---

## Component Checklist

### Navigation
- [ ] Logo link labeled
- [ ] Nav items announce role and label
- [ ] Current page indicated
- [ ] Mobile menu toggle labeled
- [ ] Mobile menu accessible
- [ ] Close button labeled

### Buttons
- [ ] All buttons announce as "Button"
- [ ] Button text/label clear
- [ ] Disabled state announced
- [ ] Loading state announced
- [ ] Icon-only buttons have aria-label

### Forms
- [ ] All inputs have labels
- [ ] Required fields indicated
- [ ] Placeholder text announced
- [ ] Error messages have role="alert"
- [ ] Errors linked with aria-describedby
- [ ] Invalid fields have aria-invalid
- [ ] Success messages announced

### Modals
- [ ] Modal announced as "Dialog"
- [ ] Modal title announced
- [ ] Focus moves to modal
- [ ] Focus trapped in modal
- [ ] Escape closes modal
- [ ] Focus returns on close
- [ ] Close button labeled

### Cards & Lists
- [ ] Lists announced with count
- [ ] List items numbered
- [ ] Card content in logical order
- [ ] Headings used for titles
- [ ] Metadata clearly announced
- [ ] Action buttons accessible

### Data Visualizations
- [ ] Graphs have text alternatives
- [ ] Chart data accessible
- [ ] Descriptions provided
- [ ] Interactive elements accessible
- [ ] Tooltips announced

### Loading States
- [ ] Loading announced (role="status")
- [ ] Progress updates announced
- [ ] Completion announced
- [ ] Skeleton loaders don't confuse

### Notifications
- [ ] Toasts announced immediately
- [ ] Success: polite announcement
- [ ] Error: assertive announcement
- [ ] Dismissible with keyboard
- [ ] Dismissal announced

---

## Keyboard Navigation Tests

### Global Shortcuts
- [ ] Alt + H → Home
- [ ] Alt + L → Library
- [ ] Alt + S → Search
- [ ] Alt + G → Knowledge Graph
- [ ] Alt + C → Collections
- [ ] Alt + P → Profile
- [ ] Ctrl/Cmd + K → Quick search
- [ ] ? → Help dialog

### Standard Navigation
- [ ] Tab moves forward
- [ ] Shift + Tab moves backward
- [ ] Enter activates buttons/links
- [ ] Space activates buttons/checkboxes
- [ ] Escape closes modals/dropdowns
- [ ] Arrow keys navigate lists/menus

---

## NVDA Specific Tests

### Browse Mode Navigation
- [ ] H - Navigate by heading
- [ ] K - Navigate by link
- [ ] B - Navigate by button
- [ ] F - Navigate by form field
- [ ] D - Navigate by landmark
- [ ] NVDA + F7 - Elements list

### Announcements
- [ ] Page title announced on load
- [ ] Landmarks announced
- [ ] Headings announce level
- [ ] Links announce destination
- [ ] Buttons announce role
- [ ] Form fields announce type

---

## VoiceOver Specific Tests

### Rotor Navigation
- [ ] VO + U opens rotor
- [ ] Headings list accessible
- [ ] Links list accessible
- [ ] Form controls list accessible
- [ ] Landmarks list accessible

### Announcements
- [ ] Page title announced on load
- [ ] Landmarks announced
- [ ] Headings announce level
- [ ] Links announce destination
- [ ] Buttons announce role
- [ ] Form fields announce type

---

## Common Issues to Check

### Content Issues
- [ ] No unlabeled buttons
- [ ] No unlabeled form fields
- [ ] No missing alt text
- [ ] No empty links
- [ ] No duplicate IDs

### Structure Issues
- [ ] Logical heading hierarchy
- [ ] Proper landmark usage
- [ ] Correct semantic HTML
- [ ] Logical reading order
- [ ] No layout tables

### Interaction Issues
- [ ] All interactive elements keyboard accessible
- [ ] Focus visible on all elements
- [ ] Focus order logical
- [ ] No keyboard traps
- [ ] Modals trap focus properly

### Dynamic Content Issues
- [ ] Live regions for updates
- [ ] Loading states announced
- [ ] Error messages announced
- [ ] Success messages announced
- [ ] Status changes announced

---

## Quick Issue Template

```
Component: [Name]
Issue: [Brief description]
Severity: [Critical/High/Medium/Low]
Steps:
1. [Step 1]
2. [Step 2]
Expected: [What should happen]
Actual: [What actually happens]
Fix: [Suggested solution]
```

---

## Test Session Template

```
Date: [Date]
Tester: [Name]
Screen Reader: [NVDA/VoiceOver] [Version]
Browser: [Name] [Version]
Duration: [Time]

Tests Completed: [X/Y]
Issues Found: [Number]
Critical Issues: [Number]

Notes:
- [Note 1]
- [Note 2]

Next Steps:
- [Action 1]
- [Action 2]
```

---

## Priority Levels

### P0 - Critical (Fix Immediately)
- Content completely inaccessible
- Keyboard trap preventing navigation
- Form submission impossible
- Critical errors not announced

### P1 - High (Fix Soon)
- Important content difficult to access
- Confusing navigation
- Missing labels on key elements
- Form validation unclear

### P2 - Medium (Fix When Possible)
- Minor labeling issues
- Suboptimal reading order
- Missing descriptions
- Inconsistent patterns

### P3 - Low (Nice to Have)
- Enhancement opportunities
- Additional context helpful
- Improved efficiency possible
- Better user experience

---

## Resources

- **Detailed Guide**: [SCREEN_READER_TESTING.md](./SCREEN_READER_TESTING.md)
- **Accessibility Docs**: [ACCESSIBILITY.md](./ACCESSIBILITY.md)
- **NVDA Download**: https://www.nvaccess.org/download/
- **ARIA Practices**: https://www.w3.org/WAI/ARIA/apg/
- **WebAIM**: https://webaim.org/

---

## Quick Tips

### NVDA
- Use Firefox or Chrome
- Toggle browse/focus mode: NVDA + Space
- Stop reading: Ctrl
- Read all: NVDA + Down Arrow

### VoiceOver
- Use Safari
- VO key: Ctrl + Option
- Stop reading: Ctrl
- Read all: VO + A
- Web rotor: VO + U

### General
- Test with eyes closed when possible
- Test all interactions, not just reading
- Document issues immediately
- Take screenshots/recordings
- Test on actual devices when possible
