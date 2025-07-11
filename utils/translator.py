# from deep_translator import GoogleTranslator

# def translate_column_names(columns):
#     translated = []
#     for col in columns:
#         try:
#             vi = GoogleTranslator(source='en', target='vi').translate(col.replace('_', ' '))
#             translated.append(vi.title())
#         except Exception:
#             translated.append(col)  # fallback nếu lỗi
#     return translated