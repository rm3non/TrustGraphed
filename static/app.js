class TrustGraphedApp {
    constructor() {
        this.modal = document.getElementById('evaluationModal');
        this.form = document.getElementById('evaluationForm');
        this.contentInput = document.getElementById('contentInput');
        this.fileInput = document.getElementById('fileInput');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.btnText = document.getElementById('btnText');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.resultsSection = document.getElementById('resultsSection');
        this.errorSection = document.getElementById('errorSection');

        // Modal controls
        this.startEvaluationBtn = document.getElementById('startEvaluationBtn');
        this.heroStartBtn = document.getElementById('heroStartBtn');
        this.uploadPasteBtn = document.getElementById('uploadPasteBtn');
        this.ctaStartBtn = document.getElementById('ctaStartBtn');
        this.closeModal = document.getElementById('closeModal');

        // File upload elements
        this.textTab = document.getElementById('textTab');
        this.fileTab = document.getElementById('fileTab');
        this.textInputSection = document.getElementById('textInputSection');
        this.fileInputSection = document.getElementById('fileInputSection');
        this.fileInfo = document.getElementById('fileInfo');
        this.fileName = document.getElementById('fileName');
        this.removeFileBtn = document.getElementById('removeFile');

        this.currentInputMethod = 'text';
        this.currentFileContent = '';
        this.currentFile = null;

        this.init();
    }

    init() {
        // Modal triggers
        this.startEvaluationBtn?.addEventListener('click', () => this.openModal());
        this.heroStartBtn?.addEventListener('click', () => this.openModal());
        this.uploadPasteBtn?.addEventListener('click', () => this.openModal('file'));
        this.ctaStartBtn?.addEventListener('click', () => this.openModal());
        this.closeModal?.addEventListener('click', () => this.closeModalHandler());

        // Modal overlay click to close
        this.modal?.addEventListener('click', (e) => {
            if (e.target === this.modal) this.closeModalHandler();
        });

        // Form handling
        this.form?.addEventListener('submit', (e) => this.handleSubmit(e));
        this.contentInput?.addEventListener('input', () => this.validateInput());
        this.fileInput?.addEventListener('change', (e) => this.handleFileUpload(e));
        this.removeFileBtn?.addEventListener('click', () => this.clearFile());

        // Tab switching
        this.textTab?.addEventListener('click', () => this.switchTab('text'));
        this.fileTab?.addEventListener('click', () => this.switchTab('file'));

        // Drag and drop
        this.setupDragAndDrop();

        // Test backend connection on load
        this.testConnection();

        // Initial validation
        this.validateInput();
    }

    openModal(defaultTab = 'text') {
        this.modal?.classList.remove('hidden');
        document.body.style.overflow = 'hidden';

        if (defaultTab === 'file') {
            this.switchTab('file');
        } else {
            this.switchTab('text');
        }

        // Focus appropriate input
        setTimeout(() => {
            if (defaultTab === 'text') {
                this.contentInput?.focus();
            }
        }, 100);
    }

    closeModalHandler() {
        this.modal?.classList.add('hidden');
        document.body.style.overflow = 'auto';
        this.hideResults();
        this.hideError();
    }

    setupDragAndDrop() {
        const dropZone = document.querySelector('.file-drop-zone');
        if (!dropZone) return;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
        });

        dropZone.addEventListener('drop', (e) => this.handleDrop(e), false);
        dropZone.addEventListener('click', () => this.fileInput?.click());
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleDrop(e) {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            // Clear any existing file first
            this.clearFile();
            // Set the file input
            this.fileInput.files = files;
            // Handle the upload
            this.handleFileUpload({ target: { files } });
        }
    }

    switchTab(method) {
        this.currentInputMethod = method;

        // Update tab styles
        this.textTab?.classList.toggle('active', method === 'text');
        this.fileTab?.classList.toggle('active', method === 'file');

        // Show/hide input sections
        this.textInputSection?.classList.toggle('active', method === 'text');
        this.textInputSection?.classList.toggle('hidden', method !== 'text');
        this.fileInputSection?.classList.toggle('hidden', method !== 'file');

        // Clear other method when switching
        if (method === 'text') {
            this.clearFile();
        } else {
            if (this.contentInput) this.contentInput.value = '';
        }

        this.validateInput();
    }

    async handleFileUpload(e) {
        const file = e.target.files[0];
        if (!file) {
            this.clearFile();
            return;
        }

        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            this.showError('File size exceeds 10MB limit. Please choose a smaller file.');
            this.clearFile();
            return;
        }

        // Validate file type
        const allowedTypes = ['.txt', '.pdf', '.docx'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

        if (!allowedTypes.includes(fileExtension)) {
            this.showError('Unsupported file type. Please upload .txt, .pdf, or .docx files only.');
            this.clearFile();
            return;
        }

        // Store the file for later submission - no client-side processing
        this.currentFile = file;
        this.currentFileContent = 'FILE_UPLOAD'; // Flag to indicate file mode
        this.showFileInfo(file.name);
        this.hideError(); // Clear any previous errors
        this.validateInput();
    }



    showFileInfo(filename) {
        if (this.fileName) this.fileName.textContent = filename;
        this.fileInfo?.classList.remove('hidden');
    }

    clearFile() {
        if (this.fileInput) {
            this.fileInput.value = '';
        }
        this.currentFileContent = '';
        this.currentFile = null;
        this.fileInfo?.classList.add('hidden');
        if (this.fileName) this.fileName.textContent = 'No file selected';
        this.hideError(); // Clear any errors when clearing file
        this.validateInput();
    }

    validateInput() {
        let hasValidInput = false;

        if (this.currentInputMethod === 'text') {
            const textContent = this.contentInput?.value.trim() || '';
            hasValidInput = textContent.length >= 10;
        } else {
            hasValidInput = this.currentFile && this.currentFile.size > 0;
        }

        if (this.analyzeBtn) this.analyzeBtn.disabled = !hasValidInput;
    }

    async testConnection() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            console.log('Backend connection successful:', data);
        } catch (error) {
            console.error('Backend connection failed:', error);
        }
    }

    async handleSubmit(e) {
        e.preventDefault();

        this.setLoading(true);
        this.hideError();
        this.hideResults();

        try {
            let response;

            if (this.currentInputMethod === 'text') {
                const content = this.contentInput?.value.trim() || '';

                if (!content || content.length < 10) {
                    this.showError('Please provide at least 10 characters of content to analyze.');
                    return;
                }

                console.log('Sending text content for evaluation:', content.substring(0, 100) + '...');

                response = await fetch('/evaluate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ content: content })
                });

            } else {
                // File upload mode
                if (!this.currentFile) {
                    this.showError('Please select a file to upload.');
                    return;
                }

                console.log('Sending file for evaluation:', this.currentFile.name);
                console.log('File size:', this.currentFile.size, 'bytes');
                console.log('File type:', this.currentFile.type);

                const formData = new FormData();
                formData.append('file', this.currentFile);

                response = await fetch('/evaluate', {
                    method: 'POST',
                    body: formData
                });
            }

            console.log('Response status:', response.status);
            console.log('Response headers:', Object.fromEntries(response.headers));

            if (!response.ok) {
                let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                try {
                    const responseText = await response.text();
                    console.log('Error response text:', responseText);
                    
                    if (responseText) {
                        try {
                            const errorData = JSON.parse(responseText);
                            errorMessage = errorData.error || errorData.message || errorMessage;
                        } catch (jsonError) {
                            // If not JSON, use the raw text if it's meaningful
                            if (responseText.length > 0 && responseText.length < 500) {
                                errorMessage = responseText;
                            }
                        }
                    }
                } catch (textError) {
                    console.error('Failed to read error response:', textError);
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            console.log('Evaluation results:', data);

            this.displayResults(data);

        } catch (error) {
            console.error('Evaluation failed:', error);
            console.error('Error type:', typeof error);
            console.error('Error constructor:', error?.constructor?.name);
            
            let errorMessage = 'Unknown error occurred during evaluation';
            
            if (error instanceof Error && error.message) {
                errorMessage = error.message;
            } else if (typeof error === 'string' && error.trim()) {
                errorMessage = error;
            } else if (error && typeof error === 'object') {
                if (error.message) {
                    errorMessage = error.message;
                } else if (error.error) {
                    errorMessage = error.error;
                } else {
                    // Try to extract meaningful info from the error object
                    const errorKeys = Object.keys(error);
                    if (errorKeys.length > 0) {
                        errorMessage = `Error object: ${JSON.stringify(error)}`;
                    }
                }
            }
            
            // Ensure we have a meaningful error message
            if (!errorMessage || errorMessage === 'Unknown error occurred during evaluation') {
                errorMessage = 'File processing failed. Please try again or use a different file.';
            }
            
            this.showError(`Evaluation failed: ${errorMessage}`);
        } finally {
            this.setLoading(false);
        }
    }

    displayResults(data) {
        if (data.status !== 'success') {
            this.showError('Evaluation completed with errors. Please try again.');
            return;
        }

        const { trust_evaluation, module_results, certificate_id, certificate, readable_summary } = data;

        // Update trust score
        const trustScoreEl = document.getElementById('trustScore');
        const trustLevelEl = document.getElementById('trustLevel');
        if (trustScoreEl) trustScoreEl.textContent = (trust_evaluation.trust_score * 100).toFixed(0);
        if (trustLevelEl) trustLevelEl.textContent = trust_evaluation.trust_level;

        // Update module results
        const sdg = module_results.source_data_grappler;
        const assertionsEl = document.getElementById('assertionsCount');
        const citationsEl = document.getElementById('citationsCount');
        const extractionEl = document.getElementById('extractionConfidence');
        if (assertionsEl) assertionsEl.textContent = sdg.assertions_found;
        if (citationsEl) citationsEl.textContent = sdg.citations_found;
        if (extractionEl) extractionEl.textContent = (sdg.extraction_confidence * 100).toFixed(0);

        const aie = module_results.assertion_integrity;
        const integrityEl = document.getElementById('integrityScore');
        const issuesEl = document.getElementById('issuesFound');
        if (integrityEl) integrityEl.textContent = (aie.integrity_score * 100).toFixed(0);
        if (issuesEl) issuesEl.textContent = aie.issues_found;

        const cce = module_results.confidence_computation;
        const overallEl = document.getElementById('overallConfidence');
        const highConfEl = document.getElementById('highConfidenceCount');
        if (overallEl) overallEl.textContent = (cce.overall_confidence * 100).toFixed(0);
        if (highConfEl) highConfEl.textContent = cce.high_confidence_assertions;

        const zfp = module_results.zero_fabrication;
        const authEl = document.getElementById('authenticityScore');
        const fabRiskEl = document.getElementById('fabricationRisk');
        const flagsEl = document.getElementById('flagsDetected');
        if (authEl) authEl.textContent = (zfp.authenticity_score * 100).toFixed(0);
        if (fabRiskEl) fabRiskEl.textContent = zfp.fabrication_risk;
        if (flagsEl) flagsEl.textContent = zfp.flags_detected;

        // Update certificate info
        const certIdEl = document.getElementById('certificateId');
        const summaryEl = document.getElementById('readableSummary');
        if (certIdEl) certIdEl.textContent = certificate_id;
        if (summaryEl) summaryEl.textContent = readable_summary;

        // Color-code trust score
        const scoreElement = trustScoreEl?.parentElement;
        if (scoreElement) {
            const score = trust_evaluation.trust_score;

            if (score >= 0.8) {
                scoreElement.style.background = 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)';
            } else if (score >= 0.6) {
                scoreElement.style.background = 'linear-gradient(135deg, #ed8936 0%, #dd6b20 100%)';
            } else {
                scoreElement.style.background = 'linear-gradient(135deg, #e53e3e 0%, #c53030 100%)';
            }
        }

        this.showResults();
    }

    setLoading(loading) {
        if (loading) {
            if (this.analyzeBtn) this.analyzeBtn.disabled = true;
            this.btnText?.classList.add('hidden');
            this.loadingSpinner?.classList.remove('hidden');
        } else {
            this.loadingSpinner?.classList.add('hidden');
            this.btnText?.classList.remove('hidden');
            this.validateInput();
        }
    }

    showResults() {
        this.resultsSection?.classList.remove('hidden');
        this.resultsSection?.scrollIntoView({ behavior: 'smooth' });
    }

    hideResults() {
        this.resultsSection?.classList.add('hidden');
    }

    showError(message) {
        const errorMessageEl = document.getElementById('errorMessage');
        if (errorMessageEl) errorMessageEl.textContent = message;
        this.errorSection?.classList.remove('hidden');
        this.errorSection?.scrollIntoView({ behavior: 'smooth' });
    }

    hideError() {
        this.errorSection?.classList.add('hidden');
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TrustGraphedApp();
});

