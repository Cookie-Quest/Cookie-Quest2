import pandas as pd


def excel_reading(excel_file: str, excel_sheet: str, column: str):
    try:
        df = pd.read_excel(excel_file, sheet_name = excel_sheet)

        if column in df.columns:
            websites = df[column]
            print("Websites to Scan:")
            print(websites)
        else:
            print(f"Column '{column}' not found in the Excel file.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


excel_reading("Capstone Excel report format.xlsx", "Sheet1", "Website")

