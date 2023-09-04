import pandas as pd

def store_websites_in_excel(websites):
    # Create a DataFrame from the websites list
    df = pd.DataFrame({'Website': websites})

    # Specify the Excel file name
    excel_filename = "websites.xlsx"

    # Save the DataFrame to an Excel file
    df.to_excel(excel_filename, index=False)

    return excel_filename
