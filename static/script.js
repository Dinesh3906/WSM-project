/**
 * script.js — Frontend logic for Information Retrieval System
 *
 * Handles:
 *  - Sending search queries to the Flask backend via fetch()
 *  - Rendering results (doc IDs, filenames, snippets, wildcards)
 *  - Clear button functionality
 *  - Enter-key shortcut
 */

// DOM references
const searchInput     = document.getElementById('searchInput');
const searchBtn       = document.getElementById('searchBtn');
const clearBtn        = document.getElementById('clearBtn');
const statusBar       = document.getElementById('statusBar');
const resultsSection  = document.getElementById('resultsSection');
const resultsSummary  = document.getElementById('resultsSummary');
const wildcardBox     = document.getElementById('wildcardBox');
const resultsContainer = document.getElementById('resultsContainer');

// ------------------------------------------------------------------
// Search Handler
// ------------------------------------------------------------------
async function performSearch() {
    const query = searchInput.value.trim();

    // Client-side empty check
    if (!query) {
        showStatus('Please enter a search query.', 'warning');
        hideResults();
        return;
    }

    // Disable button to prevent double clicks
    searchBtn.disabled = true;
    searchBtn.textContent = 'Searching…';

    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => null);
            const msg = errData && errData.message ? errData.message : `Server error (${response.status})`;
            showStatus(msg, 'error');
            hideResults();
            return;
        }

        const data = await response.json();
        renderResults(data);

    } catch (err) {
        showStatus('Network error — is the server running?', 'error');
        hideResults();
    } finally {
        searchBtn.disabled = false;
        searchBtn.textContent = 'Search';
    }
}

// ------------------------------------------------------------------
// Render Results
// ------------------------------------------------------------------
function renderResults(data) {
    // Status bar
    showStatus(data.message, data.status);

    if (data.total_matching === 0) {
        hideResults();
        return;
    }

    // Summary row
    const docIdStr = data.matching_doc_ids.join(', ');
    resultsSummary.innerHTML = `
        <span>Matching: <span class="doc-ids">${docIdStr}</span>
            &nbsp;—&nbsp; <strong>${data.total_matching}</strong> document(s)
        </span>
        <span class="exec-time">${data.execution_time_ms} ms</span>
    `;

    // Wildcard expansions
    const wcKeys = Object.keys(data.expanded_wildcards || {});
    if (wcKeys.length > 0) {
        let wcHTML = '';
        for (const pattern of wcKeys) {
            const terms = data.expanded_wildcards[pattern];
            wcHTML += `<div class="wc-label">Wildcard "${escapeHTML(pattern)}" expanded to ${terms.length} term(s):</div>`;
            wcHTML += '<div class="wc-terms">';
            for (const t of terms) {
                wcHTML += `<span>${escapeHTML(t)}</span>`;
            }
            wcHTML += '</div>';
        }
        wildcardBox.innerHTML = wcHTML;
        wildcardBox.classList.remove('hidden');
    } else {
        wildcardBox.classList.add('hidden');
    }

    // Document cards
    let cardsHTML = '';
    for (const doc of data.documents) {
        // Term frequency badges
        let tfHTML = '';
        const tfs = doc.term_frequencies || {};
        for (const [term, freq] of Object.entries(tfs)) {
            tfHTML += `<span class="term-freq">${escapeHTML(term)}: ${freq}</span>`;
        }

        cardsHTML += `
        <div class="doc-card">
            <div class="doc-header">
                <span class="doc-id">${escapeHTML(doc.doc_id)}</span>
                <span class="doc-filename">${escapeHTML(doc.filename)}</span>
            </div>
            <div class="doc-snippet">${escapeHTML(doc.snippet)}</div>
            <div class="doc-meta">
                <span>${doc.char_count} chars</span>
                ${tfHTML}
            </div>
        </div>`;
    }
    resultsContainer.innerHTML = cardsHTML;

    // Show section
    resultsSection.classList.remove('hidden');
}

// ------------------------------------------------------------------
// UI Helpers
// ------------------------------------------------------------------
function showStatus(message, type) {
    statusBar.textContent = message;
    statusBar.className = 'status-bar ' + type;
    statusBar.classList.remove('hidden');
}

function hideResults() {
    resultsSection.classList.add('hidden');
    resultsContainer.innerHTML = '';
    resultsSummary.innerHTML = '';
    wildcardBox.classList.add('hidden');
}

function clearAll() {
    searchInput.value = '';
    statusBar.classList.add('hidden');
    hideResults();
    searchInput.focus();
}

function escapeHTML(str) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

// ------------------------------------------------------------------
// Event Listeners
// ------------------------------------------------------------------
searchBtn.addEventListener('click', performSearch);

clearBtn.addEventListener('click', clearAll);

searchInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        performSearch();
    }
});

// Auto-focus on page load
window.addEventListener('DOMContentLoaded', function () {
    searchInput.focus();
});
