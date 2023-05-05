# ref https://www.codeunderscored.com/upload-download-files-flask/

import os
from os import listdir
from os.path import isfile, join
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

# initialising the flask app
app = Flask(__name__)

# Creating the upload folder
upload_folder = "uploads/"
if not os.path.exists(upload_folder):
    os.mkdir(upload_folder)

# Configuring the upload folder
app.config['UPLOAD_FOLDER'] = upload_folder

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


def get_metadata(filename: str):
    ''' return standard metadata from a filename '''
    return

@app.route('/download', methods=['GET', 'POST'])
def download():
    ''' allow user download a file specify with `name` url parameter. Return sample.txt if no parameter. '''
    filename_to_reqest = request.args.get("name")
    if not filename_to_reqest or filename_to_reqest == '':
        filename_to_reqest = 'sample.txt'
    return send_file(f"{app.config['UPLOAD_FOLDER']}/{filename_to_reqest}", as_attachment=True)

@app.route('/list_local', methods=['GET'])
def list_local():
    ''' list all file metadata in local storage folder (cache of S3) '''
    script_path = os.path.dirname(os.path.abspath(__file__))    # locate the server.py path
    cache_path = join(script_path, app.config['UPLOAD_FOLDER']) # locate the configed upload folder
    onlyfiles = [f for f in listdir(cache_path) if isfile(join(cache_path, f))] # get file names
    print(cache_path ,onlyfiles)
    return {'files': onlyfiles}

@app.route('/list', methods=['GET'])
def list():
    ''' list all file metadata in remote S3 database. '''
    return {'files': []}


if __name__ == '__main__':
    app.run()  # running the flask app
