import google.generativeai as genai

genai.configure(api_key="AIzaSyD_ujE41OPnkHzw0vooCMrmSzDVhSzI7Ng")

models = genai.list_models()
for m in models:
    print(m.name, "-", m.supported_generation_methods)
