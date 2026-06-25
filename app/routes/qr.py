from flask import Blueprint, send_file, request
from flask_login import login_required
import qrcode
import io

# Import VIP Bouncer (if you want to restrict QR generation to librarians only)
try:
    from app.utils import role_required
except ImportError:
    def role_required(*roles):
        def decorator(f):
            return f
        return decorator

qr_bp = Blueprint('qr', __name__, url_prefix='/qr')

@qr_bp.route('/copy/<int:copy_id>')
@login_required
@role_required('admin', 'librarian')
def generate_copy_qr(copy_id):
    """
    Generates a PNG QR code containing a secure inventory string.
    Designed to be scanned by USB 2D Scanners directly into desktop text fields.
    """
    # 1. Define the secure inventory payload (Instead of a URL!)
    # When scanned by a USB scanner, it will type "LIBRA-COPY-X" and hit Enter.
    target_data = f"LIBRA-COPY-{copy_id}"
    
    # 2. Configure the QR Code generator
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=4,
    )
    
    # 3. Embed the raw text string into the QR code
    qr.add_data(target_data)
    qr.make(fit=True)

    # 4. Create the visual image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 5. Save it to an in-memory buffer
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    # 6. Serve the raw image directly to the browser
    return send_file(img_buffer, mimetype='image/png')