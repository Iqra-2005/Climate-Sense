// Dashboard JavaScript

let currentStep = 1;
let footprintData = null;
let analysisText = null;
let recommendationsText = null;
let challengeData = null;
let chatHistory = [];

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
});

function initializeDashboard() {
    // Username is stored in session, will be displayed if available
    // The username is set when user registers on the index page
}

function setupEventListeners() {
    // Lifestyle form
    document.getElementById('lifestyleForm').addEventListener('submit', handleLifestyleSubmit);
    
    // Step buttons
    document.getElementById('getAnalysisBtn').addEventListener('click', () => goToStep(3));
    document.getElementById('getRecommendationsBtn').addEventListener('click', () => goToStep(4));
    document.getElementById('getChallengeBtn').addEventListener('click', () => goToStep(5));
    document.getElementById('startChatBtn').addEventListener('click', () => goToStep(6));
    
    // Challenge buttons
    document.getElementById('acceptChallengeBtn').addEventListener('click', acceptChallenge);
    document.getElementById('newChallengeBtn').addEventListener('click', getNewChallenge);
    
    // Chat
    document.getElementById('sendChatBtn').addEventListener('click', sendChatMessage);
    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
    
    // Reset button
    document.getElementById('resetBtn').addEventListener('click', () => {
        if (confirm('Start a new assessment? This will reset your current progress.')) {
            window.location.href = '/';
        }
    });
}

async function handleLifestyleSubmit(e) {
    e.preventDefault();
    showLoading();
    
    const formData = new FormData(e.target);
    const inputs = {};
    for (const [key, value] of formData.entries()) {
        inputs[key] = value;
    }
    
    try {
        const response = await fetch('/api/calculate-footprint', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ inputs: inputs })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            footprintData = data.footprint;
            displayFootprintResults(data.footprint, data.disclaimer);
            goToStep(2);
        } else {
            alert('Error: ' + (data.error || 'Failed to calculate footprint'));
        }
    } catch (error) {
        hideLoading();
        alert('Network error. Please try again.');
        console.error('Error:', error);
    }
}

function displayFootprintResults(footprint, disclaimer) {
    const container = document.getElementById('footprintResults');
    
    let html = `
        <div class="footprint-metrics">
            <div class="metric-card">
                <div class="metric-value">${footprint.level}</div>
                <div class="metric-label">Footprint Level</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${footprint.total_score.toFixed(1)}</div>
                <div class="metric-label">Total Score</div>
            </div>
        </div>
        <div class="info-box">
            <p>${footprint.level_description}</p>
        </div>
        <div class="breakdown-list">
            <h3>Category Breakdown</h3>
    `;
    
    footprint.breakdown.forEach(item => {
        html += `
            <div class="breakdown-item">
                <div>
                    <div class="breakdown-item-name">${item.category}</div>
                    <div class="breakdown-item-value">${item.value} - ${item.percentage.toFixed(1)}%</div>
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${item.percentage}%"></div>
            </div>
        `;
    });
    
    html += `
        </div>
        <div class="disclaimer">
            ${disclaimer}
        </div>
    `;
    
    container.innerHTML = html;
    document.getElementById('getAnalysisBtn').style.display = 'block';
}

function getTopEmissionDrivers(footprint, count = 3) {
    if (!footprint || !footprint.breakdown) return [];

    return [...footprint.breakdown]
        .sort((a, b) => b.percentage - a.percentage)
        .slice(0, count)
        .map(item => ({
            category: item.category,
            percentage: item.percentage
        }));
}


async function goToStep(step) {
    currentStep = step;
    updateStepDisplay();
    
    // Load step content
    if (step === 3 && !analysisText) {
        await loadAnalysis();
    } else if (step === 4 && !recommendationsText) {
        await loadRecommendations();
    } else if (step === 5 && !challengeData) {
        await loadChallenge();
    }
}

function updateStepDisplay() {
    // Hide all steps
    document.querySelectorAll('.step-content').forEach(el => {
        el.classList.remove('active');
    });
    
    // Show current step
    document.getElementById(`step${currentStep}`).classList.add('active');
    
    // Update progress indicators
    document.querySelectorAll('.step').forEach((step, index) => {
        const stepNum = index + 1;
        step.classList.remove('active', 'completed');
        if (stepNum === currentStep) {
            step.classList.add('active');
        } else if (stepNum < currentStep) {
            step.classList.add('completed');
        }
    });
}


