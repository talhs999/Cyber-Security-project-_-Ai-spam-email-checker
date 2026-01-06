// Dashboard JavaScript

let classificationChart = null;
let trendChart = null;
let currentTab = 'all';

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function () {
    loadDashboardData();
    initializeCharts();

    // Auto-refresh every 30 seconds
    setInterval(refreshData, 30000);
});

// Load all dashboard data
async function loadDashboardData() {
    showLoading();

    try {
        await Promise.all([
            loadSummaryStats(),
            loadWeeklyStats(),
            loadEmails(),
            loadChartData()
        ]);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        alert('Failed to load dashboard data. Please refresh the page.');
    } finally {
        hideLoading();
    }
}

// Load summary statistics
async function loadSummaryStats() {
    try {
        const response = await fetch('/api/stats/summary');
        const data = await response.json();

        if (data.success) {
            const stats = data.data;
            document.getElementById('total-emails').textContent = stats.total_processed || 0;
            document.getElementById('safe-emails').textContent = stats.safe || 0;
            document.getElementById('suspicious-emails').textContent = stats.suspicious || 0;
            document.getElementById('spam-emails').textContent = stats.spam || 0;

            // Load threat domains
            loadThreatDomains(stats.top_threat_domains || []);
        }
    } catch (error) {
        console.error('Error loading summary stats:', error);
    }
}

// Load weekly statistics
async function loadWeeklyStats() {
    try {
        const response = await fetch('/api/stats/weekly?days=7');
        const data = await response.json();

        if (data.success && trendChart) {
            updateTrendChart(data.data);
        }
    } catch (error) {
        console.error('Error loading weekly stats:', error);
    }
}

// Load emails
async function loadEmails(classification = null) {
    try {
        let url = '/api/emails/recent?limit=50';
        if (classification) {
            url += `&classification=${classification}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            displayEmails(data.data);
        }
    } catch (error) {
        console.error('Error loading emails:', error);
    }
}

// Display emails in list
function displayEmails(emails) {
    const emailList = document.getElementById('email-list');

    if (emails.length === 0) {
        emailList.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 40px;">No emails found</p>';
        return;
    }

    emailList.innerHTML = emails.map(email => `
        <div class="email-item" onclick="showEmailDetails('${email.email_id}', ${JSON.stringify(email).replace(/"/g, '&quot;')})">
            <span class="email-badge badge-${email.classification.toLowerCase()}">
                ${email.classification}
            </span>
            <div class="email-info">
                <div class="email-sender">${escapeHtml(email.sender_email)}</div>
                <div class="email-subject">${escapeHtml(email.subject || 'No Subject')}</div>
            </div>
            <div class="email-score" style="color: ${getScoreColor(email.threat_score)}">
                ${email.threat_score}
            </div>
        </div>
    `).join('');
}

// Show email details in modal
async function showEmailDetails(emailId, emailData) {
    const modal = document.getElementById('emailModal');
    const modalBody = document.getElementById('modalBody');

    // Show loading in modal
    modalBody.innerHTML = '<p style="text-align: center;">Loading details...</p>';
    modal.classList.add('active');

    try {
        // Fetch threat indicators
        const response = await fetch(`/api/emails/${emailId}/indicators`);
        const data = await response.json();

        const indicators = data.success ? data.data : [];

        modalBody.innerHTML = `
            <div class="detail-row">
                <div class="detail-label">From</div>
                <div class="detail-value">${escapeHtml(emailData.sender_email)}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Domain</div>
                <div class="detail-value">${escapeHtml(emailData.sender_domain || 'N/A')}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Subject</div>
                <div class="detail-value">${escapeHtml(emailData.subject || 'No Subject')}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Classification</div>
                <div class="detail-value">
                    <span class="email-badge badge-${emailData.classification.toLowerCase()}">
                        ${emailData.classification}
                    </span>
                </div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Threat Score</div>
                <div class="detail-value" style="color: ${getScoreColor(emailData.threat_score)}">
                    ${emailData.threat_score}/100
                </div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Action Taken</div>
                <div class="detail-value">${escapeHtml(emailData.action_taken || 'None')}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Has Attachments</div>
                <div class="detail-value">${emailData.has_attachments ? 'Yes' : 'No'}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">URL Count</div>
                <div class="detail-value">${emailData.url_count || 0}</div>
            </div>
            ${indicators.length > 0 ? `
                <div class="detail-row">
                    <div class="detail-label">Threat Indicators</div>
                    <ul class="indicator-list">
                        ${indicators.map(ind => `
                            <li class="indicator-item">${escapeHtml(ind.indicator_description)}</li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
    } catch (error) {
        console.error('Error loading email details:', error);
        modalBody.innerHTML = '<p style="color: var(--danger-color);">Failed to load details</p>';
    }
}

