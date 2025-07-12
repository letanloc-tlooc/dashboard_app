import os
from flask import request, session, jsonify
import pandas as pd
from app import app
# from utils.translator import translate_column_names
from utils.utils import *

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
        'total_pages': total_pg,
        'stats' : {
            'rows'   : int(df.shape[0]),
            'cols'   : int(df.shape[1]),
            'missing': int(df.isnull().sum().sum())
        }
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


# ---------- API: Lấy dữ liệu biểu đồ tần suất top 10 cho một thuộc tính ---------- 
@app.route('/api/chart', methods=['POST'])
def api_chart():
    col = request.form.get('selected_col')
    filepath = session.get('filepath')
    ext = session.get('file_ext', 'csv')
    df = load_dataframe(filepath, ext)
    if col not in df.columns:
        return jsonify({'error': 'Thuộc tính không tồn tại'}), 400
    data_count = df[col].value_counts().nlargest(10)
    return jsonify({
        'labels': data_count.index.tolist(),
        'values': data_count.values.tolist(),
        'column': col
    })


# ---------- API: Lấy thống kê mô tả cho thuộc tính số ---------- 
@app.route('/api/describe', methods=['POST'])
def api_describe():
    col = request.form.get('selected_col')
    filepath = session.get('filepath')
    ext = session.get('file_ext', 'csv')
    df = load_dataframe(filepath, ext)
    if col not in df.columns:
        return jsonify({'error': 'Thuộc tính không tồn tại'}), 400
    if col not in df.select_dtypes(include='number').columns:
        return jsonify({'error': 'Thuộc tính không phải số'}), 400
    desc = df[col].describe()
    return jsonify({
        'column': col,
        'table_data': [
            {'label': label, 'value': float(value)} for label, value in desc.items()
        ]
    })