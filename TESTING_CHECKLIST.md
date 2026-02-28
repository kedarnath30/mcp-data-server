# 🧪 DashAI V6 - Testing Checklist

## Pre-Launch Testing Checklist

Use this checklist to verify all features work correctly before deployment.

---

## ✅ Installation & Setup

- [ ] Dependencies install successfully
  ```bash
  pip install -r requirements_enhanced.txt
  ```
- [ ] `.env` file exists with valid API key
- [ ] App launches without errors
  ```bash
  streamlit run dashboard_ai_enhanced.py
  ```
- [ ] Browser opens to `localhost:8501`
- [ ] No console errors in terminal

---

## ✅ Step 1: Upload Data

### Single File Upload
- [ ] Upload single CSV file
- [ ] Upload single Excel file (.xlsx)
- [ ] Upload single Excel file (.xls)
- [ ] Data preview shows correctly
- [ ] Column info table displays
- [ ] Row/column counts match file

### Multiple File Upload
- [ ] Upload 2 CSV files
- [ ] Upload 2 Excel files
- [ ] Upload mixed (CSV + Excel)
- [ ] Files merge correctly on shared columns
- [ ] All sheets from Excel files load
- [ ] Combined row count is correct

### Data Quality Validation
- [ ] Validation panel appears
- [ ] Missing values detected (if present)
- [ ] Duplicates counted (if present)
- [ ] Outliers identified (if present)
- [ ] Severity colors correct (warning = yellow, info = blue)
- [ ] Details expandable and readable

### Error Handling
- [ ] Invalid file format shows error
- [ ] Corrupted file handled gracefully
- [ ] Empty file shows appropriate message
- [ ] Large file (>100MB) loads or shows warning

---

## ✅ Step 2: Ask Questions

### Natural Language Query
- [ ] Type question in input box
- [ ] Click "🔍 Ask" button
- [ ] Loading spinner shows
- [ ] Answer appears with real numbers
- [ ] Insight box shows business context
- [ ] Chart renders correctly
- [ ] "View Code" expander works
- [ ] Code is syntactically correct

### Query History
- [ ] Query added to history
- [ ] History shows last 5 queries
- [ ] Timestamps display correctly
- [ ] History panel is expandable

### Error Cases
- [ ] Empty question shows warning
- [ ] API error shows user-friendly message
- [ ] Rate limit error detected and messaged
- [ ] Chart error shows in expander

---

## ✅ Step 3: Generate Dashboard

### Quick Templates
- [ ] 6 template buttons visible (👔 📈 🎯 ⚙️ 💰 👥)
- [ ] Each button has correct label
- [ ] Clicking template fills prompt area
- [ ] Prompt text is editable
- [ ] Clear button resets prompt
- [ ] Different templates have unique content

### Custom Dashboard Generation
- [ ] Type custom description
- [ ] Click "Generate Custom Dashboard"
- [ ] Progress bar shows (0-100%)
- [ ] Dashboard generates within 60 seconds
- [ ] Dashboard title displays
- [ ] Dashboard description displays

### Dashboard Content
- [ ] KPIs render (3-4 typically)
- [ ] KPI values are actual numbers, not "Error"
- [ ] KPI formatting correct ($, %, etc.)
- [ ] Insights section shows 2-3 items
- [ ] Visualizations render (4-6 typically)
- [ ] Charts are interactive (zoom, pan, hover)
- [ ] Chart insights appear below charts

### Error Handling
- [ ] Empty prompt shows warning
- [ ] Parse error shows helpful message
- [ ] Code execution error shows debug panel
- [ ] API error handled gracefully

---

## ✅ Dashboard Customization

### Sidebar Filters
- [ ] Sidebar opens (click ≡ button)
- [ ] Filter columns detected automatically
- [ ] Multiselect dropdowns work
- [ ] Selecting filter updates all charts
- [ ] Active filter count shows
- [ ] Clear filters button works
- [ ] Row count updates with filtering

### Chart Styling
- [ ] "🎨 Chart Styling" expander opens
- [ ] Color palette dropdown has 7 options
- [ ] Changing color updates all charts
- [ ] Chart height slider works (300-800px)
- [ ] Height change applies to all charts
- [ ] Gridlines toggle works
- [ ] Settings persist during session

---

## ✅ Export Features

