import os
import pandas as pd
import sys

print("=" * 60)
print("SALES DASHBOARD - FILE DEBUG TOOL")
print("=" * 60)

# Step 1: Check current directory
print("\n1. Current Working Directory:")
print(f"   {os.getcwd()}")

# Step 2: List files in current directory
print("\n2. Files in current directory:")
files = os.listdir('.')
excel_files = [f for f in files if f.endswith(('.xlsx', '.xls'))]
if excel_files:
    print(f"   Found {len(excel_files)} Excel file(s):")
    for f in excel_files:
        size = os.path.getsize(f) / 1024  # KB
        print(f"   ✓ {f} ({size:.1f} KB)")
else:
    print("   ✗ No Excel files found in current directory")

# Step 3: Check for the specific file
print("\n3. Looking for 'sales_personnel_tracking.xlsx':")
if os.path.exists('sales_personnel_tracking.xlsx'):
    print("   ✓ File found!")
    file_size = os.path.getsize('sales_personnel_tracking.xlsx') / 1024
    print(f"   File size: {file_size:.1f} KB")
else:
    print("   ✗ File NOT found in current directory")
    print("   Please ensure 'sales_personnel_tracking.xlsx' is in:")
    print(f"   {os.getcwd()}")

# Step 4: Try to read the file
print("\n4. Attempting to read Excel file:")
if excel_files:
    test_file = excel_files[0]
    print(f"   Testing with: {test_file}")
    try:
        # Try to read Excel file
        xl = pd.ExcelFile(test_file)
        print(f"   ✓ File opened successfully!")
        print(f"   Sheets found: {xl.sheet_names}")
        
        # Check if expected sheets exist
        expected_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        missing_days = [day for day in expected_days if day not in xl.sheet_names]
        
        if missing_days:
            print(f"   ⚠ Warning: Missing sheets: {missing_days}")
        else:
            print(f"   ✓ All expected day sheets found!")
        
        # Try to read first sheet
        print(f"\n5. Reading first sheet ({xl.sheet_names[0]}):")
        df = pd.read_excel(test_file, sheet_name=xl.sheet_names[0])
        print(f"   ✓ Sheet loaded successfully!")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        
        # Check for expected columns
        expected_cols = ['Personnel Name', 'Login Time', 'Visit #', 'Location', 
                        'Maps Link', 'Check-In Time', 'Check-Out Time', 'Selfie', 'Logout Time']
        missing_cols = [col for col in expected_cols if col not in df.columns]
        
        if missing_cols:
            print(f"   ⚠ Warning: Missing columns: {missing_cols}")
            print(f"   Actual columns: {list(df.columns)}")
        else:
            print(f"   ✓ All expected columns found!")
            
        # Show sample data
        print(f"\n6. Sample data (first 2 rows):")
        print(df.head(2).to_string())
        
    except Exception as e:
        print(f"   ✗ Error reading file: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print("\nFull error trace:")
        traceback.print_exc()
else:
    print("   ✗ No Excel files to test")

# Step 5: Provide fix instructions
print("\n" + "=" * 60)
print("HOW TO FIX:")
print("=" * 60)

if not excel_files:
    print("\n❌ PROBLEM: No Excel file found")
    print("\n   SOLUTION:")
    print("   1. Download the 'sales_personnel_tracking.xlsx' file")
    print("   2. Place it in the same folder as sales_dashboard.py")
    print(f"   3. Current folder: {os.getcwd()}")
    
elif not os.path.exists('sales_personnel_tracking.xlsx'):
    print("\n❌ PROBLEM: Wrong filename")
    print(f"\n   Found: {excel_files}")
    print("   Expected: sales_personnel_tracking.xlsx")
    print("\n   SOLUTION (Option 1): Rename your file to 'sales_personnel_tracking.xlsx'")
    print(f"\n   SOLUTION (Option 2): Update sales_dashboard.py line 46:")
    print(f"   Change: df = load_data('/home/claude/sales_personnel_tracking.xlsx')")
    print(f"   To:     df = load_data('{excel_files[0]}')")

else:
    print("\n✅ File found and readable!")
    print("\n   Next steps:")
    print("   1. Run: streamlit run sales_dashboard.py")
    print("   2. Dashboard should open at http://localhost:8501")

print("\n" + "=" * 60)
