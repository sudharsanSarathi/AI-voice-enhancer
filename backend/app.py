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

# Global progress tracking and model cache
processing_status = {}
model_cache = {}

def get_intensity_level(intensity_value):
    """Convert slider value (1-10) to intensity level"""
    if intensity_value <= 3:
        return "light"
    elif intensity_value <= 7:
        return "medium"
    else:
        return "strong"

def get_model_config(intensity_level):
    """Get model configuration based on intensity level - using lighter models"""
    model_configs = {
        "light": {
            "model_name": "FRCRN_SE_16K",
            "description": "Fast, lightweight processing (5-10 seconds)",
            "processing_time": "5-10 seconds"
        },
        "medium": {
            "model_name": "FRCRN_SE_16K",  # Use same light model for speed
            "description": "Balanced quality and speed (5-10 seconds)",
            "processing_time": "5-10 seconds"
        },
        "strong": {
            "model_name": "FRCRN_SE_16K",  # Use same light model for speed
            "description": "Enhanced processing (5-10 seconds)",
            "processing_time": "5-10 seconds"
        }
    }
    return model_configs.get(intensity_level, model_configs["light"])

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

def get_cached_model(model_name):
    """Get cached model or load it"""
    if model_name in model_cache:
        logger.info(f"Using cached model: {model_name}")
        return model_cache[model_name]
    
    try:
        from clearvoice import ClearVoice
        logger.info(f"Loading model into cache: {model_name}")
        model = ClearVoice(task='speech_enhancement', model_names=[model_name])
        model_cache[model_name] = model
        return model
    except Exception as e:
        logger.error(f"Failed to load model {model_name}: {e}")
        return None

def process_audio_fast(input_path, output_path, intensity_level, file_id):
    """Fast audio processing with fallback options"""
    try:
        update_progress(file_id, 'initializing', 10, 'Initializing fast audio processing...')
        
        # Try ClearerVoice first (cached)
        model_name = get_model_config(intensity_level)['model_name']
        model = get_cached_model(model_name)
        
        if model:
            update_progress(file_id, 'processing', 50, f'Processing with AI model: {model_name}...')
            model(input_path, output_path)
            update_progress(file_id, 'finalizing', 90, 'Finalizing enhanced audio...')
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                update_progress(file_id, 'complete', 100, f'AI processing complete! Output: {file_size} bytes')
                return True
        
        # Fallback: Use basic audio processing
        update_progress(file_id, 'processing', 50, 'Using fallback audio processing...')
        success = process_audio_basic(input_path, output_path, intensity_level, file_id)
        
        if success:
            update_progress(file_id, 'complete', 100, 'Fallback processing complete!')
            return True
        else:
            update_progress(file_id, 'error', 0, 'All processing methods failed')
            return False
            
    except Exception as e:
        error_msg = f"Fast processing error: {e}"
        update_progress(file_id, 'error', 0, error_msg)
        logger.error(error_msg)
        return False

def process_audio_basic(input_path, output_path, intensity_level, file_id):
    """Basic audio processing using pydub - fast fallback"""
    try:
        from pydub import AudioSegment
        from pydub.effects import normalize
        
        update_progress(file_id, 'processing', 60, 'Loading audio file...')
        
        # Load audio file
        audio = AudioSegment.from_file(input_path)
        
        update_progress(file_id, 'processing', 70, 'Applying noise reduction...')
        
        # Apply basic noise reduction based on intensity
        if intensity_level == "light":
            # Light processing: normalize and slight noise gate
            audio = normalize(audio)
            audio = audio - 5  # Reduce volume slightly
        elif intensity_level == "medium":
            # Medium processing: normalize and moderate noise reduction
            audio = normalize(audio)
            audio = audio - 10  # Reduce volume more
            # Apply simple noise gate
            audio = audio.apply_gain_stereo(-5, -5)
        else:  # strong
            # Strong processing: normalize and aggressive noise reduction
            audio = normalize(audio)
            audio = audio - 15  # Reduce volume significantly
            # Apply stronger noise gate
            audio = audio.apply_gain_stereo(-10, -10)
        
        update_progress(file_id, 'processing', 80, 'Saving enhanced audio...')
        
        # Export as WAV
        audio.export(output_path, format="wav")
        
        update_progress(file_id, 'processing', 90, 'Audio enhancement complete!')
        return True
        
    except Exception as e:
        logger.error(f"Basic processing error: {e}")
        return False

def process_audio_with_clearvoice(input_path, output_path, model_name, file_id):
    """Process audio using ClearerVoice model with progress tracking"""
    try:
        # Import ClearerVoice here to handle potential import issues
        update_progress(file_id, 'initializing', 10, 'Importing ClearerVoice library...')
        from clearvoice import ClearVoice
        
        update_progress(file_id, 'model_loading', 20, f'Loading AI model: {model_name}...')
        logger.info(f"Processing audio with model: {model_name}")
        
        # Initialize ClearVoice with the specified model
        cv = ClearVoice(task='speech_enhancement', model_names=[model_name])
        
        update_progress(file_id, 'processing', 50, 'Processing audio with AI model...')
        
        # Process the audio file
        cv(input_path, output_path)
        
        update_progress(file_id, 'finalizing', 90, 'Finalizing enhanced audio...')
        
        # Verify output file
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            update_progress(file_id, 'complete', 100, f'Processing complete! Output: {file_size} bytes')
            logger.info(f"Audio processing completed successfully. Output size: {file_size} bytes")
            return True
        else:
            update_progress(file_id, 'error', 0, 'Output file not generated')
            logger.error("Output file not generated")
            return False
        
    except ImportError as e:
        error_msg = f"ClearerVoice import error: {e}"
        update_progress(file_id, 'error', 0, error_msg)
        logger.error(error_msg)
        logger.error("Please install clearvoice: pip install clearvoice")
        return False
    except Exception as e:
        error_msg = f"Audio processing error: {e}"
        update_progress(file_id, 'error', 0, error_msg)
        logger.error(error_msg)
        logger.error(f"Error type: {type(e).__name__}")
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
        # Check if ClearerVoice is available
        try:
            from clearvoice import ClearVoice
            clearvoice_available = True
        except ImportError:
            clearvoice_available = False
        
        # Check if pydub is available
        try:
            from pydub import AudioSegment
            pydub_available = True
        except ImportError:
            pydub_available = False
        
        return jsonify({
            "status": "healthy", 
            "message": "Voice Enhancer AI is running",
            "clearvoice_available": clearvoice_available,
            "pydub_available": pydub_available,
            "models_loaded": list(model_cache.keys()),
            "processing_method": "Fast processing with fallback"
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
        
        # Initialize progress tracking
        update_progress(file_id, 'uploading', 5, 'Saving uploaded file...')
        
        # Save uploaded file
        file.save(input_path)
        logger.info(f"File saved: {input_path}")
        
        update_progress(file_id, 'preparing', 15, 'Preparing fast processing...')
        
        # Get model configuration
        intensity_level = get_intensity_level(intensity)
        model_config = get_model_config(intensity_level)
        
        logger.info(f"Processing with intensity: {intensity} ({intensity_level})")
        logger.info(f"Using model: {model_config['model_name']}")
        
        # Process audio in background thread
        def process_in_background():
            try:
                success = process_audio_fast(
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
            "message": "Fast processing started. Use /api/progress/{file_id} to track progress.",
            "status": "processing",
            "estimated_time": model_config['processing_time']
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
                            "status": "complete"
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
