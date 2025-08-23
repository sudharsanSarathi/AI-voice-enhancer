// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileSelected = document.getElementById('fileSelected');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFile = document.getElementById('removeFile');
const intensitySlider = document.getElementById('intensity');
const intensityValue = document.getElementById('intensityValue');
const processBtn = document.getElementById('processBtn');
const resultsSection = document.getElementById('resultsSection');
const originalAudio = document.getElementById('originalAudio');
const enhancedAudio = document.getElementById('enhancedAudio');
const downloadBtn = document.getElementById('downloadBtn');

// Global variables
let selectedFile = null;
let processedData = null;
let currentFileId = null;
let progressInterval = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    updateIntensityDisplay();
    createProgressSection();
});

function createProgressSection() {
    // Create progress section after the controls
    const controlsSection = document.querySelector('.controls-section');
    const progressSection = document.createElement('div');
    progressSection.className = 'progress-section';
    progressSection.id = 'progressSection';
    progressSection.style.display = 'none';
    progressSection.innerHTML = `
        <div class="progress-container">
            <h3>⚡ Super-Fast Processing Audio...</h3>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div class="progress-text" id="progressText">Initializing fast processing...</div>
            <div class="progress-stage" id="progressStage">Stage: Uploading</div>
            <div class="progress-time" id="progressTime">Time: 0s</div>
            <div class="progress-estimate" id="progressEstimate">Estimated: 2-5 seconds</div>
        </div>
    `;
    
    controlsSection.parentNode.insertBefore(progressSection, controlsSection.nextSibling);
}

function setupEventListeners() {
    // File upload events
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);
    removeFile.addEventListener('click', clearFile);
    
    // Intensity slider events
    intensitySlider.addEventListener('input', updateIntensityDisplay);
    intensitySlider.addEventListener('change', updateIntensityDisplay);
    
    // Process button event
    processBtn.addEventListener('click', processAudio);
    
    // Download button event
    downloadBtn.addEventListener('click', downloadEnhancedAudio);
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    // Validate file type
    const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/flac', 'audio/ogg', 'audio/aac', 'audio/aiff'];
    const allowedExtensions = ['.mp3', '.wav', '.flac', '.ogg', '.aac', '.aiff'];
    
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
        showError('Please select a valid audio file (MP3, WAV, FLAC, OGG, AAC, AIFF)');
        return;
    }
    
    // Validate file size (50MB limit)
    const maxSize = 50 * 1024 * 1024; // 50MB in bytes
    if (file.size > maxSize) {
        showError('File size must be less than 50MB');
        return;
    }
    
    selectedFile = file;
    displaySelectedFile(file);
    enableControls();
}

function displaySelectedFile(file) {
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    uploadArea.style.display = 'none';
    fileSelected.style.display = 'flex';
}

function clearFile() {
    selectedFile = null;
    processedData = null;
    currentFileId = null;
    
    // Stop progress tracking
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
    
    // Hide progress section
    const progressSection = document.getElementById('progressSection');
    if (progressSection) {
        progressSection.style.display = 'none';
    }
    
    uploadArea.style.display = 'block';
    fileSelected.style.display = 'none';
    resultsSection.style.display = 'none';
    
    disableControls();
    resetProcessButton();
    
    // Clear file input
    fileInput.value = '';
}

function enableControls() {
    intensitySlider.disabled = false;
    processBtn.disabled = false;
}

function disableControls() {
    intensitySlider.disabled = true;
    processBtn.disabled = true;
}

function updateIntensityDisplay() {
    const value = parseInt(intensitySlider.value);
    intensityValue.textContent = value;
    
    // Update slider background based on value
    const percentage = ((value - 1) / 9) * 100;
    intensitySlider.style.background = `linear-gradient(to right, #667eea 0%, #667eea ${percentage}%, #ddd ${percentage}%, #ddd 100%)`;
}

function getIntensityLevel(value) {
    if (value <= 3) return 'light';
    if (value <= 7) return 'medium';
    return 'strong';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showError(message) {
    // Create error notification
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-notification';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #dc3545;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 1000;
        font-weight: 500;
        max-width: 300px;
    `;
    
    document.body.appendChild(errorDiv);
    
    // Remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}

function showSuccess(message) {
    // Create success notification
    const successDiv = document.createElement('div');
    successDiv.className = 'success-notification';
    successDiv.textContent = message;
    successDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 1000;
        font-weight: 500;
        max-width: 300px;
    `;
    
    document.body.appendChild(successDiv);
    
    // Remove after 3 seconds
    setTimeout(() => {
        if (successDiv.parentNode) {
            successDiv.parentNode.removeChild(successDiv);
        }
    }, 3000);
}

function setProcessButtonLoading(loading) {
    const btnText = processBtn.querySelector('.btn-text');
    const btnLoading = processBtn.querySelector('.btn-loading');
    
    if (loading) {
        btnText.style.display = 'none';
        btnLoading.style.display = 'flex';
        processBtn.disabled = true;
    } else {
        btnText.style.display = 'block';
        btnLoading.style.display = 'none';
        processBtn.disabled = false;
    }
}

function resetProcessButton() {
    setProcessButtonLoading(false);
}

function showProgressSection() {
    const progressSection = document.getElementById('progressSection');
    if (progressSection) {
        progressSection.style.display = 'block';
    }
}

function updateProgressBar(progress, stage, message) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const progressStage = document.getElementById('progressStage');
    
    if (progressFill) progressFill.style.width = `${progress}%`;
    if (progressText) progressText.textContent = message;
    if (progressStage) progressStage.textContent = `Stage: ${stage}`;
}

