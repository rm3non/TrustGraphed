
class TrustGraphedApp {
    constructor() {
        this.form = document.getElementById('evaluationForm');
        this.contentInput = document.getElementById('contentInput');
        this.fileInput = document.getElementById('fileInput');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.btnText = document.getElementById('btnText');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.resultsSection = document.getElementById('resultsSection');
        this.errorSection = document.getElementById('errorSection');
        
        // File upload elements
        this.textTab = document.getElementById('textTab');
        this.fileTab = document.getElementById('fileTab');
        this.textInputSection = document.getElementById('textInputSection');
        this.fileInputSection = document.getElementById('fileInputSection');
        this.filePreview = document.getElementById('filePreview');
        this.previewText = document.getElementById('previewText');
        this.clearFileBtn = document.getElementById('clearFile');
        
        this.currentInputMethod = 'text';
        this.currentFileContent = '';
        
        this.init();
    }

    init() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.contentInput.addEventListener('input', () => this.validateInput());
        this.fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        this.clearFileBtn.addEventListener('click', () => this.clearFile());
        
        // Tab switching
        this.textTab.addEventListener('click', () => this.switchTab('text'));
        this.fileTab.addEventListener('click', () => this.switchTab('file'));
        
        // Drag and drop
        this.setupDragAndDrop();
        
        // Test backend connection on load
        this.testConnection();
        
        // Initial validation
        this.validateInput();
    }

    setupDragAndDrop() {
        const uploadArea = document.querySelector('.file-upload-area');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => uploadArea.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('dragover'), false);
        });

        uploadArea.addEventListener('drop', (e) => this.handleDrop(e), false);
        uploadArea.addEventListener('click', () => this.fileInput.click());
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
        this.textTab.classList.toggle('active', method === 'text');
        this.fileTab.classList.toggle('active', method === 'file');
        
        // Show/hide input sections
        this.textInputSection.classList.toggle('active', method === 'text');
        this.textInputSection.classList.toggle('hidden', method !== 'text');
        this.fileInputSection.classList.toggle('hidden', method !== 'file');
        
        // Clear other method when switching
        if (method === 'text') {
            this.clearFile();
        } else {
            this.contentInput.value = '';
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
            this.showFilePreview(file.name, extractedText);
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
        // For PDF parsing, we'll use a simple approach with FileReader
        // In a production app, you'd want to include pdf.js library
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = async (e) => {
                try {
                    // This is a simplified PDF text extraction
                    // For production, integrate pdf.js or similar library
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
        // Simplified PDF text extraction - replace with pdf.js in production
        const uint8Array = new Uint8Array(arrayBuffer);
        const text = String.fromCharCode.apply(null, uint8Array);
        
        // Basic text extraction from PDF (very simplified)
        const textMatches = text.match(/\(([^)]+)\)/g);
        if (textMatches && textMatches.length > 0) {
            return textMatches.map(match => match.slice(1, -1)).join(' ').substring(0, 5000);
        }
        
        // Fallback: look for readable text patterns
        const readableText = text.replace(/[^\x20-\x7E]/g, ' ').replace(/\s+/g, ' ').trim();
        if (readableText.length > 50) {
            return readableText.substring(0, 5000);
        }
        
        throw new Error('No readable text found in PDF');
    }

    async readDocxFile(file) {
        // For DOCX parsing, we'll implement a basic approach
        // In production, you'd want to include mammoth.js or similar
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
        // Simplified DOCX text extraction - replace with mammoth.js in production
        const uint8Array = new Uint8Array(arrayBuffer);
        const text = String.fromCharCode.apply(null, uint8Array);
        
        // Look for text content patterns in DOCX XML
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

    showFilePreview(filename, content) {
        const preview = content.substring(0, 300) + (content.length > 300 ? '...' : '');
        this.previewText.textContent = `📁 ${filename}\n\n${preview}`;
        this.filePreview.classList.remove('hidden');
    }

    clearFile() {
        this.fileInput.value = '';
        this.currentFileContent = '';
        this.filePreview.classList.add('hidden');
        this.previewText.textContent = '';
        this.validateInput();
    }

    validateInput() {
        let hasValidInput = false;
        
        if (this.currentInputMethod === 'text') {
            const textContent = this.contentInput.value.trim();
            hasValidInput = textContent.length >= 10;
        } else {
            hasValidInput = this.currentFileContent.length >= 10;
        }
        
        this.analyzeBtn.disabled = !hasValidInput;
    }

    async testConnection() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            console.log('Backend connection successful:', data);
        } catch (error) {
            console.error('Backend connection failed:', error);
            this.showError('Unable to connect to backend service. Please check if the server is running.');
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        let content = '';
        
        if (this.currentInputMethod === 'text') {
            content = this.contentInput.value.trim();
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
        document.getElementById('trustScore').textContent = (trust_evaluation.trust_score * 100).toFixed(0);
        document.getElementById('trustLevel').textContent = trust_evaluation.trust_level;

        // Update module results
        const sdg = module_results.source_data_grappler;
        document.getElementById('assertionsCount').textContent = sdg.assertions_found;
        document.getElementById('citationsCount').textContent = sdg.citations_found;
        document.getElementById('extractionConfidence').textContent = (sdg.extraction_confidence * 100).toFixed(0);

        const aie = module_results.assertion_integrity;
        document.getElementById('integrityScore').textContent = (aie.integrity_score * 100).toFixed(0);
        document.getElementById('issuesFound').textContent = aie.issues_found;

        const cce = module_results.confidence_computation;
        document.getElementById('overallConfidence').textContent = (cce.overall_confidence * 100).toFixed(0);
        document.getElementById('highConfidenceCount').textContent = cce.high_confidence_assertions;

        const zfp = module_results.zero_fabrication;
        document.getElementById('authenticityScore').textContent = (zfp.authenticity_score * 100).toFixed(0);
        document.getElementById('fabricationRisk').textContent = zfp.fabrication_risk;
        document.getElementById('flagsDetected').textContent = zfp.flags_detected;

        // Update certificate info
        document.getElementById('certificateId').textContent = certificate_id;
        document.getElementById('readableSummary').textContent = readable_summary;

        // Color-code trust score
        const scoreElement = document.getElementById('trustScore').parentElement;
        const score = trust_evaluation.trust_score;
        
        if (score >= 0.8) {
            scoreElement.style.background = 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)';
        } else if (score >= 0.6) {
            scoreElement.style.background = 'linear-gradient(135deg, #ed8936 0%, #dd6b20 100%)';
        } else {
            scoreElement.style.background = 'linear-gradient(135deg, #e53e3e 0%, #c53030 100%)';
        }

        this.showResults();
    }

    setLoading(loading) {
        if (loading) {
            this.analyzeBtn.disabled = true;
            this.btnText.classList.add('hidden');
            this.loadingSpinner.classList.remove('hidden');
        } else {
            this.loadingSpinner.classList.add('hidden');
            this.btnText.classList.remove('hidden');
            this.validateInput(); // Re-validate to set correct disabled state
        }
    }

    showResults() {
        this.resultsSection.classList.remove('hidden');
        this.resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    hideResults() {
        this.resultsSection.classList.add('hidden');
    }

    showError(message) {
        document.getElementById('errorMessage').textContent = message;
        this.errorSection.classList.remove('hidden');
        this.errorSection.scrollIntoView({ behavior: 'smooth' });
    }

    hideError() {
        this.errorSection.classList.add('hidden');
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TrustGraphedApp();
});

// Debug helper - available in console
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