// Close modal
function closeModal() {
    document.getElementById('emailModal').classList.remove('active');
}

// Load threat domains
function loadThreatDomains(domains) {
    const container = document.getElementById('threat-domains-list');

    if (domains.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 20px;">No threat domains detected</p>';
        return;
    }

    container.innerHTML = domains.map(domain => `
        <div class="threat-domain-item">
            <span class="threat-domain-name">${escapeHtml(domain.sender_domain)}</span>
            <span class="threat-domain-count">${domain.count} emails</span>
        </div>
    `).join('');
}

// Initialize charts
function initializeCharts() {
    // Classification pie chart
    const classCtx = document.getElementById('classificationChart').getContext('2d');
    classificationChart = new Chart(classCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });

    // Trend line chart
    const trendCtx = document.getElementById('trendChart').getContext('2d');
    trendChart = new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

// Load chart data
async function loadChartData() {
    try {
        // Classification chart
        const classResponse = await fetch('/api/charts/classification');
        const classData = await classResponse.json();

        if (classData.success && classificationChart) {
            classificationChart.data.labels = classData.data.labels;
            classificationChart.data.datasets[0].data = classData.data.values;
            classificationChart.data.datasets[0].backgroundColor = classData.data.colors;
            classificationChart.update();
        }

        // Trend chart
        const trendResponse = await fetch('/api/charts/weekly-trend');
        const trendData = await trendResponse.json();

        if (trendData.success && trendChart) {
            trendChart.data.labels = trendData.data.labels;
            trendChart.data.datasets = trendData.data.datasets;
            trendChart.update();
        }
    } catch (error) {
        console.error('Error loading chart data:', error);
    }
}

// Update trend chart
function updateTrendChart(stats) {
    if (!trendChart || stats.length === 0) return;

    const labels = stats.map(s => s.date).reverse();
    const safeData = stats.map(s => s.safe_count).reverse();
    const suspiciousData = stats.map(s => s.suspicious_count).reverse();
    const spamData = stats.map(s => s.spam_count).reverse();

    trendChart.data.labels = labels;
    trendChart.data.datasets = [
        {
            label: 'Safe',
            data: safeData,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.4
        },
        {
            label: 'Suspicious',
            data: suspiciousData,
            borderColor: '#f59e0b',
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            tension: 0.4
        },
        {
            label: 'Spam',
            data: spamData,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            tension: 0.4
        }
    ];
    trendChart.update();
}

// Switch tabs
function switchTab(tab) {
    currentTab = tab;

    // Update active tab button
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Load emails for selected tab
    const classification = tab === 'all' ? null : tab;
    loadEmails(classification);
}

// Refresh all data
function refreshData() {
    loadDashboardData();
}

// Export report
async function exportReport() {
    try {
        showLoading();
        window.location.href = '/api/reports/export';
    } catch (error) {
        console.error('Error exporting report:', error);
        alert('Failed to export report');
    } finally {
        setTimeout(hideLoading, 1000);
    }
}

// Reset Database
function confirmReset() {
    if (confirm('Are you sure you want to reset all data? This cannot be undone.')) {
        resetDatabase();
    }
}

async function resetDatabase() {
    try {
        showLoading();
        const response = await fetch('/api/database/reset', {
            method: 'POST'
        });
        const data = await response.json();

        if (data.success) {
            alert('Database cleared successfully!');
            refreshData();
        } else {
            alert('Failed to reset database: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error resetting database:', error);
        alert('Failed to reset database');
    } finally {
        hideLoading();
    }
}

// Utility functions
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getScoreColor(score) {
    if (score <= 30) return '#10b981';
    if (score <= 70) return '#f59e0b';
    return '#ef4444';
}

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('emailModal');
    if (event.target === modal) {
        closeModal();
    }
}