// Debug helpers
window.testEvaluate = async function(content = "This is a test content with some claims that need verification.") {
    try {
        const response = await fetch('/evaluate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
        const data = await response.json();
        console.log('Test evaluation result:', data);
        return data;
    } catch (error) {
        console.error('Test failed:', error);
        return error;
    }
};

// UAT Test Suite
window.runUATTests = async function() {
    console.log('🧪 Starting UAT Test Suite for TrustGraphed');
    
    const results = {
        passed: 0,
        failed: 0,
        tests: []
    };
    
    // Test 1: Text Input Submission
    try {
        console.log('Test 1: Text input submission...');
        const textResult = await window.testEvaluate("This is a test document with multiple claims that need verification. The system should analyze this content thoroughly and provide a comprehensive trust score based on assertion integrity, fabrication detection, and confidence analysis.");
        if (textResult.status === 'success') {
            results.passed++;
            results.tests.push({ name: 'Text Input', status: 'PASS', data: textResult });
            console.log('✅ Test 1 PASSED');
        } else {
            throw new Error('Invalid response format');
        }
    } catch (error) {
        results.failed++;
        results.tests.push({ name: 'Text Input', status: 'FAIL', error: error.message });
        console.log('❌ Test 1 FAILED:', error.message);
    }
    
    // Test 2: Backend Health Check
    try {
        console.log('Test 2: Backend health check...');
        const healthResponse = await fetch('/health');
        const healthData = await healthResponse.json();
        if (healthResponse.ok && healthData.status) {
            results.passed++;
            results.tests.push({ name: 'Backend Health', status: 'PASS', data: healthData });
            console.log('✅ Test 2 PASSED');
        } else {
            throw new Error('Health check failed');
        }
    } catch (error) {
        results.failed++;
        results.tests.push({ name: 'Backend Health', status: 'FAIL', error: error.message });
        console.log('❌ Test 2 FAILED:', error.message);
    }
    
    // Test 3: File Processing Test Endpoint
    try {
        console.log('Test 3: File processing test endpoint...');
        const testFileResponse = await fetch('/evaluate/test-file', {
            method: 'POST',
            body: new FormData() // Empty form data to test error handling
        });
        
        // This should return an error, but it should be a properly formatted error
        if (!testFileResponse.ok) {
            const errorData = await testFileResponse.json();
            if (errorData.error) {
                results.passed++;
                results.tests.push({ name: 'File Error Handling', status: 'PASS', data: errorData });
                console.log('✅ Test 3 PASSED - Error handling works correctly');
            } else {
                throw new Error('Error response format is incorrect');
            }
        }
    } catch (error) {
        results.failed++;
        results.tests.push({ name: 'File Error Handling', status: 'FAIL', error: error.message });
        console.log('❌ Test 3 FAILED:', error.message);
    }
    
    console.log(`🏁 UAT Results: ${results.passed} passed, ${results.failed} failed`);
    console.table(results.tests);
    
    return results;
};

// File upload simulation test
window.testFileUpload = function(testFile) {
    console.log('🔍 Testing file upload with:', testFile?.name || 'no file');
    
    if (!testFile) {
        console.log('❌ No file provided for testing');
        return;
    }
    
    const app = new TrustGraphedApp();
    app.currentFile = testFile;
    app.currentInputMethod = 'file';
    
    console.log('File details:', {
        name: testFile.name,
        size: testFile.size,
        type: testFile.type,
        lastModified: new Date(testFile.lastModified)
    });
    
    // Simulate the form submission
    const event = new Event('submit');
    app.handleSubmit(event);
};