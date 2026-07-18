// Initialize Lucide Icons for modern scalable vector icons
lucide.createIcons();

// --- Configuration (DO NOT MODIFY, PRESERVES EXISTING BACKEND) ---
const API_URL = "http://127.0.0.1:8000";

// --- SPA Navigation Engine ---
const menuItems = document.querySelectorAll('.menu-item[data-target]');
const pageViews = document.querySelectorAll('.page-view');
const dynamicPageTitle = document.getElementById('dynamic-page-title');

menuItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        menuItems.forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');
        dynamicPageTitle.textContent = item.textContent.trim();
        pageViews.forEach(page => page.classList.add('hidden-view'));
        const targetId = item.getAttribute('data-target');
        const targetView = document.getElementById(targetId);
        if(targetView) {
            targetView.classList.remove('hidden-view');
        }
    });
});

// --- DOM Elements ---
const nlpForm = document.getElementById('nlp-rule-form');
const nlpInput = document.getElementById('nlp-input');
const btnSubmitNLP = document.getElementById('btn-submit-nlp');
const rulesTableBody = document.getElementById('rules-table-body');
const realtimeAlertsFeed = document.getElementById('realtime-alerts-feed');
const alertCounter = document.getElementById('alert-counter');
const alertCounterDisplay = document.getElementById('alert-counter-display'); 
const statRulesDisplay = document.getElementById('stat-rules');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const wsStatus = document.getElementById('ws-status');

// Added data store for live relative time tracking
let alertCount = 0;
let alertsDataStore = []; 

// --- 1. Natural Language Rule Generation ---
nlpForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const text = nlpInput.value.trim();
    if (!text) return;

    const originalBtnText = btnSubmitNLP.innerHTML;
    btnSubmitNLP.innerHTML = `<i data-lucide="loader" class="spin"></i> Processing via BRAHMA Engine...`;
    btnSubmitNLP.disabled = true;
    lucide.createIcons();

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
        alert("Failed to connect to the backend services.");
    } finally {
        btnSubmitNLP.innerHTML = originalBtnText;
        btnSubmitNLP.disabled = false;
        lucide.createIcons();
    }
});

// --- 2. Rules Management (CRUD) ---
async function fetchRules() {
    try {
        const response = await fetch(`${API_URL}/rules`);
        const rules = await response.json();
        
        rulesTableBody.innerHTML = ''; 
        
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
        console.error("Failed to fetch rules:", error);
    }
}

window.deleteRule = async function(ruleId) {
    if(!confirm(`WARNING: Are you sure you want to terminate constraint pipeline #00${ruleId}?`)) return;
    try {
        const response = await fetch(`${API_URL}/rules/${ruleId}`, { method: 'DELETE' });
        if (response.ok) fetchRules();
    } catch (error) {
        console.error("Failed to terminate rule:", error);
    }
};

// --- 3. Bulletproof Alert Manager (High-Speed HTTP Polling) ---
// This bypasses the Python WebSocket thread crash completely!

let lastAlertTime = 0; // Tracks the last time we showed a UI alert to prevent spam

async function fetchLiveAlerts() {
    try {
        const response = await fetch(`${API_URL}/alerts`);
        if (response.ok) {
            const alerts = await response.json();
            
            // If the backend YOLO pipeline has detected an alert in the current frame
            if (alerts && alerts.length > 0) {
                const now = Date.now();
                
                // Debounce: Only trigger a new UI card if 3 seconds have passed since the last one
                if (now - lastAlertTime > 3000) {
                    alerts.forEach(alert => displayAlert(alert));
                    lastAlertTime = now;
                }
            }

            // Update UI to show successful connection
            statusDot.className = "status-pulse online";
            statusText.textContent = "Uplink Established (API)";
            wsStatus.textContent = "Secured";
            wsStatus.className = "health-value cyan-text";
        }
    } catch (error) {
        statusDot.className = "status-pulse offline";
        statusText.textContent = "Uplink Severed...";
        wsStatus.textContent = "Disconnected";
        wsStatus.className = "health-value";
        wsStatus.style.color = "var(--sev-critical-border)";
    }
}

// Poll the backend every 500 milliseconds for instant alerts
setInterval(fetchLiveAlerts, 500);

// ENTERPRISE UPGRADE: Premium Alert Card Generation
function displayAlert(alertData) {
    const placeholder = realtimeAlertsFeed.querySelector('.feed-placeholder');
    if (placeholder) placeholder.remove();

    // 1. Update Live Counters
    alertCount++;
    if(alertCounter) { alertCounter.textContent = alertCount; alertCounter.classList.remove('hidden'); }
    if(alertCounterDisplay) { alertCounterDisplay.innerHTML = `${alertCount} <span class="trend up">Surge</span>`; }
    
    const sevCounterCritical = document.querySelector('.sev-count.critical');
    if(sevCounterCritical) { sevCounterCritical.textContent = alertCount; } 

    // 2. Data Mapping
    const creationTime = new Date();
    const uid = 'alert-' + Date.now();
    alertsDataStore.push({ id: uid, timestamp: creationTime });

    const severityClass = "sev-critical"; 
    const severityLabel = "CRITICAL";
    const ruleName = `Constraint #00${alertData.rule_id || 'X'} Breach`;
    const cameraName = "Camera 01 (Entrance)";
    const statusLabel = "Active";

    // 3. Build Card HTML
    const alertElement = document.createElement('div');
    alertElement.className = `alert-card ${severityClass}`;
    alertElement.id = uid;
    
    alertElement.innerHTML = `
        <div class="alert-card-header">
            
                <span class="icon">🔴</span> ${severityLabel}
            </div>
            <div class="alert-timestamp">
                <span class="alert-time-absolute">TIME: ${alertData.timestamp || creationTime.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'})}</span>
                
            </div>
        </div>
        
        
        
        <div class="alert-meta-grid">
            <div class="meta-item">
                <span class="meta-label">Camera</span>
                <span class="meta-val">${cameraName}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Status</span>
                <span class="meta-val" style="color: var(--sev-critical-border)">${statusLabel}</span>
            </div>
        </div>

        <div class="alert-description">
            ${alertData.message || "Object detection constraints triggered by YOLO pipeline."}
        </div>
    `;

    // 4. Inject into feed
    realtimeAlertsFeed.insertBefore(alertElement, realtimeAlertsFeed.firstChild);

    // 5. Cleanup to prevent memory leaks
    if (realtimeAlertsFeed.children.length > 50) {
        realtimeAlertsFeed.removeChild(realtimeAlertsFeed.lastChild);
        alertsDataStore.shift(); 
    }
}

// ENTERPRISE UPGRADE: Live Relative Time Engine
function updateRelativeTimes() {
    const now = new Date();
    alertsDataStore.forEach(alert => {
        const el = document.getElementById(`rel-${alert.id}`);
        if (!el) return;
        
        const diffInSeconds = Math.floor((now - alert.timestamp) / 1000);
        
        if (diffInSeconds < 5) {
            el.textContent = "Just now";
        } else if (diffInSeconds < 60) {
            el.textContent = `${diffInSeconds} sec ago`;
        } else if (diffInSeconds < 3600) {
            const mins = Math.floor(diffInSeconds / 60);
            el.textContent = `${mins} min ago`;
        } else {
            const hrs = Math.floor(diffInSeconds / 3600);
            el.textContent = `${hrs} hr ago`;
        }
    });
}

setInterval(updateRelativeTimes, 1000);

// --- Initialize Dashboard ---
fetchRules();
