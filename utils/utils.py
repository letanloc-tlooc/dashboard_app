import os
from flask import flash, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

def load_dataframe(filepath, ext):
    if not filepath or not os.path.exists(filepath):
        # flash("Không tìm thấy file!", "danger")
        return redirect(url_for('index'))

    if ext == 'csv':
        return pd.read_csv(filepath)
    else:
        return pd.read_excel(filepath)

def generate_base64_plot(df, col1, col2):
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x=col1, y=col2)
    plt.title(f'{col1} vs {col2}')
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.read()).decode()
    plt.close()
    return plot_url

def describe_column_plot(df, col):
    desc = df[col].describe()
    return desc
