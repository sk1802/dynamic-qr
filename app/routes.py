import os
import uuid
import psycopg2
from flask import (Blueprint, render_template, request, 
                   redirect, flash, send_from_directory, abort)
from io import BytesIO
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode

bp = Blueprint('main', __name__)

def get_db():
    print(os.environ.get('DATABASE_URL'))
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/generate', methods=['POST'])
def generate():
    url = request.form.get('url')
    if not url:
        flash('Please enter a URL')
        return redirect('/')
    
    conn = get_db()
    cur = conn.cursor()
    qr_id = str(uuid.uuid4())
    
    try:
        # Generate QR
        qr = qrcode.make(f"{os.environ['BASE_URL']}/redirect/{qr_id}")
        upload_dir = os.path.join(os.path.dirname(__file__), 'static/qrcodes')
        os.makedirs(upload_dir, exist_ok=True)
        qr.save(f"{upload_dir}/{qr_id}.png")

        # # Save to DB
        cur.execute("""
            INSERT INTO qr_codes (id, target_url) 
            VALUES (%s, %s)
        """, (qr_id, url))
        conn.commit()
        
        return redirect(f'/qr/{qr_id}')
        
    except Exception as e:
        conn.rollback()
        flash('Error generating QR')
        return redirect('/')
    finally:
        cur.close()
        conn.close()

@bp.route('/qr/<qr_id>')
def show_qr(qr_id):
    return render_template('display_qr.html', qr_id=qr_id)

@bp.route('/download/<qr_id>')
def download(qr_id):
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), 'static/qrcodes'),
        f"{qr_id}.png",
        as_attachment=True,
        download_name="qr_code.png"
    )


@bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file uploaded')
        return redirect('/')
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect('/')
    
    try:
        # Read QR code
        img = Image.open(BytesIO(file.read()))
        decoded = decode(img)
        if not decoded:
            flash('No QR code found in image')
            return redirect('/')
        
        redirect_url = decoded[0].data.decode('utf-8')
        qr_id = redirect_url.split('/')[-1]
        
        # Verify QR exists in database
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT target_url FROM qr_codes WHERE id = %s", (qr_id,))
        result = cur.fetchone()
        
        if not result:
            flash('QR code not found in database')
            return redirect('/')
            
        return render_template('update.html', 
                            qr_id=qr_id, 
                            current_url=result[0])
        
    except Exception as e:
        app.logger.error(f"Upload error: {str(e)}")
        flash('Error processing QR code')
        return redirect('/')
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()
        
@bp.route('/redirect/<qr_id>')
def redirect_url(qr_id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT target_url FROM qr_codes WHERE id = %s", (qr_id,))
        result = cur.fetchone()
        return redirect(result[0]) if result else abort(404)
    finally:
        cur.close()
        conn.close()

@bp.route('/update', methods=['POST'])
def update():
    qr_id = request.form.get('qr_id')
    new_url = request.form.get('new_url')
    
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE qr_codes 
            SET target_url = %s 
            WHERE id = %s
        """, (new_url, qr_id))
        conn.commit()
        flash('URL updated successfully')
        return redirect('/')
    except:
        conn.rollback()
        flash('Update failed')
        return redirect('/')
    finally:
        cur.close()
        conn.close()

@bp.after_request
def add_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response