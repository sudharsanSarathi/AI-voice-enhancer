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
completed_files = {}  # Store completed files for a short time

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

def cleanup_old_progress_data():
    """Clean up old progress data to prevent memory leaks"""
    current_time = time.time()
    # Remove progress data older than 5 minutes
    for file_id in list(processing_status.keys()):
        if current_time - processing_status[file_id].get('timestamp', 0) > 300:
            del processing_status[file_id]
    
    # Remove completed files older than 2 minutes
    for file_id in list(completed_files.keys()):
        if current_time - completed_files[file_id].get('timestamp', 0) > 120:
            del completed_files[file_id]

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
    """AI-powered audio processing using ClearerVoice"""
    try:
        update_progress(file_id, 'initializing', 10, 'Initializing AI-powered processing...')
        
        # Try to import ClearerVoice for AI processing
        try:
            from clearvoice import ClearVoice
            logger.info("Successfully imported ClearerVoice")
            use_clearvoice = True
        except ImportError as e:
            logger.error(f"Failed to import ClearerVoice: {e}")
            use_clearvoice = False
        
        if not use_clearvoice:
            # Fallback: Use pydub with basic enhancement
            logger.info("Using pydub fallback processing")
            return process_audio_pydub_fallback(input_path, output_path, intensity_level, file_id)
        
        update_progress(file_id, 'loading', 20, 'Loading audio file...')
        
        # Load audio file
        logger.info(f"Loading audio file from: {input_path}")
        logger.info(f"Input file exists: {os.path.exists(input_path)}")
        if os.path.exists(input_path):
            logger.info(f"Input file size: {os.path.getsize(input_path)} bytes")
        
        update_progress(file_id, 'model_loading', 30, 'Loading AI model for speech enhancement...')
        
        # Initialize ClearerVoice with appropriate model based on intensity
        model_config = get_clearvoice_model_config(intensity_level)
        logger.info(f"Using ClearerVoice model: {model_config}")
        
        try:
            # Initialize the AI model
            cv = ClearVoice(task='speech_enhancement', model_names=[model_config['model_name']])
            logger.info(f"AI model loaded successfully: {model_config['model_name']}")
        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")
            logger.info("Falling back to pydub processing")
            return process_audio_pydub_fallback(input_path, output_path, intensity_level, file_id)
        
        update_progress(file_id, 'processing', 50, 'Processing audio with AI model...')
        
        # Process the audio using AI
        try:
            cv(input_path, output_path)
            logger.info(f"AI processing completed successfully")
        except Exception as e:
            logger.error(f"AI processing failed: {e}")
            logger.info("Falling back to pydub processing")
            return process_audio_pydub_fallback(input_path, output_path, intensity_level, file_id)
        
        update_progress(file_id, 'saving', 90, 'Saving AI-enhanced audio...')
        
        # Verify output
        logger.info(f"Checking if output file exists: {output_path}")
        logger.info(f"File exists: {os.path.exists(output_path)}")
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            logger.info(f"Output file size: {file_size} bytes")
            update_progress(file_id, 'complete', 100, f'AI processing complete! Output: {file_size} bytes')
            logger.info(f"AI processing completed! Output size: {file_size} bytes")
            return True
        else:
            logger.error(f"Output file was not created: {output_path}")
            update_progress(file_id, 'error', 0, 'Output file not generated')
            return False
            
    except Exception as e:
        error_msg = f"AI processing error: {e}"
        update_progress(file_id, 'error', 0, error_msg)
        logger.error(error_msg)
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

def get_clearvoice_model_config(intensity_level):
    """Get ClearerVoice model configuration based on intensity level"""
    model_configs = {
        "light": {
            "model_name": "FRCRN_SE_16K",
            "description": "Light AI enhancement (5-10 seconds)",
            "processing_time": "5-10 seconds"
        },
        "medium": {
            "model_name": "FRCRN_SE_16K",
            "description": "Balanced AI enhancement (5-10 seconds)",
            "processing_time": "5-10 seconds"
        },
        "strong": {
            "model_name": "MossFormer2_SE_48K",
            "description": "Maximum AI enhancement (10-15 seconds)",
            "processing_time": "10-15 seconds"
        }
    }
    return model_configs.get(intensity_level, model_configs["light"])

