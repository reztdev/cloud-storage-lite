from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import shutil
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YWRtaW5fczNjcjN0OTk='
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'storage'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

db = SQLAlchemy(app)

# Model untuk user
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    storage_path = db.Column(db.String(200), nullable=False)
    
    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)
        self.storage_path = os.path.join(app.config['UPLOAD_FOLDER'], username)
        
        # Membuat folder storage untuk user baru
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

# Pastikan database dan folder storage ada
with app.app_context():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    db.create_all()

# Fungsi helper untuk cek login
def is_logged_in():
    return 'username' in session

# Route untuk halaman utama
@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('file_manager'))
    return render_template('login.html')

# Route untuk login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['username'] = username
            session['user_path'] = user.storage_path
            flash('Login berhasil!', 'success')
            return redirect(url_for('file_manager'))
        else:
            flash('Username atau password salah!', 'danger')
    
    return render_template('login.html')

# Route untuk registrasi
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            flash('Username sudah digunakan!', 'danger')
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

# Route untuk logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Route untuk file manager
@app.route('/file_manager')
def file_manager():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    username = session['username']
    user_path = session['user_path']
    current_dir = request.args.get('dir', '')
    
    # Path absolut dari direktori saat ini
    absolute_dir = os.path.join(user_path, current_dir)
    
    # Pastikan tidak bisa akses di luar folder user
    if not absolute_dir.startswith(user_path):
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('file_manager'))
    
    # Dapatkan daftar file dan folder
    files = []
    folders = []
    
    if os.path.exists(absolute_dir):
        for item in os.listdir(absolute_dir):
            item_path = os.path.join(absolute_dir, item)
            item_rel_path = os.path.join(current_dir, item) if current_dir else item
            
            if os.path.isdir(item_path):
                folders.append({
                    'name': item,
                    'path': item_rel_path,
                    'date_modified': datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%Y-%m-%d %H:%M:%S')
                })
            else:
                size = os.path.getsize(item_path)
                files.append({
                    'name': item,
                    'path': item_rel_path,
                    'size': size,
                    'size_formatted': format_size(size),
                    'date_modified': datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%Y-%m-%d %H:%M:%S')
                })
    
    # Info untuk navigasi parent folder
    parent_dir = os.path.dirname(current_dir) if current_dir else None
    
    return render_template('file_manager.html', 
                           files=files, 
                           folders=folders, 
                           current_dir=current_dir,
                           parent_dir=parent_dir,
                           username=username)

# Format ukuran file (contoh: 1.2 MB)
def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"

# Route untuk upload file
@app.route('/upload', methods=['POST'])
def upload_file():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    current_dir = request.form.get('current_dir', '')
    upload_path = os.path.join(session['user_path'], current_dir)
    
    # Pastikan direktori tujuan valid
    if not upload_path.startswith(session['user_path']):
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('file_manager'))
    
    # Upload file
    if 'file' not in request.files:
        flash('Tidak ada file yang dipilih!', 'danger')
    else:
        file = request.files['file']
        if file.filename == '':
            flash('Tidak ada file yang dipilih!', 'danger')
        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join(upload_path, filename))
            flash(f'File {filename} berhasil diupload!', 'success')
    
    return redirect(url_for('file_manager', dir=current_dir))

# Route untuk download file
@app.route('/download')
def download_file():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    filepath = request.args.get('file', '')
    fullpath = os.path.join(session['user_path'], filepath)
    
    # Pastikan file yang akan didownload valid
    if not fullpath.startswith(session['user_path']) or not os.path.isfile(fullpath):
        flash('File tidak valid!', 'danger')
        return redirect(url_for('file_manager'))
    
    filename = os.path.basename(fullpath)
    return send_file(fullpath, as_attachment=True, download_name=filename)

# Route untuk membuat folder baru
@app.route('/create_folder', methods=['POST'])
def create_folder():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    folder_name = secure_filename(request.form['folder_name'])
    current_dir = request.form.get('current_dir', '')
    
    if not folder_name:
        flash('Nama folder tidak boleh kosong!', 'danger')
    else:
        new_folder_path = os.path.join(session['user_path'], current_dir, folder_name)
        
        # Pastikan path valid
        parent_dir = os.path.join(session['user_path'], current_dir)
        if not parent_dir.startswith(session['user_path']):
            flash('Akses ditolak!', 'danger')
        elif os.path.exists(new_folder_path):
            flash(f'Folder {folder_name} sudah ada!', 'danger')
        else:
            os.makedirs(new_folder_path)
            flash(f'Folder {folder_name} berhasil dibuat!', 'success')
    
    return redirect(url_for('file_manager', dir=current_dir))

