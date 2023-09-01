import pandas as pd
from flask import request, redirect

def upload_excel_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
            print(df.head())
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


























# from flask import Flask, request, redirect
# import pandas as pd
# import os
#
# app = Flask(__name__)
#
# @app.route('/', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file and file.filename.endswith('.xlsx'):
#             df = pd.read_excel(file)
#             print(df.head())
#             return redirect('/')
#     return '''
#     <!doctype html>
#     <title>Upload URL's to scan</title>
#     <h1>Upload spreadsheet with URL's in Column A</h1>
#     <form method=post enctype=multipart/form-data>
#       <input type=file name=file>
#       <input type=submit value=Upload>
#     </form>
#     '''
#
# if __name__ == '__main__':
#     app.run(debug=True)
