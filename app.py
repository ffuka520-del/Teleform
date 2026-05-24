from flask import Flask, render_template_string, request, jsonify
import json
import os

app = Flask(__name__)

# Import generated forms dari bot
try:
    from telegram_bot import generated_forms
except ImportError:
    generated_forms = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>FormGen - Isi Form</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 500px;
            padding: 40px;
        }
        .header {
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 24px;
            margin-bottom: 5px;
            color: #333;
        }
        .header p {
            color: #666;
            font-size: 14px;
        }
        .progress-bar {
            height: 4px;
            background: #eee;
            border-radius: 2px;
            margin-bottom: 30px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s;
        }
        .form-page { display: none; }
        .form-page.active { display: block; }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
            font-size: 14px;
        }
        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            font-family: inherit;
        }
        .form-group input:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .buttons {
            display: flex;
            gap: 10px;
            margin-top: 30px;
        }
        .btn {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .btn-secondary {
            background: #f0f0f0;
            color: #333;
        }
        .btn-secondary:hover {
            background: #e0e0e0;
        }
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .success {
            text-align: center;
            padding: 40px 20px;
        }
        .success-icon {
            font-size: 60px;
            margin-bottom: 20px;
        }
        .success h2 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .page-indicator {
            text-align: center;
            font-size: 12px;
            color: #999;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container" id="app">
        <div class="header">
            <h1>{{ template }}</h1>
            <p>Isi form di bawah ini</p>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" id="progress"></div>
        </div>
        
        <div class="page-indicator" id="pageIndicator"></div>
        
        <div id="formContainer"></div>
        
        <div id="successContainer" style="display:none;" class="success">
            <div class="success-icon">✅</div>
            <h2>Form Terkirim!</h2>
            <p>Terima kasih telah mengisi form.</p>
        </div>
    </div>

    <script>
        const formData = {{ form_data | tojson }};
        let currentPage = 0;
        let answers = {};

        function render() {
            const totalPages = formData.pages.length;
            const page = formData.pages[currentPage];
            const progress = ((currentPage + 1) / totalPages) * 100;

            document.getElementById('progress').style.width = progress + '%';
            document.getElementById('pageIndicator').textContent = 
                `Halaman ${currentPage + 1} dari ${totalPages}`;

            let html = `<div class="form-page active">
                <h3 style="margin-bottom: 20px; color: #333;">${page.name}</h3>`;

            page.columns.forEach(col => {
                const value = answers[currentPage]?.[col] || '';
                html += `
                    <div class="form-group">
                        <label>${col.replace(/_/g, ' ').toUpperCase()}</label>
                        <input type="text" 
                               data-col="${col}" 
                               value="${value}"
                               placeholder="Masukkan ${col}">
                    </div>`;
            });

            html += '<div class="buttons">';
            if (currentPage > 0) {
                html += '<button class="btn btn-secondary" onclick="prevPage()">← Sebelum</button>';
            }
            html += `<button class="btn btn-primary" onclick="${currentPage === totalPages - 1 ? 'submit()' : 'nextPage()'}">
                ${currentPage === totalPages - 1 ? '✓ Kirim' : 'Berikut →'}
            </button>`;
            html += '</div></div>';

            document.getElementById('formContainer').innerHTML = html;

            // Set values
            document.querySelectorAll('input[data-col]').forEach(el => {
                el.addEventListener('change', (e) => {
                    if (!answers[currentPage]) answers[currentPage] = {};
                    answers[currentPage][e.target.dataset.col] = e.target.value;
                });
            });
        }

        function nextPage() {
            if (currentPage < formData.pages.length - 1) {
                currentPage++;
                render();
            }
        }

        function prevPage() {
            if (currentPage > 0) {
                currentPage--;
                render();
            }
        }

        function submit() {
            console.log('Form submitted:', answers);
            document.getElementById('formContainer').style.display = 'none';
            document.getElementById('successContainer').style.display = 'block';
        }

        render();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return "FormGen - Bot Form Builder"

@app.route('/f/<form_id>')
def show_form(form_id):
    if form_id not in generated_forms:
        return "Form tidak ditemukan", 404
    
    form = generated_forms[form_id]
    return render_template_string(
        HTML_TEMPLATE,
        template=form['template'].upper(),
        form_data=form
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
