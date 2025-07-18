import uuid
from flask import request, render_template, redirect, url_for, flash, session
import os
import pandas as pd
from werkzeug.utils import secure_filename
from app import app
# from utils.translator import translate_column_names
from utils.utils import *
from api import *
import io


# Route xử lý việc upload file
@app.route('/', methods=['GET', 'POST'])
def index(): 
    if request.method == 'POST':
        f = request.files.get('file')
        if not f:
            flash("⚠️ Chưa chọn file!", "warning")
            return render_template('home_main.html')

        # kiểm tra đuôi
        if f.filename.rsplit('.', 1)[-1].lower() not in ('csv', 'xlsx', 'xls'):
            flash("❌ Chỉ hỗ trợ CSV / Excel", "danger")
            return render_template('home_main.html')

        # xoá file cũ (nếu có)
        old_path = session.pop('filepath', None)
        if old_path and os.path.exists(old_path):
            os.remove(old_path)

        # lưu file mới
        filename = f"{uuid.uuid4().hex}_{secure_filename(f.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        f.save(filepath)

        # lưu session
        session['filepath'] = filepath
        session['file_ext'] = filename.rsplit('.', 1)[1].lower()

        

        # front‑end sẽ gọi /api/data nên chỉ render khung
        # flash("✅ Tải lên thành công.", "success")
        # return render_template('home_main.html')

    # GET – chỉ render khung
    return render_template('home_main.html')


@app.route('/data-view')
def data_view():
    filepath = session.get('filepath')
    ext = session.get('file_ext', 'csv')
    df = load_dataframe(filepath, ext)
    # Tất cả cột
    all_columns = df.columns.tolist()

    # Cột số thật sự (loại số và không phải mã hóa phân loại)
    numeric_columns = []
    for col in df.select_dtypes(include='number').columns:
        if df[col].nunique() > 10:  # Giới hạn phân loại: <= 10 giá trị là phân loại
            numeric_columns.append(col)
            
    return render_template('chart.html', columns=all_columns, numeric_columns=numeric_columns)



@app.route('/plot_categorical', methods=['POST'])
def plot_categorical():
    col1 = request.form.get('col1')
    col2 = request.form.get('col2')
    filepath = session.get('filepath')
    ext = session.get('file_ext', 'csv')
    # Đọc file
    df = load_dataframe(filepath, ext)

    # Vẽ biểu đồ phân loại
    plt.figure(figsize=(8, 6))
    ax = sns.countplot(x=col1, hue=col2, data=df, palette="Set2")

    for container in ax.containers:
        ax.bar_label(container, label_type='edge', fontsize=9)

    plt.title(f'{col1} vs {col2}')
    plt.xlabel(col1)
    plt.ylabel('Số lượng')
    plt.xticks(rotation=20)
    plt.tight_layout()

    # Encode biểu đồ sang base64 để nhúng trong HTML
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.read()).decode()
    plt.close()

    return render_template('plot2.html', plot_url=plot_url, col1=col1, col2=col2)

@app.route('/plot_cate_num', methods=['POST'])
def plot_cate_num():
    col_cat = request.form.get('col_cat')  # Cột phân loại
    col_num = request.form.get('col_num')  # Cột định lượng

    filepath = session.get('filepath')
    ext = session.get('file_ext', 'csv')
    df = load_dataframe(filepath,ext)
    
    # Kiểm tra cột tồn tại
    if col_cat not in df.columns or col_num not in df.columns:
        flash("Cột không hợp lệ!", "danger")
        return redirect(url_for('data_view'))

    # Kiểm tra cột định lượng là kiểu số
    if not pd.api.types.is_numeric_dtype(df[col_num]):
        flash("Cột định lượng phải là số!", "warning")
        return redirect(url_for('data_view'))

    # ✅ Phân loại lại cột phân loại nếu có ít giá trị duy nhất
    if pd.api.types.is_numeric_dtype(df[col_cat]) and df[col_cat].nunique() <= 10:
        df[col_cat] = df[col_cat].astype('category')

    # Nếu sau khi chuyển mà vẫn không phải category hoặc object thì không vẽ
    if df[col_cat].dtype not in ['category', 'object']:
        flash("Cột phân loại không hợp lệ!", "warning")
        return redirect(url_for('data_view'))


    plt.figure(figsize=(10, 6))
    sns.boxplot(x=col_cat, y=col_num, data=df, palette="Set2")
    plt.title(f'{col_num} theo nhóm {col_cat}')
    plt.xticks(rotation=20)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.read()).decode()
    plt.close()
    
    return render_template('plot2.html', plot_url=plot_url, col1=col_cat, col2=col_num)


@app.route('/heatmap')
def correlation_heatmap():
    filepath = session.get('filepath')
    ext = session.get('file_ext', 'csv')
    # Đọc file
    df = load_dataframe(filepath, ext)

    # Chỉ lấy các cột số để tính tương quan
    numeric_df = df.select_dtypes(include='number')

    if numeric_df.shape[1] < 2:
        flash("Không đủ dữ liệu số để hiển thị heatmap!", "warning")
        return redirect(url_for('data_view'))

    correlation = numeric_df.corr()

    # Vẽ heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Heatmap')
    plt.tight_layout()

    # Convert sang base64 để hiển thị
    import io, base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.read()).decode()
    plt.close()

    return render_template('heatmap.html', plot_url=plot_url)



