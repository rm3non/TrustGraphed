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
        // Modal triggers - use more robust event binding
        const startButtons = [
            this.startEvaluationBtn,
            this.heroStartBtn,
            this.ctaStartBtn,
            document.getElementById('startEvaluationBtn'),
            document.getElementById('heroStartBtn'),
            document.getElementById('ctaStartBtn')
        ];

        startButtons.forEach(btn => {
            if (btn) {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    console.log('Start button clicked, opening modal...');
                    this.openModal();
                });
            }
        });

        // Upload button
        const uploadButtons = [this.uploadPasteBtn, document.getElementById('uploadPasteBtn')];
        uploadButtons.forEach(btn => {
            if (btn) {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    console.log('Upload button clicked, opening modal...');
                    this.openModal('file');
                });
            }
        });

        // Close modal
        if (this.closeModal) {
            this.closeModal.addEventListener('click', () => this.closeModalHandler());
        }

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

        // Add global click handlers for any missed buttons
        this.setupGlobalHandlers();
    }

    openModal(defaultTab = 'text') {
        console.log('Opening modal with tab:', defaultTab);

        if (!this.modal) {
            console.error('Modal element not found!');
            return;
        }

        this.modal.classList.remove('hidden');
        this.modal.style.display = 'flex';
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

        console.log('Modal opened successfully');
    }

    closeModalHandler() {
        this.modal?.classList.add('hidden');
        document.body.style.overflow = 'auto';
        this.hideResults();
        this.hideError();

        // Reset detailed explanation section attributes
        const toggleBtn = document.getElementById('toggleDetailedReport');
        if (toggleBtn) {
            toggleBtn.removeAttribute('data-initialized');
        }
    }

    setupDragAndDrop() {
        const dropZone = document.getElementById('dropZone');
        if (!dropZone) return;

        // Prevent default behavior for drag events
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
        });

        // Add visual feedback for drag events
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
        });

        // Handle file drop
        dropZone.addEventListener('drop', (e) => this.handleDrop(e), false);

        // Handle click to open file dialog with proper event handling
        dropZone.addEventListener('click', (e) => {
            // Only open file dialog if clicking directly on the drop zone, not on child elements
            if (e.target === dropZone || e.target.closest('.upload-icon, h4, .file-format-hint, .click-hint')) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Drop zone clicked, opening file dialog...');
                this.openFileDialog();
            }
        });
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    openFileDialog() {
        console.log('openFileDialog called');
        if (this.fileInput) {
            console.log('File input found, triggering click...');
            // Reset the input first to allow selecting the same file again
            this.fileInput.value = '';
            this.fileInput.click();
        } else {
            console.error('File input element not found');
        }
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
        console.log('handleFileUpload called');
        const file = e.target.files[0];
        if (!file) {
            console.log('No file selected, clearing');
            this.clearFile();
            return;
        }

        console.log('File selected:', file.name, 'Size:', file.size, 'Type:', file.type);

        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            this.showError('File size exceeds 10MB limit. Please choose a smaller file.');
            this.clearFile();
            return;
        }

        // Validate file type more robustly
        const allowedExtensions = ['.txt', '.pdf', '.docx'];
        const fileName = file.name.toLowerCase();
        const fileExtension = '.' + fileName.split('.').pop();

        // Also check MIME types for additional validation
        const allowedMimeTypes = [
            'text/plain',
            'application/pdf', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword'
        ];

        if (!allowedExtensions.includes(fileExtension) && !allowedMimeTypes.includes(file.type)) {
            this.showError('Unsupported file type. Please upload .txt, .pdf, or .docx files only.');
            this.clearFile();
            return;
        }

        // Store the file for later submission
        this.currentFile = file;
        this.currentFileContent = 'FILE_UPLOAD';
        this.showFileInfo(file.name);
        this.hideError();
        this.validateInput();

        console.log('File successfully loaded and validated');
    }



    showFileInfo(filename) {
        if (this.fileName) this.fileName.textContent = filename;
        if (this.fileInfo) {
            this.fileInfo.classList.remove('hidden');
            this.fileInfo.style.display = 'flex';
        }
    }

    clearFile() {
        if (this.fileInput) {
            this.fileInput.value = '';
        }
        this.currentFileContent = '';
        this.currentFile = null;
        if (this.fileInfo) {
            this.fileInfo.classList.add('hidden');
            this.fileInfo.style.display = 'none';
        }
        if (this.fileName) this.fileName.textContent = 'No file selected';
        this.hideError();
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
            let body;

            if (this.currentInputMethod === 'text') {
                const content = this.contentInput?.value.trim() || '';

                if (!content || content.length < 10) {
                    this.showError('Please provide at least 10 characters of content to analyze.');
                    return;
                }

                console.log('Sending text content for evaluation:', content.substring(0, 100) + '...');

                // Prepare JSON data for text input
                const assertionType = document.getElementById('contentSource')?.value || 'unsure';
                body = JSON.stringify({
                    content: this.contentInput.value.trim(),
                    content_assertion: assertionType
                });

                response = await fetch('/evaluate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: body
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

                // Prepare form data for file upload
                const formData = new FormData();
                formData.append('file', this.currentFile);

                // Add content assertion from dropdown
                const assertionType = document.getElementById('contentSource')?.value || 'unsure';
                formData.append('content_assertion', assertionType);

                body = formData;

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
        const readableSummaryEl = document.getElementById('readableSummary');
        if (certIdEl) certIdEl.textContent = certificate_id || 'N/A';
        if (readableSummaryEl) readableSummaryEl.textContent = readable_summary || 'Certificate generated successfully';

        // Display detailed explanation if available
        if (data.trust_evaluation && data.trust_evaluation.detailed_explanation) {
            const explanationContainer = document.getElementById('detailedExplanation');
            if (explanationContainer) {
                this.displayDetailedExplanation(data.trust_evaluation.detailed_explanation);
            } else {
                console.warn('Detailed explanation container not found in DOM');
            }
        }

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

     // Method to display the detailed explanation
    displayDetailedExplanation(explanation) {
        console.log('Detailed explanation data:', explanation);

        if (!explanation || typeof explanation !== 'object') {
            console.warn('No detailed explanation data available');
            return;
        }

        // Show the detailed explanation section
        const explanationSection = document.getElementById('detailedExplanationSection');
        if (explanationSection) {
            explanationSection.classList.remove('hidden');

            // Set up toggle functionality only once
            const toggleBtn = document.getElementById('toggleDetailedReport');
            const detailedReport = document.getElementById('detailedReport');

            if (toggleBtn && detailedReport && !toggleBtn.hasAttribute('data-initialized')) {
                toggleBtn.setAttribute('data-initialized', 'true');
                toggleBtn.onclick = () => {
                    const isHidden = detailedReport.classList.contains('hidden');
                    if (isHidden) {
                        detailedReport.classList.remove('hidden');
                        toggleBtn.textContent = 'Hide Detailed Analysis';
                    } else {
                        detailedReport.classList.add('hidden');
                        toggleBtn.textContent = 'Show Detailed Analysis';
                    }
                };
            }
        } else {
            // Create explanation section if it doesn't exist
            this.createDetailedExplanationSection();
        }

        // Populate overall explanation
        const overallExpl = document.getElementById('overallExplanation');
        if (overallExpl && explanation.overall_explanation) {
            overallExpl.textContent = explanation.overall_explanation;
        }

        // Populate score breakdown
        const scoreBreakdown = document.getElementById('scoreBreakdown');
        if (scoreBreakdown && explanation.score_breakdown) {
            let breakdownHTML = '<div class="breakdown-table">';

            Object.entries(explanation.score_breakdown).forEach(([key, value]) => {
                if (key !== 'final_calculation' && typeof value === 'object') {
                    breakdownHTML += `
                        <div class="breakdown-row">
                            <strong>${key}</strong>
                            <span>${value.calculation || `${value.raw_score} × ${value.weight}`}</span>
                            <span>${value.weighted_contribution || 'N/A'}</span>
                        </div>
                    `;
                }
            });

            if (explanation.score_breakdown.final_calculation) {
                breakdownHTML += `
                    <div class="breakdown-final">
                        <strong>Final Score: ${explanation.score_breakdown.final_calculation.total_weighted_score}</strong>
                    </div>
                `;
            }

            breakdownHTML += '</div>';
            scoreBreakdown.innerHTML = breakdownHTML;
        }

        // Populate component analysis
        const componentAnalysis = document.getElementById('componentAnalysis');
        if (componentAnalysis && explanation.component_explanations) {
            let componentHTML = '';

            Object.entries(explanation.component_explanations).forEach(([key, comp]) => {
                componentHTML += `
                    <div class="component-detail">
                        <h6>${comp.name} (Weight: ${comp.weight || 'N/A'})</h6>
                        <p><strong>Score:</strong> ${comp.score || 'N/A'}</p>
                        <p><strong>Explanation:</strong> ${comp.explanation || 'N/A'}</p>
                        <p><strong>Impact:</strong> ${comp.impact || 'N/A'}</p>
                        ${comp.details ? `
                            <div class="component-details-extra">
                                ${Object.entries(comp.details).map(([k, v]) => 
                                    k !== 'what_this_means' ? `<span><strong>${k.replace(/_/g, ' ')}:</strong> ${v}</span>` : ''
                                ).join('')}
                                ${comp.details.what_this_means ? `<p><em>${comp.details.what_this_means}</em></p>` : ''}
                            </div>
                        ` : ''}
                    </div>
                `;
            });

            componentAnalysis.innerHTML = componentHTML;
        }

        // Populate methodology
        const methodologyDetails = document.getElementById('methodologyDetails');
        if (methodologyDetails && explanation.methodology_details) {
            const methodology = explanation.methodology_details;
            let methodHTML = `
                <p><strong>Approach:</strong> ${methodology.approach || 'N/A'}</p>
                <div class="methodology-components">
                    <h6>Component Weights:</h6>
            `;

            if (methodology.components) {
                Object.entries(methodology.components).forEach(([key, value]) => {
                    methodHTML += `<div class="method-component"><strong>${key}:</strong> ${value}</div>`;
                });
            }

            methodHTML += '</div>';

            if (methodology.score_calculation) {
                methodHTML += `<p><strong>Calculation:</strong> ${methodology.score_calculation}</p>`;
            }

            methodologyDetails.innerHTML = methodHTML;
        }

        // Populate recommendations
        const recommendations = document.getElementById('recommendations');
        if (recommendations && explanation.recommendations) {
            let recHTML = '';
            explanation.recommendations.forEach(rec => {
                recHTML += `<div class="recommendation">${rec}</div>`;
            });
            recommendations.innerHTML = recHTML;
        }
    }

    createDetailedExplanationSection() {
        const resultsSection = document.getElementById('resultsSection');
        if (!resultsSection) return;

        // Create the detailed explanation section if it doesn't exist
        const existingSection = document.getElementById('detailedExplanationSection');
        if (existingSection) return;

        const explanationSection = document.createElement('div');
        explanationSection.id = 'detailedExplanationSection';
        explanationSection.className = 'detailed-explanation-section';
        explanationSection.innerHTML = `
            <h4>📊 Detailed Analysis Report</h4>
            <button id="toggleDetailedReport" class="btn-secondary">Show Detailed Analysis</button>
            <div id="detailedReport" class="detailed-report hidden">
                <div class="explanation-card">
                    <h5>🎯 Overall Score Explanation</h5>
                    <div id="overallExplanation" class="explanation-content"></div>
                </div>
                <div class="explanation-card">
                    <h5>⚖️ Score Breakdown</h5>
                    <div id="scoreBreakdown" class="score-breakdown"></div>
                </div>
                <div class="explanation-card">
                    <h5>🔍 Component Analysis</h5>
                    <div id="componentAnalysis" class="component-analysis"></div>
                </div>
                <div class="explanation-card">
                    <h5>📋 Methodology</h5>
                    <div id="methodologyDetails" class="methodology-details"></div>
                </div>
                <div class="explanation-card">
                    <h5>💡 Recommendations</h5>
                    <div id="recommendations" class="recommendations"></div>
                </div>
            </div>
        `;

        resultsSection.appendChild(explanationSection);
    }

    createDetailedExplanationContainer(explanation) {
        const resultsSection = document.getElementById('resultsSection');
        if (!resultsSection) return;

        const explanationDiv = document.createElement('div');
        explanationDiv.id = 'detailedExplanation';
        explanationDiv.className = 'detailed-explanation';
        explanationDiv.innerHTML = `
            <h4>📋 Detailed Analysis</h4>
            <div class="explanation-content">
                ${explanation.split('\n').map(line => `<p>${line}</p>`).join('')}
            </div>
        `;

        resultsSection.appendChild(explanationDiv);
    }

    setupGlobalHandlers() {
        // Global click handler for buttons that might not be caught
        document.addEventListener('click', (e) => {
            const target = e.target;

            // Check for start evaluation buttons
            if (target.id === 'startEvaluationBtn' || 
                target.id === 'heroStartBtn' || 
                target.id === 'ctaStartBtn' ||
                target.textContent?.includes('Start Evaluation') ||
                target.textContent?.includes('Try Protocol')) {
                e.preventDefault();
                console.log('Global handler caught start button click');
                this.openModal();
                return;
            }

            // Check for upload buttons
            if (target.id === 'uploadPasteBtn' || 
                target.textContent?.includes('Upload Document')) {
                e.preventDefault();
                console.log('Global handler caught upload button click');
                this.openModal('file');
                return;
            }
        });
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.trustGraphedApp = new TrustGraphedApp();
});

// Utility functions for navigation
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

function scrollToDemo() {
    const demoSection = document.getElementById('demo');
    if (demoSection) {
        demoSection.scrollIntoView({ behavior: 'smooth' });
    }
    // Open the evaluation modal after scrolling
    setTimeout(() => {
        const app = window.trustGraphedApp;
        if (app) {
            app.openModal();
        }
    }, 500);
}

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

// TrustGraphed Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    checkBackendHealth();
    initializeEventListeners();
});

