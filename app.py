import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "pablo_hosting_secret_key_2026"

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'py', 'php', 'js', 'java', 'c', 'cpp', 'zip', 'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('لم يتم اختيار ملف!', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('اسم الملف فارغ!', 'error')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        flash(f'تم رفع الملف "{filename}" بنجاح 🚀', 'success')
    else:
        flash('صيغة الملف غير مدعومة!', 'error')
    
    return redirect(url_for('index'))

@app.route('/run/<filename>', methods=['POST'])
def run_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    ext = filename.rsplit('.', 1)[1].lower()
    output = ""

    try:
        if ext == 'py':
            result = subprocess.run(['python', filepath], capture_output=True, text=True, timeout=5)
            output = result.stdout if result.returncode == 0 else result.stderr
        elif ext == 'js':
            result = subprocess.run(['node', filepath], capture_output=True, text=True, timeout=5)
            output = result.stdout if result.returncode == 0 else result.stderr
        elif ext == 'php':
            result = subprocess.run(['php', filepath], capture_output=True, text=True, timeout=5)
            output = result.stdout if result.returncode == 0 else result.stderr
        else:
            output = f"التشغيل المباشر غير مدعوم لهذه الصيغة ({ext}) حالياً، الملف مرفوع وجاهز للاستخدام!"
    except Exception as e:
        output = f"حدث خطأ أثناء التشغيل: {str(e)}"

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files, output=output, active_file=filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