async function loadAnalysis() {
    if (!footprintData) return;

    showLoading();

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ footprint: footprintData })
        });

        const data = await response.json();
        hideLoading();

        // ✅ AI success
        if (data.success) {
            analysisText = data.analysis;

            document.getElementById('analysisResults').innerHTML =
                formatAIResponse(analysisText);

            document.getElementById('getRecommendationsBtn').style.display = 'block';

        } else {
            // ⚠️ AI failed → dynamic fallback using real footprint data
            const topDrivers = getTopEmissionDrivers(footprintData);

            let fallbackHtml = `
                <div class="info-box">
                    <strong>⚠️ AI analysis temporarily unavailable</strong>
                    <p>
                        Our AI service is currently busy. Based on your calculated
                        carbon footprint, your highest contributing categories are:
                    </p>
                    <ul>
            `;

            topDrivers.forEach(driver => {
                fallbackHtml += `
                    <li>
                        <strong>${driver.category}</strong>
                        (${driver.percentage.toFixed(1)}%)
                    </li>
                `;
            });

            fallbackHtml += `
                    </ul>
                    <p style="margin-top:1rem;">
                        🔁 Please try again shortly to receive a detailed AI explanation.
                    </p>
                </div>
            `;

            document.getElementById('analysisResults').innerHTML = fallbackHtml;
        }

    } catch (error) {
        hideLoading();
        console.error('Analysis error:', error);

        document.getElementById('analysisResults').innerHTML = `
            <div class="info-box">
                <strong>⚠️ Unable to reach AI service</strong>
                <p>
                    We couldn’t generate the AI analysis due to a temporary
                    network issue. Please try again in a few moments.
                </p>
            </div>
        `;
    }
}


async function loadRecommendations() {
    if (!footprintData || !analysisText) return;
    
    showLoading();
    try {
        const response = await fetch('/api/recommendations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                footprint: footprintData,
                analysis: analysisText 
            })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            recommendationsText = data.recommendations;
            document.getElementById('recommendationsResults').innerHTML = formatAIResponse(recommendationsText);
            document.getElementById('getChallengeBtn').style.display = 'block';
        } else {
            alert('Error: ' + (data.error || 'Failed to get recommendations'));
        }
    } catch (error) {
        hideLoading();
        alert('Network error. Please try again.');
        console.error('Error:', error);
    }
}


// ==========================
// Load a new challenge
// ==========================
async function loadChallenge() {
    if (!footprintData || !recommendationsText) return;

    showLoading();

    try {
        const response = await fetch('/api/challenge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                footprint: footprintData,
                recommendations: recommendationsText
            })
        });

        const data = await response.json();
        console.log("Challenge API response:", data);

        hideLoading();

        if (data.success) {
            challengeData = data.challenge;

            // Store challenge ID directly on the accept button
            const acceptBtn = document.getElementById('acceptChallengeBtn');
            acceptBtn.dataset.challengeId = data.challenge_id;
            acceptBtn.style.display = 'block';

            // Show other buttons
            document.getElementById('newChallengeBtn').style.display = 'block';
            document.getElementById('startChatBtn').style.display = 'block';

            console.log("Stored challengeId on button:", acceptBtn.dataset.challengeId);

            // Display challenge content
            displayChallenge(data.challenge);

        } else {
            alert('Error: ' + (data.error || 'Failed to get challenge'));
        }

    } catch (error) {
        hideLoading();
        alert('Network error. Please try again.');
        console.error('Error loading challenge:', error);
    }
}

// ==========================
// Display challenge in HTML
// ==========================
function displayChallenge(challenge) {
    const container = document.getElementById('challengeResults');
    container.innerHTML = `
        <div class="challenge-title">${challenge.title || 'Your Climate Challenge'}</div>
        <div class="challenge-section">
            <strong>What to do:</strong>
            <p>${challenge.description || 'N/A'}</p>
        </div>
        <div class="challenge-section">
            <strong>Why it matters:</strong>
            <p>${challenge.impact || 'N/A'}</p>
        </div>
        <div class="challenge-section">
            <strong>Success criteria:</strong>
            <p>${challenge.success_criteria || 'N/A'}</p>
        </div>
    `;
}

