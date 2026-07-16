// Initialize Lucide Icons for modern scalable vector icons
lucide.createIcons();

// --- Configuration (DO NOT MODIFY, PRESERVES EXISTING BACKEND) ---
const API_URL = "http://127.0.0.1:8000";
const WS_URL = "ws://127.0.0.1:8000/ws/alerts";

// --- SPA Navigation Engine ---
const menuItems = document.querySelectorAll('.menu-item[data-target]');
const pageViews = document.querySelectorAll('.page-view');
const dynamicPageTitle = document.getElementById('dynamic-page-title');

menuItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        // Remove active class from all nav items
        menuItems.forEach(nav => nav.classList.remove('active'));
        // Add to clicked item
        item.classList.add('active');
        
        // Update Title text (extract text without the icon)
        dynamicPageTitle.textContent = item.textContent.trim();
        
        // Hide all views
        pageViews.forEach(page => page.classList.add('hidden-view'));
        
        // Show target view
        const targetId = item.getAttribute('data-target');
        const targetView = document.getElementById(targetId);
        if(targetView) {
            targetView.classList.remove('hidden-view');
        }
    });
});

// --- DOM Elements (Preserved connections) ---
const nlpForm = document.getElementById('nlp-rule-form');
const nlpInput = document.getElementById('nlp-input');
const btnSubmitNLP = document.getElementById('btn-submit-nlp');
const rulesTableBody = document.getElementById('rules-table-body');
const realtimeAlertsFeed = document.getElementById('realtime-alerts-feed');
const alertCounter = document.getElementById('alert-counter');
const alertCounterDisplay = document.getElementById('alert-counter-display'); // Added for dashboard stats
const statRulesDisplay = document.getElementById('stat-rules');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const wsStatus = document.getElementById('ws-status');

let alertCount = 0;

// --- 1. Natural Language Rule Generation (Intact Logic) ---
nlpForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const text = nlpInput.value.trim();
    if (!text) return;

    const originalBtnText = btnSubmitNLP.innerHTML;
    btnSubmitNLP.innerHTML = `<i data-lucide="loader" class="spin"></i> Processing via BRAHMA Engine...`;
    btnSubmitNLP.disabled = true;
    lucide.createIcons(); // re-render icon

    try {
        const response = await fetch(`${API_URL}/generate-rule`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        if (response.ok) {
            nlpInput.value = '';
            fetchRules();
        } else {
            const errorData = await response.json();
            alert(`BRAHMA Engine Error: ${errorData.detail}`);
        }
    } catch (error) {
        console.error("NLP Generation Failed:", error);
        alert("Failed to connect to the BRAHMA backend services.");
    } finally {
        btnSubmitNLP.innerHTML = originalBtnText;
        btnSubmitNLP.disabled = false;
        lucide.createIcons();
    }
});

// --- 2. Rules Management (CRUD) (Intact Logic with Premium Table Styling) ---
async function fetchRules() {
    try {
        const response = await fetch(`${API_URL}/rules`);
        const rules = await response.json();
        
        rulesTableBody.innerHTML = ''; 
        
        // Update Dashboard Stats
        if(statRulesDisplay) {
            statRulesDisplay.innerHTML = `${rules.length} <span class="trend">Stable</span>`;
        }

        if (rules.length === 0) {
            rulesTableBody.innerHTML = `<tr><td colspan="7" class="table-placeholder">No active constraints in pipeline. Initialize via Command Line Intelligence.</td></tr>`;
            return;
        }

        rules.forEach(rule => {
            const tr = document.createElement('tr');
            
            const secondaryObj = rule.object2 ? rule.object2.toUpperCase() : "N/A";
            const statusClass = rule.enabled ? "status-active" : "status-inactive";
            const statusText = rule.enabled ? "Online" : "Offline";

            tr.innerHTML = `
                <td style="color: var(--text-muted);">#00${rule.id}</td>
                <td style="font-weight: 600; color: var(--text-main);">${rule.object1.toUpperCase()}</td>
                <td style="color: var(--highlight); font-weight: 500;">${rule.condition.toUpperCase()}</td>
                <td>${secondaryObj}</td>
                <td style="font-family: monospace;">${rule.distance > 0 ? rule.distance + 'px' : 'N/A'}</td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td>
                    <button class="btn-sm-delete" onclick="deleteRule(${rule.id})">Terminate</button>
                </td>
            `;
            rulesTableBody.appendChild(tr);
        });
    } catch (error) {
        console.error("Failed to fetch BRAHMA rules:", error);
    }
}

window.deleteRule = async function(ruleId) {
    if(!confirm(`WARNING: Are you sure you want to terminate constraint pipeline #00${ruleId}?`)) return;

    try {
        const response = await fetch(`${API_URL}/rules/${ruleId}`, { method: 'DELETE' });
        if (response.ok) {
            fetchRules();
        }
    } catch (error) {
        console.error("Failed to terminate rule:", error);
    }
};

// --- 3. WebSocket Real-Time Alert Manager (Intact Logic) ---
function initWebSocket() {
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
        console.log("BRAHMA WebSocket uplink established.");
        statusDot.className = "status-pulse online";
        statusText.textContent = "Uplink Established";
        wsStatus.textContent = "Secured";
        wsStatus.className = "health-value cyan-text";
    };

    ws.onmessage = (event) => {
        const alertData = JSON.parse(event.data);
        displayAlert(alertData);
    };

    ws.onclose = () => {
        console.warn("Uplink severed. Reconnecting to BRAHMA core in 5s...");
        statusDot.className = "status-pulse offline";
        statusText.textContent = "Uplink Severed. Retrying...";
        wsStatus.textContent = "Disconnected";
        wsStatus.className = "health-value";
        
        setTimeout(initWebSocket, 5000);
    };

    ws.onerror = (error) => {
        console.error("WebSocket sequence error:", error);
        ws.close();
    };
}

function displayAlert(alertData) {
    const placeholder = realtimeAlertsFeed.querySelector('.feed-placeholder');
    if (placeholder) placeholder.remove();

    alertCount++;
    alertCounter.textContent = alertCount;
    alertCounter.classList.remove('hidden');
    if(alertCounterDisplay) {
        alertCounterDisplay.innerHTML = `${alertCount} <span class="trend up">Surge</span>`;
    }

    const alertElement = document.createElement('div');
    alertElement.className = 'alert-item';
    alertElement.innerHTML = `
        <div class="alert-time">SYS_TIME: ${alertData.timestamp} | REF: #00${alertData.rule_id}</div>
        <div class="alert-msg">${alertData.message}</div>
    `;

    realtimeAlertsFeed.insertBefore(alertElement, realtimeAlertsFeed.firstChild);

    if (realtimeAlertsFeed.children.length > 50) {
        realtimeAlertsFeed.removeChild(realtimeAlertsFeed.lastChild);
    }
}

// --- Initialize Dashboard ---
fetchRules();
initWebSocket();