# Route untuk rename file/folder
@app.route('/rename', methods=['POST'])
def rename():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    old_name = request.form['old_name']
    new_name = secure_filename(request.form['new_name'])
    current_dir = request.form.get('current_dir', '')
    
    if not new_name:
        flash('Nama baru tidak boleh kosong!', 'danger')
    else:
        old_path = os.path.join(session['user_path'], current_dir, old_name)
        new_path = os.path.join(session['user_path'], current_dir, new_name)
        
        # Pastikan path valid
        if not old_path.startswith(session['user_path']):
            flash('Akses ditolak!', 'danger')
        elif not os.path.exists(old_path):
            flash(f'File/folder tidak ditemukan!', 'danger')
        elif os.path.exists(new_path):
            flash(f'File/folder {new_name} sudah ada!', 'danger')
        else:
            os.rename(old_path, new_path)
            flash(f'Rename dari {old_name} ke {new_name} berhasil!', 'success')
    
    return redirect(url_for('file_manager', dir=current_dir))

# Route untuk delete file/folder
@app.route('/delete', methods=['POST'])
def delete():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    item_name = request.form['item_name']
    current_dir = request.form.get('current_dir', '')
    
    item_path = os.path.join(session['user_path'], current_dir, item_name)
    
    # Pastikan path valid
    if not item_path.startswith(session['user_path']):
        flash('Akses ditolak!', 'danger')
    elif not os.path.exists(item_path):
        flash(f'File/folder tidak ditemukan!', 'danger')
    else:
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)
        flash(f'{item_name} berhasil dihapus!', 'success')
    
    return redirect(url_for('file_manager', dir=current_dir))

# Variabel untuk menyimpan file/folder yang akan di-copy/move
app.jinja_env.globals.update(clipboard={})

# Route untuk copy file/folder
@app.route('/copy', methods=['POST'])
def copy():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    item_name = request.form['item_name']
    current_dir = request.form.get('current_dir', '')
    
    # Simpan info clipboard di session
    session['clipboard'] = {
        'action': 'copy',
        'item_name': item_name,
        'source_dir': current_dir
    }
    
    flash(f'{item_name} ditandai untuk di-copy. Pilih folder tujuan dan klik paste.', 'info')
    return redirect(url_for('file_manager', dir=current_dir))

# Route untuk cut file/folder
@app.route('/cut', methods=['POST'])
def cut():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    item_name = request.form['item_name']
    current_dir = request.form.get('current_dir', '')
    
    # Simpan info clipboard di session
    session['clipboard'] = {
        'action': 'cut',
        'item_name': item_name,
        'source_dir': current_dir
    }
    
    flash(f'{item_name} ditandai untuk dipindahkan. Pilih folder tujuan dan klik paste.', 'info')
    return redirect(url_for('file_manager', dir=current_dir))

# Route untuk paste file/folder
@app.route('/paste', methods=['POST'])
def paste():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    current_dir = request.form.get('current_dir', '')
    
    # Pastikan ada item di clipboard
    if 'clipboard' not in session or not session['clipboard']:
        flash('Tidak ada item yang ditandai untuk di-copy/pindahkan!', 'danger')
        return redirect(url_for('file_manager', dir=current_dir))
    
    clipboard = session['clipboard']
    action = clipboard['action']
    item_name = clipboard['item_name']
    source_dir = clipboard['source_dir']
    
    source_path = os.path.join(session['user_path'], source_dir, item_name)
    target_path = os.path.join(session['user_path'], current_dir, item_name)
    
    # Pastikan path valid
    if not source_path.startswith(session['user_path']) or not os.path.join(session['user_path'], current_dir).startswith(session['user_path']):
        flash('Akses ditolak!', 'danger')
    elif not os.path.exists(source_path):
        flash(f'File/folder sumber tidak ditemukan!', 'danger')
    elif os.path.exists(target_path):
        # Jika file/folder sudah ada, tambahkan suffix
        base, ext = os.path.splitext(item_name)
        item_name = f"{base}_copy{ext}"
        target_path = os.path.join(session['user_path'], current_dir, item_name)
        
        if os.path.exists(target_path):
            # Tambahkan random suffix jika masih konflik
            random_suffix = uuid.uuid4().hex[:6]
            item_name = f"{base}_copy_{random_suffix}{ext}"
            target_path = os.path.join(session['user_path'], current_dir, item_name)
    
    try:
        if action == 'copy':
            if os.path.isdir(source_path):
                shutil.copytree(source_path, target_path)
            else:
                shutil.copy2(source_path, target_path)
            flash(f'{item_name} berhasil di-copy!', 'success')
        else:  # action == 'cut'
            shutil.move(source_path, target_path)
            flash(f'{item_name} berhasil dipindahkan!', 'success')
        
        # Hapus clipboard setelah selesai
        session.pop('clipboard', None)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('file_manager', dir=current_dir))

# Jalankan aplikasi
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)