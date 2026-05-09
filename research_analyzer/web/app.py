from flask import Flask, send_file, render_template
import qrcode
from datetime import datetime
import os
import logging
from ..core.paper_analyzer import PaperAnalyzer
from ..core.report_generator import generate_report
from ..utils.error_handler import handle_error

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
QR_CODE_PATH = os.path.join(RESULTS_DIR, 'qr_code.png')

def generate_qr_code(url):
    """Generate QR code for the given URL"""
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image.save(QR_CODE_PATH)
        return QR_CODE_PATH
    except Exception as e:
        error_msg = f"Error generating QR code: {str(e)}"
        logger.error(error_msg)
        handle_error(error_msg)
        return None

def get_latest_report():
    """Get the path to the latest report"""
    try:
        reports = [f for f in os.listdir(RESULTS_DIR) if f.endswith('.pdf')]
        if not reports:
            return None
        latest_report = max(reports, key=lambda x: os.path.getctime(os.path.join(RESULTS_DIR, x)))
        return os.path.join(RESULTS_DIR, latest_report)
    except Exception as e:
        error_msg = f"Error getting latest report: {str(e)}"
        logger.error(error_msg)
        handle_error(error_msg)
        return None

@app.route('/')
def home():
    """Home page with QR code display"""
    latest_report = get_latest_report()
    if latest_report:
        report_url = f"/download/{os.path.basename(latest_report)}"
        qr_code_path = generate_qr_code(f"http://your-domain.com{report_url}")
        return render_template('home.html', 
                             qr_code=qr_code_path, 
                             report_date=datetime.fromtimestamp(os.path.getctime(latest_report)).strftime("%Y-%m-%d"))
    return "No reports available", 404

@app.route('/download/<filename>')
def download_report(filename):
    """Download the latest report"""
    try:
        return send_file(os.path.join(RESULTS_DIR, filename),
                        mimetype='application/pdf',
                        as_attachment=True,
                        download_name=filename)
    except Exception as e:
        error_msg = f"Error downloading report: {str(e)}"
        logger.error(error_msg)
        handle_error(error_msg)
        return "Error downloading report", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
