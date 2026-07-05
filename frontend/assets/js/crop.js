// Crop Recommendation Form Handler
const cropForm = document.getElementById('cropForm');
if (cropForm) {
    cropForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            nitrogen: parseFloat(document.getElementById('nitrogen').value),
            phosphorus: parseFloat(document.getElementById('phosphorus').value),
            potassium: parseFloat(document.getElementById('potassium').value),
            temperature: parseFloat(document.getElementById('temperature').value),
            humidity: parseFloat(document.getElementById('humidity').value),
            ph: parseFloat(document.getElementById('ph').value),
            rainfall: parseFloat(document.getElementById('rainfall').value),
            season: document.getElementById('season').value
        };
        
        try {
            const response = await fetch(`${CONFIG.API_URL}${CONFIG.ENDPOINTS.CROP.RECOMMEND}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${Utils.getToken()}`
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                displayRecommendations(data.recommendations, data.soil_analysis);
                Utils.showNotification('Recommendations generated!', 'success');
            } else {
                Utils.showNotification(data.message || 'Failed to get recommendations', 'error');
            }
        } catch (error) {
            Utils.showNotification('Network error. Please try again.', 'error');
            console.error('Recommendation error:', error);
        }
    });
}

function displayRecommendations(recommendations, soilAnalysis) {
    const resultsCard = document.getElementById('resultsCard');
    const recommendationsDiv = document.getElementById('recommendations');
    const soilAnalysisDiv = document.getElementById('soilAnalysis');
    
    // Show results card
    resultsCard.style.display = 'block';
    
    // Display recommendations
    recommendationsDiv.innerHTML = recommendations.map((rec, index) => `
        <div class="recommendation-item">
            <div class="rank">#${index + 1}</div>
            <div class="crop-info">
                <h4>${rec.crop}</h4>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${rec.confidence}%"></div>
                </div>
                <p>${rec.confidence.toFixed(1)}% Match</p>
            </div>
        </div>
    `).join('');
    
    // Display soil analysis
    soilAnalysisDiv.innerHTML = `
        <div class="soil-params">
            <div class="param-item">
                <span class="param-label">Nitrogen (N)</span>
                <span class="param-value">${soilAnalysis.nitrogen}</span>
            </div>
            <div class="param-item">
                <span class="param-label">Phosphorus (P)</span>
                <span class="param-value">${soilAnalysis.phosphorus}</span>
            </div>
            <div class="param-item">
                <span class="param-label">Potassium (K)</span>
                <span class="param-value">${soilAnalysis.potassium}</span>
            </div>
            <div class="param-item">
                <span class="param-label">pH Level</span>
                <span class="param-value">${soilAnalysis.ph}</span>
            </div>
        </div>
    `;
    
    // Scroll to results
    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}