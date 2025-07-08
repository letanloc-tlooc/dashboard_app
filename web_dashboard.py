import os
import pandas as pd
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join('upload')
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'This is your secret key to utilize session in Flask'

# Trang upload file
@app.route('/', methods=['GET', 'POST'])
def uploadFile():
    if request.method == 'POST':
        f = request.files.get('file')

        if f and f.filename.endswith('.csv'):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Tạo folder nếu chưa có
            data_filename = secure_filename(f.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)
            f.save(filepath)

            # Lưu đường dẫn file vào session
            session['uploaded_data_file_path'] = filepath

            return render_template('index2.html')  # Hiển thị trang xác nhận
        else:
            return "Vui lòng chọn file .csv hợp lệ!"

    return render_template("index.html")

# Trang hiển thị dữ liệu
@app.route('/show_data')
def showData():
    data_file_path = session.get('uploaded_data_file_path', None)

    if data_file_path is None:
        return redirect(url_for('uploadFile'))

    try:
        uploaded_df = pd.read_csv(data_file_path, encoding='unicode_escape')
        uploaded_df_html = uploaded_df.to_html(classes="table table-bordered")
        return render_template('index2.html', data_var=uploaded_df_html)
    except Exception as e:
        return f"Lỗi đọc file: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