function startProgressTracking(fileId) {
    currentFileId = fileId;
    const startTime = Date.now();
    let errorCount = 0;
    const maxErrors = 10; // Stop after 10 consecutive errors
    
    // Show progress section
    showProgressSection();
    
    // Start progress polling
    progressInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/progress/${fileId}`);
            if (response.ok) {
                const progressData = await response.json();
                errorCount = 0; // Reset error count on success
                
                // Update progress bar
                updateProgressBar(
                    progressData.progress || 0,
                    progressData.stage || 'unknown',
                    progressData.message || 'Processing...'
                );
                
                // Update time
                const elapsed = Math.floor((Date.now() - startTime) / 1000);
                const progressTime = document.getElementById('progressTime');
                if (progressTime) {
                    progressTime.textContent = `Time: ${elapsed}s`;
                }
                
                // Check if processing is complete
                if (progressData.stage === 'complete') {
                    clearInterval(progressInterval);
                    progressInterval = null;
                    
                    // Get the result
                    await getProcessingResult(fileId);
                    
                    // Hide progress section
                    const progressSection = document.getElementById('progressSection');
                    if (progressSection) {
                        progressSection.style.display = 'none';
                    }
                }
                
                // Check if there's an error
                if (progressData.stage === 'error') {
                    clearInterval(progressInterval);
                    progressInterval = null;
                    showError(progressData.message || 'Processing failed');
                    
                    // Hide progress section
                    const progressSection = document.getElementById('progressSection');
                    if (progressSection) {
                        progressSection.style.display = 'none';
                    }
                }
            } else if (response.status === 404) {
                errorCount++;
                console.warn(`Progress not found for file ${fileId}, error count: ${errorCount}`);
                
                // Stop polling after too many 404 errors
                if (errorCount >= maxErrors) {
                    clearInterval(progressInterval);
                    progressInterval = null;
                    showError('Processing status not found. Please try uploading again.');
                    
                    // Hide progress section
                    const progressSection = document.getElementById('progressSection');
                    if (progressSection) {
                        progressSection.style.display = 'none';
                    }
                }
            }
        } catch (error) {
            errorCount++;
            console.error('Progress tracking error:', error);
            
            // Stop polling after too many errors
            if (errorCount >= maxErrors) {
                clearInterval(progressInterval);
                progressInterval = null;
                showError('Failed to track progress. Please try uploading again.');
                
                // Hide progress section
                const progressSection = document.getElementById('progressSection');
                if (progressSection) {
                    progressSection.style.display = 'none';
                }
            }
        }
    }, 1000); // Poll every 1 second to reduce server load
}

async function getProcessingResult(fileId) {
    try {
        const response = await fetch(`/api/result/${fileId}`);
        if (response.ok) {
            const resultData = await response.json();
            if (resultData.success) {
                processedData = resultData;
                displayResults(resultData);
                showSuccess('⚡ Audio processing completed successfully! (Super-fast processing)');
            }
        }
    } catch (error) {
        console.error('Error getting result:', error);
        showError('Failed to retrieve processing result');
    }
}

async function processAudio() {
    if (!selectedFile) {
        showError('Please select an audio file first');
        return;
    }
    
    const intensity = parseInt(intensitySlider.value);
    const intensityLevel = getIntensityLevel(intensity);
    
    setProcessButtonLoading(true);
    
    try {
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('audio', selectedFile);
        formData.append('intensity', intensity);
        
        // Send request to API
        const response = await fetch('/api/process', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.status === 'processing') {
            // Start progress tracking
            startProgressTracking(data.file_id);
            showSuccess('⚡ Super-fast processing started! Should complete in 2-5 seconds.');
            
            // Update estimate
            const progressEstimate = document.getElementById('progressEstimate');
            if (progressEstimate && data.estimated_time) {
                progressEstimate.textContent = `Estimated: ${data.estimated_time}`;
            }
        } else {
            throw new Error(data.message || 'Unexpected response');
        }
        
    } catch (error) {
        console.error('Processing error:', error);
        showError(`Processing failed: ${error.message}`);
    } finally {
        setProcessButtonLoading(false);
    }
}

function displayResults(data) {
    // Set audio sources
    originalAudio.src = `/api/audio/uploads/${data.original_file}`;
    enhancedAudio.src = `/api/audio/processed/${data.enhanced_file}`;
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function downloadEnhancedAudio() {
    if (!processedData) {
        showError('No processed audio available for download');
        return;
    }
    
    // Create download link
    const downloadUrl = `/api/download/${processedData.enhanced_file}`;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `enhanced_${selectedFile.name}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showSuccess('Download started!');
}

// Utility function to handle API errors
function handleApiError(error) {
    console.error('API Error:', error);
    
    if (error.message.includes('fetch')) {
        showError('Unable to connect to server. Please check your connection.');
    } else {
        showError(error.message || 'An unexpected error occurred.');
    }
}

// Initialize intensity display on page load
updateIntensityDisplay();
