import uuid
from flask import request, render_template, redirect, url_for, flash, session, jsonify
import os
import pandas as pd
from werkzeug.utils import secure_filename
from app import app
# from utils.translator import translate_column_names
from utils.utils import allowed_file, load_dataframe, generate_base64_plot, describe_column_plot
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

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
        flash("✅ Tải lên thành công.", "success")
        return render_template('home_main.html')

    # GET – chỉ render khung
    return render_template('home_main.html')


# ---------- API: bảng dữ liệu ----------
@app.route('/api/data')
def api_data():
    filepath = session.get('filepath')
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'No file'}), 404

    ext = session.get('file_ext', 'csv')
    df = load_dataframe(filepath, ext)

    page      = int(request.args.get('page', 1))
    per_page  = 100
    total_pg  = (len(df)-1)//per_page + 1

    start = (page-1) * per_page
    end   = start + per_page
    html  = df.iloc[start:end].to_html(classes='table table-striped', index=False)

    return jsonify({
        'html': html,
        'current_page': page,
        'total_pages': total_pg
    })


# ---------- API: thông tin cột thiếu ----------
@app.route('/api/missing-info')
def api_missing_info():
    filepath = session.get('filepath')
    if not filepath or not os.path.exists(filepath):
        return jsonify([])

    ext = session.get('file_ext', 'csv')
    df  = load_dataframe(filepath, ext)

    nulls = df.isnull().sum()
    res   = [dict(column=c, missing=int(nulls[c]),
                  numeric=pd.api.types.is_numeric_dtype(df[c]))
             for c in df.columns if nulls[c] > 0]
    return jsonify(res)


# ---------- API: xử lý dữ liệu thiếu ----------
@app.route('/api/handle-missing', methods=['POST'])
def api_handle_missing():
    filepath = session.get('filepath')
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'No file'}), 404

    ext = session.get('file_ext', 'csv')
    df  = load_dataframe(filepath, ext)

    nulls = df.isnull().sum()
    miss_cols = nulls[nulls > 0].index

    for col in miss_cols:
        strategy = request.form.get(f'strategy_{col}')
        if strategy == 'drop':
            df = df[df[col].notnull()]
        elif strategy == 'mean' and pd.api.types.is_numeric_dtype(df[col]):
            df[col].fillna(df[col].mean(), inplace=True)
        elif strategy == 'median' and pd.api.types.is_numeric_dtype(df[col]):
            df[col].fillna(df[col].median(), inplace=True)

    # ghi đè
    if ext == 'csv':
        df.to_csv(filepath, index=False)
    else:
        df.to_excel(filepath, index=False)

    return jsonify({'message': '✅ Đã xử lý dữ liệu thiếu.'})



# Trang dashboard thống kê & trực quan
@app.route('/data_visualization')
def data_visualization():
    filepath = session.get('filepath')
    ext = session.get('file_ext', 'csv')

    if not filepath or not os.path.exists(filepath):
        flash("⚠️ Không có file nào được tải lên.", "warning")
        return redirect(url_for('index'))

    df = load_dataframe(filepath, ext)
    
    r, d = df.shape
    null_series = df.isnull().sum()
    total_missing = int(null_series.sum())
    missing_cols = null_series[null_series > 0].to_dict()
    numeric_columns = df.select_dtypes(include='number').columns.tolist()
    categorical_columns = [col for col in df.columns if df[col].dtype == 'object' or df[col].nunique() <= 10]
    quantitative_columns = [col for col in numeric_columns if col not in categorical_columns]

    return render_template(
        'data_view_main.html',
        r=r,
        d=d,
        total_missing=total_missing,
        missing_cols=missing_cols,
        columns=df.columns.tolist(),
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        quantitative_columns=quantitative_columns
    )



#Hàm vẻ biểu đồ 1 thuộc tính
@app.route('/chart', methods=['POST'])
def chart():
    col = request.form.get('selected_col') #chọn thuộc tính
    filepath = session.get('filepath')
    ext = session.get('file_ext', 'csv')
    df = load_dataframe(filepath, ext)

    data_count = df[col].value_counts().nlargest(10) #hiển thị 10 dòng đầu 
    labels = data_count.index.tolist()
    values = data_count.values.tolist()

    return render_template('char.html', labels=labels, values=values, column=col)

@app.route('/describe', methods=['POST'])
def describe_chart():
    col = request.form.get('selected_col')
    filepath = session.get('filepath')
    ext = session.get('file_ext', 'csv')
    df = load_dataframe(filepath, ext)

    if col not in df.select_dtypes(include='number').columns:
        flash("Không thể thực hiện trực quan hóa cho thuộc tính không phải số.", "warning")
        return redirect(url_for('data_view'))

    desc = df[col].describe()
    table_data = list(desc.items())  # [(count, xxx), (mean, xxx), ...]

    return render_template('describe.html', table_data=table_data, col=col)

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



