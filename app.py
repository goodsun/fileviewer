from flask import Flask, request, jsonify, send_file, abort
import subprocess, os, mimetypes
from PIL import Image

app = Flask(__name__, static_folder='static', static_url_path='')

SEARCH_ROOTS = ['/home/alice', '/home/ec2-user']
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
MD_EXTS = {'.md'}
ALLOWED_EXTS = MD_EXTS | IMAGE_EXTS

def is_safe_path(path):
    path = os.path.realpath(path)
    return any(path.startswith(os.path.realpath(r)) for r in SEARCH_ROOTS)

@app.route('/api/files')
def list_files():
    results = []
    for root in SEARCH_ROOTS:
        if not os.path.exists(root):
            continue
        try:
            out = subprocess.check_output(
                ['find', root, '-type', 'f', '(',
                 '-name', '*.md',
                 '-o', '-name', '*.jpg', '-o', '-name', '*.jpeg',
                 '-o', '-name', '*.png', '-o', '-name', '*.gif',
                 '-o', '-name', '*.webp', '-o', '-name', '*.svg',
                 ')'],
                stderr=subprocess.DEVNULL, text=True
            )
            for line in out.strip().splitlines():
                if not line: continue
                ext = os.path.splitext(line)[1].lower()
                try:
                    stat = os.stat(line)
                    mtime = stat.st_mtime
                    ctime = stat.st_ctime
                    size  = stat.st_size
                except:
                    mtime = ctime = size = 0
                mime = mimetypes.guess_type(line)[0] or 'application/octet-stream'
                results.append({
                    'path': line,
                    'name': os.path.basename(line),
                    'type': 'image' if ext in IMAGE_EXTS else 'md',
                    'dir': os.path.dirname(line),
                    'mtime': mtime,
                    'ctime': ctime,
                    'size': size,
                    'mime': mime,
                })
        except Exception:
            pass
    results.sort(key=lambda x: x['path'])
    return jsonify(results)

@app.route('/api/file')
def get_file():
    path = request.args.get('path', '')
    if not path or not is_safe_path(path):
        abort(403)
    if not os.path.isfile(path):
        abort(404)
    ext = os.path.splitext(path)[1].lower()
    if ext not in ALLOWED_EXTS:
        abort(403)
    if ext in IMAGE_EXTS:
        mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        return send_file(path, mimetype=mime)
    with open(path, 'r', errors='replace') as f:
        return f.read(), 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/api/file', methods=['DELETE'])
def delete_file():
    path = request.args.get('path', '')
    if not path or not is_safe_path(path):
        abort(403)
    if not os.path.isfile(path):
        abort(404)
    ext = os.path.splitext(path)[1].lower()
    if ext not in ALLOWED_EXTS:
        abort(403)
    os.remove(path)
    return jsonify({'ok': True, 'deleted': path})

@app.route('/api/compress', methods=['POST'])
def compress_file():
    path = request.args.get('path', '')
    if not path or not is_safe_path(path):
        abort(403)
    if not os.path.isfile(path):
        abort(404)
    ext = os.path.splitext(path)[1].lower()
    if ext not in IMAGE_EXTS or ext == '.svg':
        abort(400)
    before = os.path.getsize(path)
    try:
        img = Image.open(path).convert('RGB')
        out_path = os.path.splitext(path)[0] + '.jpg'
        img.save(out_path, 'JPEG', quality=85, optimize=True)
        # 元がjpg以外なら元ファイルを削除
        if path != out_path:
            os.remove(path)
        after = os.path.getsize(out_path)
        return jsonify({'ok': True, 'before': before, 'after': after, 'path': out_path})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8850)
