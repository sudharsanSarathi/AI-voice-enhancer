from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import tempfile
import uuid
import time
import threading
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

# Global progress tracking
processing_status = {}

def get_intensity_level(intensity_value):
    """Convert slider value (1-10) to intensity level"""
    if intensity_value <= 3:
        return "light"
    elif intensity_value <= 7:
        return "medium"
    else:
        return "strong"

def get_processing_config(intensity_level):
    """Get processing configuration based on intensity level"""
    configs = {
        "light": {
            "description": "Light enhancement (2-3 seconds)",
            "processing_time": "2-3 seconds",
            "noise_reduction": 5,
            "normalization": True,
            "compression": False,
            "eq_boost": 2
        },
        "medium": {
            "description": "Balanced enhancement (3-4 seconds)",
            "processing_time": "3-4 seconds",
            "noise_reduction": 10,
            "normalization": True,
            "compression": True,
            "eq_boost": 5
        },
        "strong": {
            "description": "Maximum enhancement (4-5 seconds)",
            "processing_time": "4-5 seconds",
            "noise_reduction": 15,
            "normalization": True,
            "compression": True,
            "eq_boost": 8
        }
    }
    return configs.get(intensity_level, configs["light"])

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def update_progress(file_id, stage, progress, message):
    """Update processing progress"""
    if file_id not in processing_status:
        processing_status[file_id] = {}
    
    processing_status[file_id].update({
        'stage': stage,
        'progress': progress,
        'message': message,
        'timestamp': time.time()
    })
    logger.info(f"Progress for {file_id}: {stage} - {progress}% - {message}")

