import os
from flask import Flask
# Import routes sau khi tạo app


app = Flask(__name__)
app.secret_key = 'supersecret'
#Cấu hình thư mục chứa dữ liệu
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'upload')
from routes import *


if __name__ == '__main__':
    app.run(debug=True)


# ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# #Hàm upload
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         f = request.files.get('file')
#         if f and allowed_file(f.filename):
#             os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#             filename = secure_filename(f.filename)
#             filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             f.save(filepath)

#             session['filepath'] = filepath
#             session['file_ext'] = filename.rsplit('.', 1)[1].lower()

#             return redirect(url_for('data_view')) #trả về /data_view
#     return render_template('index_app.html')

# #Hàm hiển thị dữ liệu
# @app.route('/data_view')
# def data_view():
#     filepath = session.get('filepath')
#     ext = session.get('file_ext', 'csv')

#     if not filepath or not os.path.exists(filepath):
#         flash("Không tìm thấy file dữ liệu!", "danger")
#         return redirect(url_for('index'))

#     # Đọc file theo định dạng
#     if ext == 'csv':
#         df = pd.read_csv(filepath)
#     elif ext in ['xlsx', 'xls']:
#         df = pd.read_excel(filepath)
#     else:
#         flash("Không hỗ trợ định dạng file này.", "danger")
#         return redirect(url_for('index'))

#     r, d = df.shape #xem số dòng, số cột
#     null_series = df.isnull().sum() #xem số dữ liệu thiếu
#     total_missing = int(null_series.sum()) 
#     missing_cols = null_series[null_series > 0].to_dict()
#     numeric_columns = df.select_dtypes(include='number').columns.tolist()

#     return render_template(
#         'index_app.html',
#         table_html=df.head(10).to_html(classes="table table-bordered", index=False),
#         r=r,
#         d=d,
#         total_missing=total_missing,
#         missing_cols=missing_cols,
#         columns=df.columns.tolist(),
#         numeric_columns=numeric_columns
#     )

# #Hàm xóa dữ liệu
# @app.route('/clear_data')
# def clear_data():
#     filepath = session.pop('filepath', None)
#     if filepath and os.path.exists(filepath):
#         os.remove(filepath)
#     flash("✅ Dữ liệu đã được xóa", "success")
#     return redirect(url_for('index'))

# #Hàm vẻ biểu đồ 1 thuộc tính
# @app.route('/chart', methods=['POST'])
# def chart():
#     col = request.form.get('selected_col') #chọn thuộc tính
#     filepath = session.get('filepath')
#     ext = session.get('file_ext', 'csv')
    
#     if not filepath or not os.path.exists(filepath):
#         flash("Không tìm thấy file!", "danger")
#         return redirect(url_for('index'))

#     # Đọc file theo định dạng
#     if ext == 'csv':
#         df = pd.read_csv(filepath)
#     else:
#         df = pd.read_excel(filepath)
#     if col not in df.columns:
#         return redirect(url_for('index'))

#     data_count = df[col].value_counts().nlargest(10) #hiển thị 10 dòng đầu 
#     labels = data_count.index.tolist()
#     values = data_count.values.tolist()

#     return render_template('char.html', labels=labels, values=values, column=col)

# #Hàm thống kê dữ liệu
# @app.route('/describe', methods=['POST'])
# def describe_chart():
#     col = request.form.get('selected_col')
#     filepath = session.get('filepath')
#     ext = session.get('file_ext', 'csv')
    
#     if not filepath or not os.path.exists(filepath):
#         flash("Không tìm thấy file!", "danger")
#         return redirect(url_for('index'))

#     # Đọc file theo định dạng
#     if ext == 'csv':
#         df = pd.read_csv(filepath)
#     else:
#         df = pd.read_excel(filepath)

#     if not pd.api.types.is_numeric_dtype(df[col]): #kiểm tra kiểu dữ liệu (chỉ nhận dạng số int/fl...)
#         flash(f"Cột '{col}' không phải dạng số nên không thể thống kê.", "warning")
#         return redirect(url_for('data_view'))

#     desc = df[col].describe()
#     table_data = list(desc.items())  # [(count, xxx), (mean, xxx), ...]

#     return render_template('describe.html', table_data=table_data, col=col)

# #Hàm trực quan 2 thuộc tính
# @app.route('/plot_categorical', methods=['POST'])
# def plot_categorical():
#     col1 = request.form.get('col1')
#     col2 = request.form.get('col2')
#     filepath = session.get('filepath')
#     ext = session.get('file_ext', 'csv')

#     if not filepath or not os.path.exists(filepath):
#         flash("Không tìm thấy file!", "danger")
#         return redirect(url_for('index'))

#     # Đọc dữ liệu
#     df = pd.read_csv(filepath) if ext == 'csv' else pd.read_excel(filepath)

#     if col1 not in df.columns or col2 not in df.columns:
#         flash("Thuộc tính không hợp lệ!", "danger")
#         return redirect(url_for('data_view'))

#     # Vẽ biểu đồ phân loại (categorical)
#     plt.figure(figsize=(8, 6))
#     ax = sns.countplot(x=col1, hue=col2, data=df, palette="Set2")

#     # Thêm nhãn
#     for container in ax.containers:
#         ax.bar_label(container, label_type='edge', fontsize=9)

#     plt.title(f'{col1} vs {col2}')
#     plt.xlabel(col1)
#     plt.ylabel('Số lượng')
#     plt.xticks(rotation=20)
#     plt.tight_layout()

#     # Xuất ảnh ra base64
#     import io, base64
#     img = io.BytesIO()
#     plt.savefig(img, format='png')
#     img.seek(0)
#     plot_url = base64.b64encode(img.getvalue()).decode()
#     plt.close()

#     return render_template('plot2.html', plot_url=plot_url, col1=col1, col2=col2)

