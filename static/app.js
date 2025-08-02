
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
            this.fileInput.files = files;
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

        try {
            this.setLoading(true);
            this.hideError();
            
            let extractedText = '';
            
            switch (fileExtension) {
                case '.txt':
                    extractedText = await this.readTextFile(file);
                    break;
                case '.pdf':
                    extractedText = await this.readPdfFile(file);
                    break;
                case '.docx':
                    extractedText = await this.readDocxFile(file);
                    break;
            }
            
            if (!extractedText || extractedText.trim().length < 10) {
                throw new Error('Unable to extract sufficient text from file. Please check the file content.');
            }
            
            this.currentFileContent = extractedText;
            this.showFileInfo(file.name);
            this.validateInput();
            
        } catch (error) {
            console.error('File processing error:', error);
            this.showError(`Failed to process file: ${error.message}`);
            this.clearFile();
        } finally {
            this.setLoading(false);
        }
    }

    async readTextFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('Failed to read text file'));
            reader.readAsText(file);
        });
    }

    async readPdfFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = async (e) => {
                try {
                    const arrayBuffer = e.target.result;
                    const text = await this.extractPdfText(arrayBuffer);
                    resolve(text);
                } catch (error) {
                    reject(new Error('Failed to parse PDF file. Please ensure it contains readable text.'));
                }
            };
            reader.onerror = () => reject(new Error('Failed to read PDF file'));
            reader.readAsArrayBuffer(file);
        });
    }

    async extractPdfText(arrayBuffer) {
        const uint8Array = new Uint8Array(arrayBuffer);
        const text = String.fromCharCode.apply(null, uint8Array);
        
        const textMatches = text.match(/\(([^)]+)\)/g);
        if (textMatches && textMatches.length > 0) {
            return textMatches.map(match => match.slice(1, -1)).join(' ').substring(0, 5000);
        }
        
        const readableText = text.replace(/[^\x20-\x7E]/g, ' ').replace(/\s+/g, ' ').trim();
        if (readableText.length > 50) {
            return readableText.substring(0, 5000);
        }
        
        throw new Error('No readable text found in PDF');
    }

    async readDocxFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = async (e) => {
                try {
                    const arrayBuffer = e.target.result;
                    const text = await this.extractDocxText(arrayBuffer);
                    resolve(text);
                } catch (error) {
                    reject(new Error('Failed to parse DOCX file. Please save as .txt or try a different file.'));
                }
            };
            reader.onerror = () => reject(new Error('Failed to read DOCX file'));
            reader.readAsArrayBuffer(file);
        });
    }

    async extractDocxText(arrayBuffer) {
        const uint8Array = new Uint8Array(arrayBuffer);
        const text = String.fromCharCode.apply(null, uint8Array);
        
        const xmlMatches = text.match(/<w:t[^>]*>([^<]+)<\/w:t>/g);
        if (xmlMatches && xmlMatches.length > 0) {
            const extractedText = xmlMatches
                .map(match => match.replace(/<[^>]+>/g, ''))
                .join(' ')
                .trim();
            
            if (extractedText.length > 10) {
                return extractedText.substring(0, 5000);
            }
        }
        
        throw new Error('No readable text found in DOCX file');
    }

    showFileInfo(filename) {
        if (this.fileName) this.fileName.textContent = filename;
        this.fileInfo?.classList.remove('hidden');
    }

    clearFile() {
        if (this.fileInput) this.fileInput.value = '';
        this.currentFileContent = '';
        this.fileInfo?.classList.add('hidden');
        if (this.fileName) this.fileName.textContent = 'No file selected';
        this.validateInput();
    }

    validateInput() {
        let hasValidInput = false;
        
        if (this.currentInputMethod === 'text') {
            const textContent = this.contentInput?.value.trim() || '';
            hasValidInput = textContent.length >= 10;
        } else {
            hasValidInput = this.currentFileContent.length >= 10;
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
        
        let content = '';
        
        if (this.currentInputMethod === 'text') {
            content = this.contentInput?.value.trim() || '';
        } else {
            content = this.currentFileContent;
        }
        
        if (!content || content.length < 10) {
            this.showError('Please provide at least 10 characters of content to analyze.');
            return;
        }

        this.setLoading(true);
        this.hideError();
        this.hideResults();

        try {
            console.log('Sending content for evaluation:', content.substring(0, 100) + '...');
            
            const response = await fetch('/evaluate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content: content })
            });

            console.log('Response status:', response.status);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('Evaluation results:', data);
            
            this.displayResults(data);
            
        } catch (error) {
            console.error('Evaluation failed:', error);
            this.showError(`Evaluation failed: ${error.message}`);
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

// Debug helper
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