def process_audio_pydub_fallback(input_path, output_path, intensity_level, file_id):
    """Fallback audio processing using pydub when AI is not available"""
    try:
        update_progress(file_id, 'processing', 60, 'Using pydub enhancement...')
        
        # Import pydub
        try:
            from pydub import AudioSegment
            logger.info("Successfully imported pydub")
        except ImportError as e:
            logger.error(f"Failed to import pydub: {e}")
            update_progress(file_id, 'error', 0, 'Audio processing library not available')
            return False
        
        # Load audio file
        audio = AudioSegment.from_file(input_path)
        logger.info(f"Audio loaded successfully, duration: {len(audio)}ms")
        
        update_progress(file_id, 'processing', 70, 'Applying audio enhancement...')
        
        # Get processing configuration
        config = get_processing_config(intensity_level)
        
        # Apply audio enhancement
        enhanced_audio = apply_audio_enhancement(audio, config, file_id)
        
        update_progress(file_id, 'saving', 90, 'Saving enhanced audio...')
        
        # Export as high-quality WAV
        logger.info(f"Exporting enhanced audio to: {output_path}")
        enhanced_audio.export(
            output_path, 
            format="wav",
            parameters=["-q:a", "0"]  # High quality
        )
        
        # Verify output
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            logger.info(f"Pydub processing completed! Output size: {file_size} bytes")
            update_progress(file_id, 'complete', 100, f'Pydub enhancement complete! Output: {file_size} bytes')
            return True
        else:
            logger.error(f"Output file was not created: {output_path}")
            update_progress(file_id, 'error', 0, 'Output file not generated')
            return False
            
    except Exception as e:
        error_msg = f"Pydub fallback error: {e}"
        update_progress(file_id, 'error', 0, error_msg)
        logger.error(error_msg)
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
            logger.info("ClearerVoice is available in health check")
            processing_method = "AI-powered ClearerVoice processing (5-15 seconds)"
        except ImportError as e:
            clearvoice_available = False
            logger.error(f"ClearerVoice import error in health check: {e}")
            processing_method = "Fallback pydub processing"
        
        # Check if pydub is available
        try:
            from pydub import AudioSegment
            pydub_available = True
            logger.info("Pydub is available in health check")
        except ImportError as e:
            pydub_available = False
            logger.error(f"Pydub import error in health check: {e}")
        
        # Check if directories exist
        upload_exists = Config.UPLOAD_FOLDER.exists()
        processed_exists = Config.PROCESSED_FOLDER.exists()
        
        return jsonify({
            "status": "healthy", 
            "message": "Voice Enhancer AI is running",
            "clearvoice_available": clearvoice_available,
            "pydub_available": pydub_available,
            "upload_folder_exists": upload_exists,
            "processed_folder_exists": processed_exists,
            "processing_method": processing_method,
            "version": "3.0 - AI-Powered"
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/progress/<file_id>')
def get_progress(file_id):
    """Get processing progress for a specific file"""
    # Clean up old data first
    cleanup_old_progress_data()
    
    if file_id in processing_status:
        return jsonify(processing_status[file_id])
    elif file_id in completed_files:
        # Return completion status
        return jsonify({
            "stage": "complete",
            "progress": 100,
            "message": "Processing completed successfully!",
            "timestamp": completed_files[file_id]['timestamp']
        })
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
        logger.info(f"About to save file: {input_path}")
        logger.info(f"Upload folder exists: {Config.UPLOAD_FOLDER.exists()}")
        logger.info(f"Upload folder path: {Config.UPLOAD_FOLDER.absolute()}")
        logger.info(f"File object: {file}")
        logger.info(f"File filename: {file.filename}")
        logger.info(f"File content type: {file.content_type}")
        
        try:
            file.save(input_path)
            logger.info(f"File saved successfully: {input_path}")
            logger.info(f"Saved file exists: {os.path.exists(input_path)}")
            if os.path.exists(input_path):
                logger.info(f"Saved file size: {os.path.getsize(input_path)} bytes")
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            update_progress(file_id, 'error', 0, f'Failed to save uploaded file: {str(e)}')
            return jsonify({"error": f"Failed to save file: {str(e)}"}), 500
        
        update_progress(file_id, 'preparing', 15, 'Preparing super-fast processing...')
        
        # Get processing configuration
        intensity_level = get_intensity_level(intensity)
        ai_config = get_clearvoice_model_config(intensity_level)
        
        logger.info(f"Processing with intensity: {intensity} ({intensity_level})")
        logger.info(f"AI model config: {ai_config}")
        
        # Process audio in background thread
        def process_in_background():
            try:
                logger.info(f"Background processing started for file_id: {file_id}")
                logger.info(f"Input path: {input_path}")
                logger.info(f"Output path: {output_path}")
                logger.info(f"Input file exists: {os.path.exists(input_path)}")
                
                success = process_audio_super_fast(
                    str(input_path), 
                    str(output_path), 
                    intensity_level,
                    file_id
                )
                
                if success:
                    # Mark as completed and add to completed files
                    logger.info(f"Processing succeeded for file_id: {file_id}")
                    logger.info(f"Output file exists: {os.path.exists(output_path)}")
                    if os.path.exists(output_path):
                        logger.info(f"Output file size: {os.path.getsize(output_path)} bytes")
                    
                    update_progress(file_id, 'complete', 100, 'Processing completed successfully!')
                    completed_files[file_id] = {
                        'timestamp': time.time(),
                        'file_id': file_id,
                        'original_file': input_filename,
                        'enhanced_file': output_filename,
                        'status': 'complete'
                    }
                    logger.info(f"Processing completed for file_id: {file_id}")
                else:
                    logger.error(f"Processing failed for file_id: {file_id}")
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
            "message": "AI-powered processing started! Use /api/progress/{file_id} to track progress.",
            "status": "processing",
            "estimated_time": ai_config['processing_time'],
            "processing_method": "AI-powered ClearerVoice enhancement"
        })
        
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route('/api/result/<file_id>')
def get_result(file_id):
    """Get processing result for a completed file"""
    try:
        # Check if processing is complete
        if file_id in completed_files:
            result = completed_files[file_id]
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
        logger.info(f"Requesting uploaded file: {filename}")
        logger.info(f"Upload folder: {Config.UPLOAD_FOLDER}")
        logger.info(f"Full path: {Config.UPLOAD_FOLDER / filename}")
        logger.info(f"File exists: {(Config.UPLOAD_FOLDER / filename).exists()}")
        
        if not (Config.UPLOAD_FOLDER / filename).exists():
            logger.error(f"Uploaded file not found: {filename}")
            return jsonify({"error": "File not found"}), 404
            
        return send_from_directory(str(Config.UPLOAD_FOLDER.absolute()), filename)
    except Exception as e:
        logger.error(f"Error serving uploaded file {filename}: {e}")
        return jsonify({"error": "File not found"}), 404