// ==========================
// Accept the current challenge
// ==========================
async function acceptChallenge() {
    try {
        const acceptBtn = document.getElementById('acceptChallengeBtn');
        const challengeId = acceptBtn.dataset.challengeId;

        if (!challengeId) {
            alert("Challenge ID is missing. Please reload the page and try again.");
            return;
        }

        console.log("Accepting challenge ID:", challengeId);

        const response = await fetch('/api/challenge/accept', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ challenge_id: challengeId })
        });

        const result = await response.json();

        if (!response.ok) {
            console.error("Accept challenge error:", result);
            alert(result.error || "Failed to accept challenge");
            return;
        }

        alert("Challenge accepted! 💪");

        // Hide Accept and New Challenge buttons
        acceptBtn.style.display = 'none';
        document.getElementById('newChallengeBtn').style.display = 'none';

        // Show Download button
        const downloadBtn = document.getElementById('downloadCardBtn');
        downloadBtn.style.display = 'inline-block';

        // Get actual username from page
        const username = document.getElementById('usernameDisplay').textContent.trim();

        // Add click event to generate card
        downloadBtn.onclick = function() {
            if (!challengeData) {
                alert("No challenge data available!");
                return;
            }
            generateChallengeCard(challengeData, username);
        };

        // Update leaderboard
        loadLeaderboard();

    } catch (error) {
        console.error("Network error accepting challenge:", error);
        alert('Error accepting challenge. Please try again.');
    }
}

// ==========================
// Get a new challenge
// ==========================
function getNewChallenge() {
    challengeData = null;
    loadChallenge();

    // Hide download button for new challenge
    const downloadBtn = document.getElementById('downloadCardBtn');
    downloadBtn.style.display = 'none';

    // Show accept button again
    const acceptBtn = document.getElementById('acceptChallengeBtn');
    acceptBtn.style.display = 'inline-block';
}



async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addChatMessage('user', message);
    input.value = '';
    
    // Add to history
    chatHistory.push({ role: 'user', content: message });
    
    showLoading();
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                footprint_profile: footprintData || {},
                chat_history: chatHistory,
                current_challenge: challengeData?.title || null
            })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            addChatMessage('assistant', data.response);
            chatHistory.push({ role: 'assistant', content: data.response });
        } else {
            addChatMessage('assistant', 'Sorry, I encountered an error. Please try again.');
        }
    } catch (error) {
        hideLoading();
        addChatMessage('assistant', 'Network error. Please try again.');
        console.error('Error:', error);
    }
}

function addChatMessage(role, content) {
    const container = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    messageDiv.innerHTML = `
        <div class="message-content">${content}</div>
    `;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}


