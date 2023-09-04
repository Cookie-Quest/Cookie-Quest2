from flask import Flask, request, redirect
import pandas as pd




@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
            print(df.head())  # Just printing the first 5 rows to console
            return redirect('/')
    return '''
    <!doctype html>
    <title>Upload an Excel File</title>
    <h1>Upload an Excel file</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