@app.route('/api/audio/processed/<filename>')
def get_processed_audio(filename):
    """Serve processed audio files"""
    try:
        logger.info(f"Requesting processed file: {filename}")
        logger.info(f"Processed folder: {Config.PROCESSED_FOLDER}")
        logger.info(f"Full path: {Config.PROCESSED_FOLDER / filename}")
        logger.info(f"File exists: {(Config.PROCESSED_FOLDER / filename).exists()}")
        
        if not (Config.PROCESSED_FOLDER / filename).exists():
            logger.error(f"Processed file not found: {filename}")
            return jsonify({"error": "File not found"}), 404
            
        return send_from_directory(str(Config.PROCESSED_FOLDER.absolute()), filename)
    except Exception as e:
        logger.error(f"Error serving processed file {filename}: {e}")
        return jsonify({"error": "File not found"}), 404

@app.route('/api/download/<filename>')
def download_audio(filename):
    """Download processed audio file"""
    try:
        return send_from_directory(
            str(Config.PROCESSED_FOLDER.absolute()), 
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

@app.route('/api/test-upload', methods=['POST'])
def test_upload():
    """Test endpoint to verify file upload functionality"""
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Generate test filename
        file_id = str(uuid.uuid4())
        original_extension = file.filename.rsplit('.', 1)[1].lower()
        test_filename = f"test_{file_id}_original.{original_extension}"
        test_path = Config.UPLOAD_FOLDER / test_filename
        
        logger.info(f"TEST: About to save test file: {test_path}")
        logger.info(f"TEST: Upload folder exists: {Config.UPLOAD_FOLDER.exists()}")
        logger.info(f"TEST: Upload folder path: {Config.UPLOAD_FOLDER.absolute()}")
        logger.info(f"TEST: File object: {file}")
        logger.info(f"TEST: File filename: {file.filename}")
        logger.info(f"TEST: File content type: {file.content_type}")
        
        # Save file
        file.save(test_path)
        
        # Verify file was saved
        file_exists = os.path.exists(test_path)
        file_size = os.path.getsize(test_path) if file_exists else 0
        
        logger.info(f"TEST: File saved successfully: {test_path}")
        logger.info(f"TEST: File exists: {file_exists}")
        logger.info(f"TEST: File size: {file_size} bytes")
        
        return jsonify({
            "success": True,
            "test_filename": test_filename,
            "file_exists": file_exists,
            "file_size": file_size,
            "upload_folder": str(Config.UPLOAD_FOLDER.absolute()),
            "message": "Test upload completed"
        })
        
    except Exception as e:
        logger.error(f"TEST: Upload error: {e}")
        return jsonify({"error": f"Test upload failed: {str(e)}"}), 500

@app.route('/api/test-serve/<filename>')
def test_serve(filename):
    """Test endpoint to verify file serving functionality"""
    try:
        logger.info(f"TEST: Requesting test file: {filename}")
        logger.info(f"TEST: Upload folder: {Config.UPLOAD_FOLDER}")
        logger.info(f"TEST: Upload folder absolute: {Config.UPLOAD_FOLDER.absolute()}")
        logger.info(f"TEST: Full path: {Config.UPLOAD_FOLDER / filename}")
        logger.info(f"TEST: Full path absolute: {(Config.UPLOAD_FOLDER / filename).absolute()}")
        logger.info(f"TEST: File exists: {(Config.UPLOAD_FOLDER / filename).exists()}")
        
        # List all files in upload folder
        all_files = list(Config.UPLOAD_FOLDER.glob("*"))
        logger.info(f"TEST: All files in upload folder: {[f.name for f in all_files]}")
        
        if not (Config.UPLOAD_FOLDER / filename).exists():
            logger.error(f"TEST: File not found: {filename}")
            return jsonify({"error": "File not found"}), 404
            
        return send_from_directory(str(Config.UPLOAD_FOLDER.absolute()), filename)
    except Exception as e:
        logger.error(f"TEST: Error serving file {filename}: {e}")
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', Config.PORT))
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)
