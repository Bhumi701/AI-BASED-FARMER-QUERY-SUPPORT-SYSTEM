// Disease Detection Form Handler
const diseaseForm = document.getElementById('diseaseForm');
if (diseaseForm) {
    diseaseForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const cropName = document.getElementById('cropName').value;
        const imageFile = document.getElementById('imageUpload').files[0];
        
        if (!imageFile) {
            Utils.showNotification('Please select an image', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('crop_name', cropName);
        
        try {
            Utils.showNotification('Analyzing image...', 'success');
            
            const response = await fetch(`${CONFIG.API_URL}${CONFIG.ENDPOINTS.DISEASE.DETECT}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${Utils.getToken()}`
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                displayDetectionResults(data);
                Utils.showNotification('Detection complete!', 'success');
            } else {
                Utils.showNotification(data.message || 'Detection failed', 'error');
            }
        } catch (error) {
            Utils.showNotification('Network error. Please try again.', 'error');
            console.error('Detection error:', error);
        }
    });
}

function displayDetectionResults(data) {
    const resultsCard = document.getElementById('resultsCard');
    const resultsDiv = document.getElementById('detectionResults');
    
    // Show results card
    resultsCard.style.display = 'block';
    
    // Display results
    resultsDiv.innerHTML = `
        <div class="detection-result">
            <div class="disease-header">
                <h4>${data.disease}</h4>
                <span class="confidence-badge">${data.confidence.toFixed(1)}% Confidence</span>
            </div>
            
            <div class="result-section">
                <h5>🔍 Symptoms</h5>
                <p>${data.symptoms}</p>
            </div>
            
            <div class="result-section">
                <h5>💊 Treatment</h5>
                <p>${data.treatment}</p>
            </div>
            
            <div class="result-section">
                <h5>🛡️ Prevention</h5>
                <p>${data.prevention}</p>
            </div>
        </div>
    `;
    
    // Scroll to results
    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}