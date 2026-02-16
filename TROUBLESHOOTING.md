# Dashboard Troubleshooting Guide

## Quick Fix Steps

### Step 1: Run the Debug Script

```bash
python debug_excel.py
```

This will show you:
- ✓ Current directory
- ✓ Excel files found
- ✓ What's wrong with the file
- ✓ How to fix it

### Step 2: Check Common Issues

#### Issue 1: File not in the right location

**Problem:** Dashboard looks for file in `/home/claude/` but you're in a different directory

**Solution A - Copy file to current directory:**
```bash
# Find where you are
pwd

# Copy the Excel file here
cp /path/to/sales_personnel_tracking.xlsx .

# Or on Windows
copy C:\path\to\sales_personnel_tracking.xlsx .
```

**Solution B - Update dashboard code:**
Open `sales_dashboard.py` and change line 46:
```python
# FROM:
df = load_data('/home/claude/sales_personnel_tracking.xlsx')

# TO:
df = load_data('sales_personnel_tracking.xlsx')  # Just the filename
```

#### Issue 2: File has wrong name

**Problem:** Your file is named `sales_data.xlsx` but dashboard looks for `sales_personnel_tracking.xlsx`

**Solution A - Rename your file:**
```bash
mv your_file.xlsx sales_personnel_tracking.xlsx
```

**Solution B - Use the improved dashboard:**
```bash
# The new version auto-detects Excel files
streamlit run sales_dashboard_v2.py
```

#### Issue 3: File is corrupted or wrong format

**Problem:** File won't open or has wrong structure

**Solution - Regenerate the file:**
```bash
python generate_sales_data.py
```

This creates a fresh `sales_personnel_tracking.xlsx` with sample data.

---

## Detailed Debugging

### Method 1: Use the Improved Dashboard (Easiest)

The `sales_dashboard_v2.py` has better error handling:

```bash
streamlit run sales_dashboard_v2.py
```

Features:
- ✅ Auto-finds Excel files in current directory
- ✅ Shows detailed error messages
- ✅ Has file uploader built-in
- ✅ Lists all available files

### Method 2: Manual Check

**Step 1: Where is the dashboard looking?**
```python
import os
print(os.getcwd())
```

**Step 2: Where is your Excel file?**
```bash
# On Mac/Linux
find ~ -name "sales_personnel_tracking.xlsx"

# On Windows (PowerShell)
Get-ChildItem -Path C:\ -Filter sales_personnel_tracking.xlsx -Recurse -ErrorAction SilentlyContinue
```

**Step 3: Put them in the same place**

Either:
- Move Excel file to where dashboard is running
- Move dashboard to where Excel file is
- Update the file path in code

### Method 3: Test File Reading

Create a test script `test_read.py`:

```python
import pandas as pd
import os

# Show current directory
print("Current directory:", os.getcwd())

# List Excel files
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
print("Excel files found:", excel_files)

# Try to read the file
if excel_files:
    file = excel_files[0]
    print(f"\nTrying to read: {file}")
    
    # Read the file
    xl = pd.ExcelFile(file)
    print("Sheets:", xl.sheet_names)
    
    # Read first sheet
    df = pd.read_excel(file, sheet_name=xl.sheet_names[0])
    print(f"\nFirst sheet has {len(df)} rows")
    print("Columns:", list(df.columns))
    print("\nFirst 2 rows:")
    print(df.head(2))
else:
    print("\nNo Excel files found!")
    print("Place sales_personnel_tracking.xlsx in:", os.getcwd())
```

Run it:
```bash
python test_read.py
```

---

## Common Error Messages

### Error: "No data found. Please check the Excel file."

**Cause:** File not found or empty

**Fix:**
1. Run `python debug_excel.py`
2. Check file location matches current directory
3. Use `sales_dashboard_v2.py` which auto-finds files

### Error: "FileNotFoundError: [Errno 2] No such file or directory"

**Cause:** File path is wrong

**Fix:**
```python
# In sales_dashboard.py, change:
df = load_data('/home/claude/sales_personnel_tracking.xlsx')

# To use relative path:
df = load_data('sales_personnel_tracking.xlsx')

# Or full path to your file:
df = load_data('/Users/yourname/Documents/sales_personnel_tracking.xlsx')
```

### Error: "Excel file format cannot be determined"

**Cause:** File is corrupted or not a real Excel file

**Fix:**
1. Re-download or regenerate the file
2. Open in Excel/LibreOffice and re-save
3. Run `python generate_sales_data.py` to create new file

### Error: "Sheet 'Monday' not found"

**Cause:** Excel file doesn't have expected sheet names

**Fix:**
1. Check sheet names in Excel file
2. Make sure sheets are named: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday
3. Regenerate file with correct structure

---

## Step-by-Step Setup (From Scratch)

### 1. Create a folder for the project
```bash
mkdir sales_dashboard
cd sales_dashboard
```

### 2. Save all files in this folder
- `sales_dashboard_v2.py`
- `requirements_dashboard.txt`
- `generate_sales_data.py`
- `debug_excel.py`

### 3. Install dependencies
```bash
pip install -r requirements_dashboard.txt
```

### 4. Generate sample data
```bash
python generate_sales_data.py
```

This creates `sales_personnel_tracking.xlsx` in the same folder.

### 5. Verify file exists
```bash
# Mac/Linux
ls -l sales_personnel_tracking.xlsx

# Windows
dir sales_personnel_tracking.xlsx
```

### 6. Run dashboard
```bash
streamlit run sales_dashboard_v2.py
```

Should open at: http://localhost:8501

---

## File Structure Check

Your folder should look like this:

```
sales_dashboard/
├── sales_dashboard_v2.py          ← Main dashboard
├── requirements_dashboard.txt      ← Dependencies
├── generate_sales_data.py          ← Data generator
├── debug_excel.py                  ← Debug tool
├── sales_personnel_tracking.xlsx   ← Your data file ✓
└── README_DASHBOARD.md             ← Documentation
```

---

## Still Not Working?

### Option 1: Use File Uploader

Run the improved dashboard:
```bash
streamlit run sales_dashboard_v2.py
```

If file isn't found, it will show a file uploader. Click and upload your Excel file directly.

### Option 2: Check Python Environment

```bash
# Check Python version (need 3.8+)
python --version

# Check installed packages
pip list | grep -E "(streamlit|pandas|plotly|openpyxl)"

# Reinstall if needed
pip install --upgrade streamlit pandas plotly openpyxl
```

### Option 3: Use Absolute Path

Find the full path to your Excel file:
```bash
# Mac/Linux
find ~ -name "sales_personnel_tracking.xlsx" -type f

# Windows
Get-ChildItem -Path C:\ -Filter sales_personnel_tracking.xlsx -Recurse
```

Then update `sales_dashboard.py`:
```python
# Use the full path from above
df = load_data('/full/path/to/sales_personnel_tracking.xlsx')
```

---

## Quick Commands Reference

```bash
# Debug the issue
python debug_excel.py

# Generate fresh data
python generate_sales_data.py

# Run improved dashboard (recommended)
streamlit run sales_dashboard_v2.py

# Run original dashboard
streamlit run sales_dashboard.py

# Check current directory
pwd  # Mac/Linux
cd   # Windows

# List Excel files
ls *.xlsx  # Mac/Linux
dir *.xlsx # Windows
```

---

## Contact/Support

If still stuck:

1. Run `python debug_excel.py` and copy the output
2. Check what error message appears in the dashboard
3. Verify file exists: `ls -l sales_personnel_tracking.xlsx`
4. Make sure you're in the right directory: `pwd`

The debug script will tell you exactly what's wrong!