### PDF Export
- [ ] Click "📥 Export to PDF" button
- [ ] Loading spinner shows
- [ ] Download button appears
- [ ] Downloaded PDF opens
- [ ] PDF contains:
  - [ ] Dashboard title
  - [ ] KPIs in table
  - [ ] Insights as bullets
  - [ ] Visualization descriptions
- [ ] PDF is readable and formatted

### PowerPoint Export
- [ ] Click "📊 Export to PowerPoint" button
- [ ] Loading spinner shows
- [ ] Download button appears
- [ ] Downloaded PPTX opens
- [ ] PPTX contains:
  - [ ] Title slide
  - [ ] KPI slide with cards
  - [ ] Insights slide
  - [ ] Chart slides with titles
- [ ] PPTX is editable

### JSON Export
- [ ] Click "📄 Download JSON" button
- [ ] JSON file downloads
- [ ] JSON is valid (can be opened)
- [ ] JSON contains complete dashboard config
- [ ] Can be re-imported (future feature)

---

## ✅ Save/Load Features

### Save Dashboard
- [ ] Click "💾 Save Dashboard" button
- [ ] Success message shows
- [ ] Dashboard appears in sidebar
- [ ] Timestamp is correct
- [ ] Name matches dashboard title

### Load Dashboard
- [ ] Sidebar shows "📚 Saved Dashboards"
- [ ] Saved dashboard listed
- [ ] Click saved dashboard
- [ ] Dashboard loads correctly
- [ ] All charts render
- [ ] Settings preserved

### Delete Dashboard
- [ ] Click 🗑️ button next to saved dashboard
- [ ] Dashboard removed from list
- [ ] No error shown

### Clear All
- [ ] Click "🗑️ Clear All Saved"
- [ ] Confirmation (implicit)
- [ ] All dashboards removed
- [ ] Empty state shows

---

## ✅ Step 4: Preset Dashboards

### Generation
- [ ] Click "📊 Generate 5 Role-Based Dashboards"
- [ ] Progress bar shows
- [ ] 5 dashboards generated
- [ ] Success message shows count
- [ ] Dashboard cards display

### Dashboard Cards
- [ ] Each card shows:
  - [ ] Icon (👔 📈 🎯 ⚙️ 💰)
  - [ ] Name (Executive, Sales, etc.)
  - [ ] Audience description
  - [ ] Description text
- [ ] "Select" button on each card

### Selection
- [ ] Click "Select" on any dashboard
- [ ] Dashboard loads and renders
- [ ] Can customize after loading
- [ ] Can save selected dashboard

### Regeneration
- [ ] Click "🔄 Regenerate All"
- [ ] Returns to selection screen
- [ ] Can generate new set

---

## ✅ User Experience

### Loading States
- [ ] File upload shows progress
- [ ] Dashboard generation shows progress (0-100%)
- [ ] Each KPI shows "Computing..." spinner
- [ ] Each chart shows "Generating..." spinner
- [ ] Exports show "Generating..." message

### Error Messages
- [ ] API errors show specific message
- [ ] Rate limit shows time-based message
- [ ] Parse errors suggest simpler prompt
- [ ] Code errors show in expander with details

### Visual Polish
- [ ] Icons display correctly (📊 💡 🎯 etc.)
- [ ] Colors are consistent
- [ ] Spacing is appropriate
- [ ] Text is readable
- [ ] Buttons are clearly clickable

---

## ✅ Performance

### Speed Tests
- [ ] File upload: <5 seconds (10MB file)
- [ ] Dashboard generation: 20-40 seconds
- [ ] Chart rendering: <2 seconds per chart
- [ ] PDF export: 5-10 seconds
- [ ] PPTX export: 5-10 seconds
- [ ] Save dashboard: <1 second
- [ ] Load dashboard: <2 seconds

### Resource Usage
- [ ] Memory usage reasonable (<500MB)
- [ ] CPU usage spikes during generation only
- [ ] No memory leaks (check after 30 min use)
- [ ] Browser responsive throughout

---

## ✅ Edge Cases

### Data Edge Cases
- [ ] Empty dataset handled
- [ ] Single row dataset works
- [ ] Single column dataset works
- [ ] All null values in column handled
- [ ] Very large numbers formatted correctly
- [ ] Very small numbers formatted correctly
- [ ] Special characters in column names handled

### UI Edge Cases
- [ ] Very long dashboard title wraps
- [ ] Very long insight text wraps
- [ ] Many KPIs (6+) layout works
- [ ] Many charts (10+) layout works
- [ ] Very wide screen renders well
- [ ] Very narrow screen usable