function formatAIResponse(text) {
    if (!text) return '';

    return text
        // Headings
        .replace(/^### (.*)$/gm, '<h3>$1</h3>')
        .replace(/^## (.*)$/gm, '<h2>$1</h2>')

        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

        // Bullet points
        .replace(/^\* (.*)$/gm, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')

        // Line breaks
        .replace(/\n\n/g, '<br><br>');
}


function toggleLeaderboard() {
    const panel = document.getElementById('leaderboardPanel');
    panel.classList.toggle('hidden');

    if (!panel.classList.contains('hidden')) {
        loadLeaderboard();
    }
}

document.getElementById('leaderboardBtn')
    .addEventListener('click', toggleLeaderboard);



function loadLeaderboard() {
    fetch('/api/leaderboard')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('leaderboardContainer');
            container.innerHTML = '';

// Add the header row
            container.innerHTML += `
                <div class="leaderboard-header-row">
                    <span class="rank">Sr. No</span>
                    <span class="username">Name</span>
                    <span class="count">Challenges Accepted</span>
                </div>
            `;



            const trophyEmojis = ['🥇', '🥈', '🥉']; // Top 3
            const bgColors = ['#ffe02fff', '#C0C0C0', '#f9c48fff']; // Gold, Silver, Bronze

            data.leaderboard.forEach((user, index) => {
                const trophy = index < 3 ? trophyEmojis[index] + ' ' : '';
                const bgColor = index < 3 ? bgColors[index] : '#fff'; // Highlight top 3

                container.innerHTML += `
                    <div class="leaderboard-card" style="background-color: ${bgColor};">
                        <span class="rank">${trophy}#${index + 1}</span>
                        <span class="username">${user.username}</span>
                        <span class="count">${user.accepted_count} 🌱</span>
                    </div>
                `;
            });
        });
}


function generateChallengeCard(challenge, username) {
    const canvas = document.createElement('canvas');
    canvas.width = 1200;
    canvas.height = 700;
    const ctx = canvas.getContext('2d');

    // ========================
    // Background color same as first page
    // ========================
    ctx.fillStyle = '#f4f7f6'; // matching the landing page background
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // ========================
    // Card container with shadow
    // ========================
    const cardX = 50;
    const cardY = 50;
    const cardWidth = canvas.width - 100;
    const cardHeight = canvas.height - 100;
    ctx.shadowColor = 'rgba(0,0,0,0.15)';
    ctx.shadowBlur = 20;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 10;

    ctx.fillStyle = '#ffffff'; // card background
    roundRect(ctx, cardX, cardY, cardWidth, cardHeight, 30, true, false);

    ctx.shadowColor = 'transparent'; // remove shadow for text

    // ========================
    // Logo & App Name at top
    // ========================
    ctx.fillStyle = '#4CAF50';
    ctx.font = 'bold 40px Inter';
    ctx.textAlign = 'left';
    ctx.fillText("🌍 ClimateSense", cardX + 40, cardY + 80);

    // Optional tagline below logo
    ctx.fillStyle = '#555';
    ctx.font = '20px Inter';
    ctx.fillText("AI Climate Action & Carbon Footprint Reduction Agent", cardX + 40, cardY + 120);

    // ========================
    // User Name
    // ========================
    ctx.fillStyle = '#333';
    ctx.font = 'bold 36px Inter';
    ctx.textAlign = 'center';
    ctx.fillText(username, canvas.width / 2, cardY + 220);

    // ========================
    // Challenge Title Box
    // ========================
    const boxX = canvas.width / 2 - 450;
    const boxY = cardY + 260;
    const boxWidth = 900;
    const boxHeight = 100;

    ctx.fillStyle = '#E8F5E9'; // light green accent
    roundRect(ctx, boxX, boxY, boxWidth, boxHeight, 20, true, false);

    ctx.strokeStyle = '#4CAF50';
    ctx.lineWidth = 4;
    roundRect(ctx, boxX, boxY, boxWidth, boxHeight, 20, false, true);

    ctx.fillStyle = '#2E7D32';
    ctx.font = 'bold 28px Inter';
    ctx.fillText(challenge.title || "Your Climate Challenge", canvas.width / 2, boxY + 60);

    // ========================
    // Challenge Description
    // ========================
    ctx.fillStyle = '#555';
    ctx.font = '20px Inter';
    wrapText(ctx, challenge.description || "", canvas.width / 2, boxY + 140, 900, 28);

    // ========================
    // Footer tagline
    // ========================
    ctx.font = '18px Inter';
    ctx.fillStyle = '#777';
    ctx.textAlign = 'center';
    ctx.fillText("I accepted this challenge on ClimateSense", canvas.width / 2, canvas.height - 70);

    // ========================
    // Trigger download
    // ========================
    const link = document.createElement('a');
    link.download = 'my_climate_challenge.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
}

// ========================
// Helper: Wrap Text
// ========================
function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
    const words = text.split(' ');
    let line = '';
    for (let n = 0; n < words.length; n++) {
        const testLine = line + words[n] + ' ';
        const metrics = ctx.measureText(testLine);
        if (metrics.width > maxWidth && n > 0) {
            ctx.fillText(line, x, y);
            line = words[n] + ' ';
            y += lineHeight;
        } else {
            line = testLine;
        }
    }
    ctx.fillText(line, x, y);
}

// ========================
// Helper: Rounded Rectangle
// ========================
function roundRect(ctx, x, y, width, height, radius, fill, stroke) {
    if (typeof stroke === 'undefined') stroke = true;
    if (typeof radius === 'undefined') radius = 5;
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    if (fill) ctx.fill();
    if (stroke) ctx.stroke();
}



function showAIQuotaMessage() {
    const msg = document.getElementById("aiStatusMessage");
    msg.className = "ai-status-message warning";
    msg.innerText = "⚠️ AI is temporarily busy. Please try again in a few seconds.'Go to New Assessment to reset in sometime.'";
    msg.style.display = "block";

    setTimeout(() => {
        msg.style.display = "none";
    }, 6000);
}
