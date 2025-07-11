import os
from flask import Flask

app = Flask(__name__)
app.secret_key = 'supersecret'

#Cấu hình thư mục chứa dữ liệu
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'upload')

from routes import *

if __name__ == '__main__':
    app.run(debug=True)