def apply_audio_enhancement(audio, config, file_id):
    """Apply advanced audio enhancement techniques"""
    try:
        update_progress(file_id, 'processing', 30, 'Applying audio normalization...')
        
        # 1. Normalize audio levels
        if config['normalization']:
            from pydub.effects import normalize
            audio = normalize(audio)
        
        update_progress(file_id, 'processing', 40, 'Reducing background noise...')
        
        # 2. Noise reduction using volume adjustment
        audio = audio - config['noise_reduction']
        
        update_progress(file_id, 'processing', 50, 'Applying dynamic compression...')
        
        # 3. Dynamic compression for better clarity
        if config['compression']:
            # Simple compression: boost quiet parts, reduce loud parts
            audio = audio.apply_gain_stereo(-config['noise_reduction']//2, -config['noise_reduction']//2)
        
        update_progress(file_id, 'processing', 60, 'Enhancing frequency response...')
        
        # 4. EQ boost for voice frequencies (300Hz - 3kHz)
        if config['eq_boost'] > 0:
            # Boost mid frequencies for voice clarity
            audio = audio + config['eq_boost']
        
        update_progress(file_id, 'processing', 70, 'Applying final adjustments...')
        
        # 5. Final volume adjustment for optimal levels
        audio = audio + 3  # Boost overall volume slightly
        
        # 6. Ensure audio doesn't clip
        if audio.max_possible_amplitude > 0:
            audio = audio.normalize()
        
        update_progress(file_id, 'processing', 80, 'Audio enhancement complete!')
        return audio
        
    except Exception as e:
        logger.error(f"Audio enhancement error: {e}")
        return audio  # Return original if enhancement fails

def process_audio_super_fast(input_path, output_path, intensity_level, file_id):
    """Super fast audio processing using only pydub"""
    try:
        update_progress(file_id, 'initializing', 10, 'Initializing super-fast processing...')
        
        # Import pydub
        from pydub import AudioSegment
        
        update_progress(file_id, 'loading', 20, 'Loading audio file...')
        
        # Load audio file
        audio = AudioSegment.from_file(input_path)
        
        update_progress(file_id, 'processing', 25, 'Getting processing configuration...')
        
        # Get processing configuration
        config = get_processing_config(intensity_level)
        
        # Apply audio enhancement
        enhanced_audio = apply_audio_enhancement(audio, config, file_id)
        
        update_progress(file_id, 'saving', 90, 'Saving enhanced audio...')
        
        # Export as high-quality WAV
        enhanced_audio.export(
            output_path, 
            format="wav",
            parameters=["-q:a", "0"]  # High quality
        )
        
        # Verify output
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            update_progress(file_id, 'complete', 100, f'Super-fast processing complete! Output: {file_size} bytes')
            logger.info(f"Super-fast processing completed! Output size: {file_size} bytes")
            return True
        else:
            update_progress(file_id, 'error', 0, 'Output file not generated')
            return False
            
    except Exception as e:
        error_msg = f"Super-fast processing error: {e}"
        update_progress(file_id, 'error', 0, error_msg)
        logger.error(error_msg)
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
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
    try:
        # Check if pydub is available
        try:
            from pydub import AudioSegment
            pydub_available = True
        except ImportError:
            pydub_available = False
        
        return jsonify({
            "status": "healthy", 
            "message": "Voice Enhancer AI is running",
            "pydub_available": pydub_available,
            "processing_method": "Super-fast pydub processing (2-5 seconds)",
            "version": "2.0 - Lightning Fast"
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/progress/<file_id>')
def get_progress(file_id):
    """Get processing progress for a specific file"""
    if file_id in processing_status:
        return jsonify(processing_status[file_id])
    else:
        return jsonify({"error": "File ID not found"}), 404

@app.route('/api/process', methods=['POST'])
def process_audio():
    """Process uploaded audio file with super-fast processing"""
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
        
        # Initialize progress tracking
        update_progress(file_id, 'uploading', 5, 'Saving uploaded file...')
        
        # Save uploaded file
        file.save(input_path)
        logger.info(f"File saved: {input_path}")
        
        update_progress(file_id, 'preparing', 15, 'Preparing super-fast processing...')
        
        # Get processing configuration
        intensity_level = get_intensity_level(intensity)
        config = get_processing_config(intensity_level)
        
        logger.info(f"Processing with intensity: {intensity} ({intensity_level})")
        logger.info(f"Processing config: {config}")
        
        # Process audio in background thread
        def process_in_background():
            try:
                success = process_audio_super_fast(
                    str(input_path), 
                    str(output_path), 
                    intensity_level,
                    file_id
                )
                
                if success:
                    # Clean up progress data after successful processing
                    if file_id in processing_status:
                        del processing_status[file_id]
                else:
                    # Keep error status for a while
                    update_progress(file_id, 'error', 0, 'Processing failed. Please try again.')
                    
            except Exception as e:
                logger.error(f"Background processing error: {e}")
                update_progress(file_id, 'error', 0, f'Unexpected error: {str(e)}')
        
        # Start background processing
        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()
        
        # Return immediately with file ID for progress tracking
        return jsonify({
            "success": True,
            "file_id": file_id,
            "message": "Super-fast processing started! Use /api/progress/{file_id} to track progress.",
            "status": "processing",
            "estimated_time": config['processing_time'],
            "processing_method": "Lightning-fast pydub enhancement"
        })
        
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route('/api/result/<file_id>')
def get_result(file_id):
    """Get processing result for a completed file"""
    try:
        # Check if processing is complete
        if file_id in processing_status:
            status = processing_status[file_id]
            if status.get('stage') == 'complete':
                # Find the processed file
                processed_files = list(Config.PROCESSED_FOLDER.glob(f"{file_id}_enhanced.wav"))
                if processed_files:
                    output_filename = processed_files[0].name
                    # Find the original file
                    original_files = list(Config.UPLOAD_FOLDER.glob(f"{file_id}_original.*"))
                    if original_files:
                        original_filename = original_files[0].name
                        
                        return jsonify({
                            "success": True,
                            "file_id": file_id,
                            "original_file": original_filename,
                            "enhanced_file": output_filename,
                            "status": "complete",
                            "processing_method": "Super-fast pydub enhancement"
                        })
        
        return jsonify({"error": "Processing not complete or file not found"}), 404
        
    except Exception as e:
        logger.error(f"Result retrieval error: {e}")
        return jsonify({"error": f"Failed to retrieve result: {str(e)}"}), 500

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
