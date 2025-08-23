from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import tempfile
import uuid
from pathlib import Path
import logging
from werkzeug.utils import secure_filename
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the absolute path to the project root
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_folder = os.path.join(project_root, 'static')
template_folder = os.path.join(project_root, 'frontend')

app = Flask(__name__, static_folder=static_folder, template_folder=template_folder)
app.config.from_object(Config)
CORS(app)

# Ensure directories exist
Config.UPLOAD_FOLDER.mkdir(exist_ok=True)
Config.PROCESSED_FOLDER.mkdir(exist_ok=True)

def get_intensity_level(intensity_value):
    """Convert slider value (1-10) to intensity level"""
    if intensity_value <= 3:
        return "light"
    elif intensity_value <= 7:
        return "medium"
    else:
        return "strong"

def get_model_config(intensity_level):
    """Get model configuration based on intensity level"""
    model_configs = {
        "light": {
            "model_name": "FRCRN_SE_16K",
            "description": "Fast, lightweight processing"
        },
        "medium": {
            "model_name": "MossFormer2_SE_48K", 
            "description": "Balanced quality and speed"
        },
        "strong": {
            "model_name": "MossFormerGAN_SE_16K",
            "description": "Best quality, more aggressive"
        }
    }
    return model_configs.get(intensity_level, model_configs["medium"])

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def process_audio_with_clearvoice(input_path, output_path, model_name):
    """Process audio using ClearerVoice model"""
    try:
        # Import ClearerVoice here to handle potential import issues
        from clearvoice import ClearVoice
        
        logger.info(f"Processing audio with model: {model_name}")
        
        # Initialize ClearVoice with the specified model
        cv = ClearVoice(task='speech_enhancement', model_names=[model_name])
        
        # Process the audio file
        cv(input_path, output_path)
        
        logger.info(f"Audio processing completed successfully")
        return True
        
    except ImportError as e:
        logger.error(f"ClearerVoice import error: {e}")
        logger.error("Please install clearvoice: pip install clearvoice")
        return False
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        return False

@app.route('/')
def index():
    """Serve the main application page"""
    try:
        return send_from_directory(template_folder, 'index.html')
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        # Fallback: try to render template directly
        from flask import render_template
        return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(static_folder, filename)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Voice Enhancer AI is running"})

@app.route('/api/process', methods=['POST'])
def process_audio():
    """Process uploaded audio file"""
    try:
        # Check if file is present
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        file = request.files['audio']
        intensity = int(request.form.get('intensity', 5))
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not supported"}), 400
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        original_extension = file.filename.rsplit('.', 1)[1].lower()
        input_filename = f"{file_id}_original.{original_extension}"
        output_filename = f"{file_id}_enhanced.wav"
        
        input_path = Config.UPLOAD_FOLDER / input_filename
        output_path = Config.PROCESSED_FOLDER / output_filename
        
        # Save uploaded file
        file.save(input_path)
        logger.info(f"File saved: {input_path}")
        
        # Get model configuration
        intensity_level = get_intensity_level(intensity)
        model_config = get_model_config(intensity_level)
        
        logger.info(f"Processing with intensity: {intensity} ({intensity_level})")
        logger.info(f"Using model: {model_config['model_name']}")
        
        # Process audio
        success = process_audio_with_clearvoice(
            str(input_path), 
            str(output_path), 
            model_config['model_name']
        )
        
        if not success:
            return jsonify({"error": "Audio processing failed"}), 500
        
        # Verify output file exists
        if not output_path.exists():
            return jsonify({"error": "Enhanced audio file not generated"}), 500
        
        return jsonify({
            "success": True,
            "file_id": file_id,
            "original_file": input_filename,
            "enhanced_file": output_filename,
            "intensity_level": intensity_level,
            "model_used": model_config['model_name'],
            "model_description": model_config['description']
        })
        
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route('/api/audio/uploads/<filename>')
def get_uploaded_audio(filename):
    """Serve uploaded audio files"""
    try:
        return send_from_directory(Config.UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.route('/api/audio/processed/<filename>')
def get_processed_audio(filename):
    """Serve processed audio files"""
    try:
        return send_from_directory(Config.PROCESSED_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.route('/api/download/<filename>')
def download_audio(filename):
    """Download processed audio file"""
    try:
        return send_from_directory(
            Config.PROCESSED_FOLDER, 
            filename, 
            as_attachment=True,
            download_name=f"enhanced_{filename}"
        )
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({"error": "File too large. Maximum size is 50MB."}), 413

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {e}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', Config.PORT))
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)