async function checkBackendHealth(){
    try {
        const response = await fetch('/health');
        const data = await response.json();
        console.log('Backend connection successful:', data);
    } catch (error) {
        console.error('Backend connection failed:', error);
    }
}

function initializeEventListeners() {
    // File input change handler
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            if (fileName) {
                const label = this.nextElementSibling;
                label.innerHTML = `<i class="fas fa-file"></i> ${fileName}`;
            }
        });
    }
}

// Navigation functions
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

function scrollToDemo() {
    const element = document.getElementById('demo');
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

// Tab switching functionality
function switchTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab content
    const targetTab = document.getElementById(tabName + 'Tab');
    if (targetTab) {
        targetTab.classList.add('active');
    }

    // Add active class to clicked button
    event.target.classList.add('active');
}

async function handleFileUpload() {
    console.log("handleFileUpload called");

    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        console.log("No file selected");
        return;
    }

    console.log("File selected:", file.name, "Size:", file.size, "Type:", file.type);

    // Validate file type
    const allowedTypes = [
        'application/pdf',
        'text/plain',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];

    if (!allowedTypes.includes(file.type)) {
        showMessage('Unsupported file type. Please upload PDF, TXT, DOC, or DOCX files.', 'error');
        return;
    }

    console.log("File successfully loaded and validated");

    // Get content assertion declaration
    const contentSource = document.getElementById('contentSource').value;
    console.log("Content assertion declared as:", contentSource);

    // Show loading state
    showMessage('Analyzing file with declared content type...', 'info');
    showLoading(true);

    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('content_assertion', contentSource);

        console.log("Sending file for evaluation:", file.name);
        console.log("File size:", file.size, "bytes");
        console.log("File type:", file.type);
        console.log("Content assertion:", contentSource);

        const response = await fetch('/evaluate', {
            method: 'POST',
            body: formData
        });

        console.log("Response status:", response.status);
        console.log("Response headers:", Object.fromEntries(response.headers.entries()));

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log("Evaluation results:", result);

        if (result.status === 'success') {
            displayResults(result.trust_evaluation);
            showMessage('Analysis complete!', 'success');
        } else {
            throw new Error(result.message || 'Evaluation failed');
        }

    } catch (error) {
        console.error('Error during file upload:', error);
        showMessage(`Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function displayResults(response) {
    // Hide loading indicator
    showLoading(false);

    // Display trust score
    document.getElementById('trustScoreValue').innerText = (response.trust_score * 100).toFixed(2) + '%';
    document.getElementById('trustScoreLabel').innerText = response.trust_level;

    // Display component scores
    document.getElementById('sourceDataGrapplerScore').innerText = (response.module_scores.source_data_grappler * 100).toFixed(2) + '%';
    document.getElementById('assertionIntegrityScore').innerText = (response.module_scores.assertion_integrity * 100).toFixed(2) + '%';
    document.getElementById('confidenceComputationScore').innerText = (response.module_scores.confidence_computation * 100).toFixed(2) + '%';
    document.getElementById('zeroFabricationScore').innerText = (response.module_scores.zero_fabrication * 100).toFixed(2) + '%';

    // Show results
    document.getElementById('resultsContainer').classList.remove('hidden');
    document.getElementById('trustScore').classList.remove('hidden');
    document.getElementById('disclaimer').classList.remove('hidden');
    document.getElementById('insights').classList.remove('hidden');
    document.getElementById('componentScores').classList.remove('hidden');

    // Display disclaimer
    const disclaimerContainer = document.getElementById('disclaimer');
    if (disclaimerContainer && response.disclaimer) {
        disclaimerContainer.innerHTML = `
            <div class="disclaimer-box">
                <h4>📋 Score Explanation</h4>
                <p class="disclaimer-text">${response.disclaimer}</p>
            </div>
        `;
    }

    // Display insights
    const insightsContainer = document.getElementById('insights');
    if (insightsContainer && response.insights) {
        insightsContainer.innerHTML = `
            <h4>🔍 Analysis Insights</h4>
            <ul>
                ${response.insights.map(insight => `<li>${insight}</li>`).join('')}
            </ul>
        `;
    }

}
function showLoading(isLoading) {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = isLoading ? 'flex' : 'none';
    }
}

function showMessage(message, type = 'info') {
    const messageBox = document.getElementById('messageBox');
    if (messageBox) {
        messageBox.textContent = message;
        messageBox.className = `message-box ${type}`;
        messageBox.classList.remove('hidden');

        // Hide the message after 5 seconds
        setTimeout(() => {
            messageBox.classList.add('hidden');
        }, 5000);
    }
}