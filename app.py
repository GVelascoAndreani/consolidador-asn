from flask import Flask, render_template, request, jsonify
import openpyxl
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['UPLOAD_FOLDER'] = '/tmp'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Procesar Excel
        wb = openpyxl.load_workbook(filepath)
        ws = wb.active
        
        data = []
        for row in ws.iter_rows(values_only=True):
            if row and any(cell is not None for cell in row):
                data.append(row)
        
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'rows': len(data),
            'data': data[:100]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
