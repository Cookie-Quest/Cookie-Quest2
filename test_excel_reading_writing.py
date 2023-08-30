import pandas as pd

excel_file = "Capstone Excel report format.xlsx"
excel_sheet = "Sheet1"
column = "Website"

try:
    df = pd.read_excel(excel_file, sheet_name = excel_sheet)

    if column in df.columns:
        websites = df[column]
        print("Websites to Scan:")
    else:
        print(f"Column '{column}' not found in the Excel file.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
print(websites)
