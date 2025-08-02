
class TrustGraphedApp {
    constructor() {
        this.form = document.getElementById('evaluationForm');
        this.contentInput = document.getElementById('contentInput');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.btnText = document.getElementById('btnText');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.resultsSection = document.getElementById('resultsSection');
        this.errorSection = document.getElementById('errorSection');
        
        this.init();
    }

    init() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Test backend connection on load
        this.testConnection();
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
        
        const content = this.contentInput.value.trim();
        
        if (!content || content.length < 10) {
            this.showError('Please enter at least 10 characters of content to analyze.');
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
            this.analyzeBtn.disabled = false;
            this.btnText.classList.remove('hidden');
            this.loadingSpinner.classList.add('hidden');
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
