# ref https://www.codeunderscored.com/upload-download-files-flask/

import os
import boto3
from os import listdir
from os.path import isfile, join
from flask import Flask, render_template, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# initialising the flask app
app = Flask(__name__)
CORS(app)

# Creating the upload folder
upload_folder = "uploads/"
if not os.path.exists(upload_folder):
    os.mkdir(upload_folder)

# Configuring the upload folder
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['BUCKET_NAME'] = "final-test-bucket-1"

# configuring the allowed extensions
allowed_extensions = ['jpg', 'png', 'pdf', 'txt', 'doc']


def check_file_extension(filename):
    return filename.split('.')[-1] in allowed_extensions

@app.route('/')
def upload_file():
    ''' simple html up & download page '''
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def uploadfile():
    ''' allow multiple file uploads to server. Accept multipart/form-data POST request with name `files`. '''
    # get the file from the files object
    files = request.files.getlist('files')
    print(files)
    for f in files:
        print(f.filename)
        # Saving the file in the required destination
        if check_file_extension(f.filename):
            # this will secure the file
            f.save(os.path.join(
                app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
    return 'file uploaded successfully'  # Display thsi message after uploading

@app.route('/upload_remote', methods=['POST'])
def uploadfile_remote():
    ''' allow multiple file uploads to server. Accept multipart/form-data POST request with name `files`. '''
    # get the file from the files object
    files = request.files.getlist('files')
    print(files)
    for f in files:
        print(f.filename)
        # Saving the file in the required destination
        if check_file_extension(f.filename):
            # this will secure the file
            # f.save(os.path.join(
            #     app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            s3 = boto3.client('s3')
            data_path = os.path.join(app.config["UPLOAD_FOLDER"], f.filename)
            s3.upload_fileobj(f, app.config["BUCKET_NAME"], data_path)

    return 'file uploaded successfully'  # Display thsi message after uploading


def get_metadata(filename: str):
    ''' return standard metadata from a filename '''
    year, department, title = 110, None, None
    try:
        fields = filename.split('-')
        year = int(fields[0])
    except:
        year = 110
    try:
        fields = filename.split('-')
        department = fields[1]
    except:
        department = None
    try:
        title = fields[2]
    except:
        title = filename
    format = {
        "year": year,
        "department": department,
        "title": title,
        "fileurl": f"http://127.0.0.1:5000/download?name={filename}", # url 先這樣，之後改成 load-balancer 的 DNS url。
    }
    return format

# test script
# res = get_metadata('sample.txt')
# res = get_metadata('110-生科系-想了解生科系的一定要看.txt') 
# # {'year': 110, 'department': '生科系', 'title': '想了解生科系的一定要看.txt', 'fileurl': '110-生科系-想了解生科系的一定要看.txt'}
# print(res)

@app.route('/download', methods=['GET', 'POST'])
def download():
    ''' allow user download a file specify with `name` url parameter. Return sample.txt if no parameter. '''
    filename_to_reqest = request.args.get("name")
    if not filename_to_reqest or filename_to_reqest == '':
        filename_to_reqest = 'sample.txt'
    print(filename_to_reqest)
    return send_file(f"{app.config['UPLOAD_FOLDER']}/{filename_to_reqest}", as_attachment=True)

@app.route('/download_remote', methods=['GET', 'POST'])
def download_remote():
    ''' allow user download a file specify with `name` url parameter. Return sample.txt if no parameter. '''
    filename_to_reqest = request.args.get("name")
    
    # default behavior
    if not filename_to_reqest or filename_to_reqest == '':
        filename_to_reqest = 'sample.txt'
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename_to_reqest)
    # check if file exist in local path, if not, download from s3
    if not os.path.exists(file_path):
        s3 = boto3.client('s3')
        s3.download_file(app.config['BUCKET_NAME'], file_path, file_path)
    
    return send_file(f"{app.config['UPLOAD_FOLDER']}/{filename_to_reqest}", as_attachment=True)


@app.route('/list', methods=['GET'])
def list_local():
    ''' list all file metadata in local storage folder (cache of S3) '''
    script_path = os.path.dirname(os.path.abspath(__file__))    # locate the server.py path
    cache_path = join(script_path, app.config['UPLOAD_FOLDER']) # locate the configed upload folder
    onlyfiles = [f for f in listdir(cache_path) if isfile(join(cache_path, f))] # get file names
    print(cache_path ,onlyfiles)
    return {'files': [get_metadata(o) for o in onlyfiles]}

@app.route('/list_remote', methods=['GET'])
def list():
    ''' list all file metadata in remote S3 database. '''
    
    files = []
    client = boto3.client("s3")
    response = client.list_objects_v2(
        Bucket=app.config['BUCKET_NAME'],
        Prefix=app.config["UPLOAD_FOLDER"]
    )

    for content in response.get('Contents', []):
        filename = content['Key'].replace(app.config["UPLOAD_FOLDER"], "")
        if filename == "": # directory self
            continue
        files.append(get_metadata(filename))
    
    return {'files': files}


if __name__ == '__main__':
    app.run()  # running the flask app