### Session Edge Cases
- [ ] Refresh page (session clears - expected)
- [ ] Multiple tabs (independent sessions)
- [ ] Back button (handled gracefully)
- [ ] Network disconnect during generation

---

## ✅ Browser Compatibility

### Desktop Browsers
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

### Mobile (Basic Check)
- [ ] Works on mobile Chrome
- [ ] Works on mobile Safari
- [ ] UI is usable (not optimal, but functional)

---

## ✅ Accessibility

### Keyboard Navigation
- [ ] Tab through inputs
- [ ] Enter to submit forms
- [ ] Expanders toggle with keyboard

### Screen Reader (Basic)
- [ ] Buttons have labels
- [ ] Form inputs have labels
- [ ] Error messages announced

---

## ✅ Security

### Input Validation
- [ ] SQL injection attempts rejected
- [ ] XSS attempts sanitized
- [ ] File path traversal blocked
- [ ] Large file sizes handled

### API Key
- [ ] API key not exposed in UI
- [ ] API key not in console logs
- [ ] API key read from .env only

---

## ✅ Documentation

### Files Present
- [ ] README_V6.md exists and complete
- [ ] FEATURES_V6.md exists and complete
- [ ] QUICKSTART.md exists and complete
- [ ] IMPLEMENTATION_SUMMARY.md exists
- [ ] V5_VS_V6_COMPARISON.md exists
- [ ] requirements_enhanced.txt exists

### Documentation Quality
- [ ] Installation steps clear
- [ ] Screenshots/examples present
- [ ] Troubleshooting section helpful
- [ ] Feature descriptions accurate

---

## ✅ Deployment Readiness

### Pre-Deployment
- [ ] All tests passed
- [ ] No console errors
- [ ] No deprecation warnings
- [ ] All dependencies listed
- [ ] .env.example created
- [ ] README updated

### Production Considerations
- [ ] API key in .env (not hardcoded)
- [ ] Error handling robust
- [ ] User feedback clear
- [ ] Performance acceptable
- [ ] Security reviewed

---

## 🎯 Test Scenarios

### Scenario 1: First-Time User
```
1. Install dependencies ✓
2. Add API key ✓
3. Run app ✓
4. Upload sample data ✓
5. Click Executive template ✓
6. Generate dashboard ✓
7. Export PDF ✓
Total time: <5 minutes
Experience: Smooth
```

### Scenario 2: Power User
```
1. Upload data ✓
2. Generate 3 different dashboards ✓
3. Save all 3 ✓
4. Customize each with different colors ✓
5. Export all as PDF and PPTX ✓
6. Load and modify one ✓
Total time: <15 minutes
Experience: Productive
```

### Scenario 3: Error Recovery
```
1. Upload data ✓
2. Hit rate limit ✓
3. See clear error message ✓
4. Wait 60 seconds ✓
5. Retry successfully ✓
Experience: Frustration-free
```

---

## 📊 Test Results Template

### Test Date: __________
### Tester: __________
### Environment: __________

| Category | Pass | Fail | Notes |
|----------|------|------|-------|
| Installation | ☐ | ☐ | |
| Upload | ☐ | ☐ | |
| Questions | ☐ | ☐ | |
| Templates | ☐ | ☐ | |
| Generation | ☐ | ☐ | |
| Customization | ☐ | ☐ | |
| Export | ☐ | ☐ | |
| Save/Load | ☐ | ☐ | |
| Presets | ☐ | ☐ | |
| Performance | ☐ | ☐ | |
| Edge Cases | ☐ | ☐ | |

**Overall**: Pass ☐ / Fail ☐

**Critical Issues**: __________

**Minor Issues**: __________

**Recommendations**: __________

---

## 🚀 Sign-Off

**Tested By**: __________  
**Date**: __________  
**Version**: 6.0.0  
**Status**: Ready for Production ☐ / Needs Work ☐

**Notes**: __________

---

## 📝 Known Limitations (Expected)

- [ ] Session storage clears on refresh (by design)
- [ ] Chart images not in PDF/PPTX (future feature)
- [ ] Saved dashboards not persistent (by design for V6)
- [ ] Rate limits apply (Anthropic API)

These are expected and documented. Not bugs.

---

**Happy Testing!** 🎉
