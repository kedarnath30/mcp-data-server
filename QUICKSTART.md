# 🚀 DashAI V6 - Quick Start Guide

## Installation (2 minutes)

### Windows
```bash
# Navigate to project directory
cd C:\Users\kedar\mcp-data-server

# Run installer
install_enhanced.bat

# OR manually:
pip install -r requirements_enhanced.txt
```

### Mac/Linux
```bash
cd ~/mcp-data-server
pip install -r requirements_enhanced.txt
```

---

## Running the App (1 command)

```bash
streamlit run dashboard_ai_enhanced.py
```

The app will open in your browser at `http://localhost:8501`

---

## Your First Dashboard (60 seconds)

### Step 1: Upload Data (10 sec)
- Drag & drop your `verizon_mobile_dashboard.xlsx`
- ✓ See data preview

### Step 2: Pick a Template (5 sec)
- Click **👔 Executive** button
- Prompt auto-fills

### Step 3: Generate (30 sec)
- Click **"🚀 Generate Custom Dashboard"**
- Watch progress bar
- Dashboard appears!

### Step 4: Customize & Export (15 sec)
- Sidebar → Change color scheme to "Blues"
- Click **"📥 Export to PDF"**
- Download and open!

---

## Quick Feature Tour

### 💡 Templates
**Location**: Step 3  
**Use**: Click any emoji button (👔 📈 🎯 ⚙️ 💰 👥)  
**Result**: Instant professional prompt

### 🎨 Styling
**Location**: Sidebar → "🎨 Chart Styling"  
**Options**: 
- Color Palette (7 options)
- Chart Height (slider)
- Gridlines (toggle)

### 💾 Save & Load
**Save**: Click "💾 Save Dashboard" button  
**Load**: Sidebar → "📚 Saved Dashboards" → Click name  
**Delete**: Click 🗑️ next to saved dashboard

### 📥 Export
**Buttons**: Top of dashboard view  
**Options**:
- 📥 PDF → For reports
- 📊 PowerPoint → For presentations  
- 📄 JSON → For sharing config

### ✅ Validation
**Location**: Data preview section  
**Shows**: Missing values, duplicates, outliers, etc.

---

## Common Tasks

### Create Marketing Dashboard
```
1. Upload data
2. Click "🎯 Marketing" template
3. Generate
4. Done!
```

### Weekly Report Automation
```
1. Generate dashboard once
2. Save it ("💾 Save Dashboard")
3. Each week:
   - Upload new data
   - Load saved dashboard
   - Export PDF
```

### Custom Colors for Brand
```
1. Generate dashboard
2. Sidebar → "🎨 Chart Styling"
3. Select color matching brand
4. Export
```

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Focus search | `/` |
| Rerun app | `R` |
| Clear cache | `C` |

---

## Troubleshooting

### "API rate limit reached"
**Solution**: Wait 30-60 seconds, then retry

### Charts not showing
**Solution**: Check "View Code & Error" expander

### Can't find saved dashboard
**Solution**: Dashboards clear on refresh. Export as JSON to preserve.

---

## Pro Tips

1. **Start with templates** - Customize from there
2. **Save early, save often** - Export JSON for backup
3. **Check validation** - Fix data issues before generating
4. **Use filters** - Sidebar slicers work on all charts
5. **Adjust for audience** - Change colors for different stakeholders

---

## Next Level

### Reusable Templates
1. Create base dashboard
2. Save with descriptive name
3. Load and modify for specific needs

### Data Quality First
1. Upload data
2. Check validation warnings
3. Fix issues
4. Re-upload
5. Generate with confidence

### Presentation Ready
1. Generate dashboard
2. Customize colors to match slides
3. Export PowerPoint
4. Open and present!

---

## Getting Help

1. Check `FEATURES_V6.md` for detailed docs
2. See `IMPLEMENTATION_SUMMARY.md` for overview
3. Review error messages in app
4. Check console for technical details

---

## What's New in V6

✨ **6 one-click templates**  
📥 **PDF & PowerPoint export**  
💾 **Save/load system**  
✅ **Data validation**  
🎨 **Chart customization**  
⚡ **Better loading & errors**

---

**Ready? Let's go!** 🚀

```bash
streamlit run dashboard_ai_enhanced.py
```
