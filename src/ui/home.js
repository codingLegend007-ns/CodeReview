/* =========================
   Utility & State
   ========================= */
const DEFAULT_GEMINI_MODEL = 'gemini-2.5-flash';
const GEMINI_MODEL_ALIASES = {
  'gemini-1.5-flash': 'gemini-2.5-flash',
  'gemini-1.5-flash-latest': 'gemini-2.5-flash',
  'gemini-1.5-pro': 'gemini-2.0-flash',
  'gemini-1.5-pro-latest': 'gemini-2.0-flash',
  '1.5-flash': 'gemini-2.5-flash',
  '1.5-pro': 'gemini-2.0-flash',
  'gemini-2.0-flash-latest': 'gemini-2.0-flash',
  'gemini-flash-latest': 'gemini-2.5-flash',
  'gemini-flash': 'gemini-2.5-flash',
  'flash': 'gemini-2.5-flash',
  'pro': 'gemini-2.0-flash',
};

const els = {
  ghToken: document.getElementById('ghToken'),
  geminiKey: document.getElementById('geminiKey'),
  geminiModel: document.getElementById('geminiModel'),
  repoOwner: document.getElementById('repoOwner'),
  repoName: document.getElementById('repoName'),
  maxFiles: document.getElementById('maxFiles'),
  maxChars: document.getElementById('maxChars'),
  btnValidate: document.getElementById('btnValidate'),
  btnFetch: document.getElementById('btnFetch'),
  btnReview: document.getElementById('btnReview'),
  credStatus: document.getElementById('credStatus'),
  prList: document.getElementById('prList'),
  reviews: document.getElementById('reviews'),
  reviewContent: document.getElementById('reviewsContent'),
  ldrFetch: document.getElementById('ldrFetch'),
  reviewSpinner: document.getElementById('reviewSpinner'),
  reviewSpinnerTitle: document.querySelector('#reviewSpinner [data-spinner-title]'),
  reviewSpinnerSubtitle: document.querySelector('#reviewSpinner [data-spinner-subtitle]'),
};

let PRS = [];             // Fetched PR metadata
let REVIEW_RESULTS = {};  // Map PR number -> backend review response

if (els.geminiModel && !els.geminiModel.value) {
  els.geminiModel.value = DEFAULT_GEMINI_MODEL;
}

function sanitize(str) {
  // Basic sanitation to avoid injection into HTML
  return (str ?? '')
    .replace(/[<>&]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));
}

function groupAgentOutput(output) {
  const groups = [];
  let current = null;

  String(output ?? '')
    .split(/\r?\n/)
    .forEach(rawLine => {
      const line = rawLine.trim();
      if (!line) return;

      const headerMatch = line.match(/^\*\*(.+?)\*\*$/);
      if (headerMatch) {
        const header = headerMatch[1].trim() || 'General';
        current = { header, items: [] };
        groups.push(current);
        return;
      }

      if (!current) {
        current = { header: 'General', items: [] };
        groups.push(current);
      }

      current.items.push(line);
    });

  return groups;
}

function formatAgentLine(line) {
  const trimmed = line.trim();
  const lower = trimmed.toLowerCase();
  const fixIndex = lower.indexOf('fix:');

  let issuePart = trimmed;
  let fixPart = '';

  if (fixIndex !== -1) {
    issuePart = trimmed.slice(0, fixIndex).trim();
    fixPart = trimmed.slice(fixIndex + 4).trim();
  }

  let lineLabel = 'Line ?';
  let issueText = issuePart;

  const lineMatch = issuePart.match(/^Line\s+([^:]+):\s*(.*)$/i);
  if (lineMatch) {
    lineLabel = `Line ${lineMatch[1].trim() || '?'}`;
    issueText = lineMatch[2].trim() || 'Issue details missing.';
  } else if (/^Unknown/i.test(issuePart)) {
    lineLabel = 'Line Unknown';
    issueText = issuePart.replace(/^Unknown\s*:?\s*/i, '').trim() || 'Issue details missing.';
  }

  if (!issueText) {
    issueText = 'Issue details missing.';
  }

  return {
    lineLabel,
    issueText,
    fixText: fixPart,
  };
}

function renderAgentOutput(output) {
  const groups = groupAgentOutput(output);
  if (!groups.length) {
    return `<p class="agent-empty">${sanitize(output || 'No output provided.')}</p>`;
  }

  const renderedGroups = groups.map(group => {
    const headerHtml = `<div class="agent-header">${sanitize(group.header || 'General')}</div>`;
    const itemsHtml = (group.items && group.items.length)
      ? group.items.map(item => {
          const parsed = formatAgentLine(item);
          const lineLabel = sanitize(parsed.lineLabel);
          const issue = sanitize(parsed.issueText);
          const fix = parsed.fixText
            ? `<div class="line-fix"><span>Fix:</span> ${sanitize(parsed.fixText)}</div>`
            : '';
          return `<div class="review-line"><div class="line-label">${lineLabel}</div><div class="line-issue">${issue}</div>${fix}</div>`;
        }).join('')
      : '<div class="review-line agent-empty">No findings reported.</div>';

    return `<div class="agent-group">${headerHtml}${itemsHtml}</div>`;
  });

  return renderedGroups.join('<hr class="agent-divider" />');
}

function normalizeGeminiModel(modelName) {
  const trimmed = (modelName || '').trim();
  if (!trimmed) return DEFAULT_GEMINI_MODEL;

  const withoutPrefix = trimmed.replace(/^models\//i, '');
  const lower = withoutPrefix.toLowerCase();

  if (GEMINI_MODEL_ALIASES[lower]) {
    return GEMINI_MODEL_ALIASES[lower];
  }

  if (lower.startsWith('gemini-1.5-') && !lower.endsWith('-latest')) {
    return `${lower}-latest`;
  }

  return lower;
}

function setLoading(elButton, elLoader, loading) {
  elButton.disabled = loading;
  if (elLoader) {
    elLoader.style.display = loading ? 'inline-block' : 'none';
  }
  // Handle fetch icon animation
  const fetchIcon = document.getElementById('fetchIcon');
  if (fetchIcon) {
    if (loading && elButton.id === 'btnFetch') {
      fetchIcon.classList.add('is-spinning');
    } else {
      fetchIcon.classList.remove('is-spinning');
    }
  }
}

function showReviewSpinner(
  title = 'Review in progress…',
  subtitle = 'Hang tight while the agents analyze these pull requests.'
) {
  const spinner = els.reviewSpinner;
  if (!spinner) {
    return;
  }

  if (els.reviewSpinnerTitle) {
    els.reviewSpinnerTitle.textContent = title;
  }
  if (els.reviewSpinnerSubtitle) {
    els.reviewSpinnerSubtitle.textContent = subtitle;
  }

  spinner.classList.add('is-active');
  spinner.setAttribute('aria-hidden', 'false');
}

function hideReviewSpinner(delay = 0) {
  const spinner = els.reviewSpinner;
  if (!spinner) {
    return;
  }

  const reset = () => {
    spinner.classList.remove('is-active');
    spinner.setAttribute('aria-hidden', 'true');
  };

  if (delay > 0) {
    setTimeout(reset, delay);
  } else {
    reset();
  }
}

function enableActions() {
  const tokensValid = !!els.ghToken.value && !!els.geminiKey.value;
  els.btnFetch.disabled = !tokensValid;
  // Review only enabled after PRs fetched
  els.btnReview.disabled = !(tokensValid && PRS.length > 0);
}

/* =========================
   Validation
   ========================= */
els.btnValidate.addEventListener('click', () => {
  const gh = els.ghToken.value.trim();
  const gm = els.geminiKey.value.trim();
  if (!gh || !gm) {
    els.credStatus.textContent = 'Status: Missing tokens';
    els.credStatus.style.color = '#ffb347';
  } else {
    els.credStatus.textContent = 'Status: OK';
    els.credStatus.style.color = '#42c980';
  }
  enableActions();
});

/* =========================
   Fetch PRs
   ========================= */
els.btnFetch.addEventListener('click', async () => {
  const owner = els.repoOwner.value.trim();
  const repo = els.repoName.value.trim();
  if (!owner || !repo) {
    alert('Please enter owner and repository name.');
    return;
  }
  setLoading(els.btnFetch, els.ldrFetch, true);
  els.prList.innerHTML = '';
  if (els.reviewContent) {
    els.reviewContent.innerHTML = '<div class="success-box" data-review-placeholder="true">Select "Perform Code Review" to analyze the listed pull requests.</div>';
  }
  hideReviewSpinner();
  REVIEW_RESULTS = {};
  PRS = [];

  try {
    const url = `https://api.github.com/repos/${owner}/${repo}/pulls?state=open&per_page=50`;
    const res = await fetch(url, {
      headers: {
        'Authorization': `token ${els.ghToken.value.trim()}`,
        'Accept': 'application/vnd.github+json'
      }
    });
    if (!res.ok) {
      const txt = await res.text();
      throw new Error(`GitHub API error ${res.status}: ${txt}`);
    }
    const data = await res.json();
    PRS = data.map(pr => ({
      number: pr.number,
      title: pr.title,
      created_at: pr.created_at,
      user: pr.user?.login,
      url: pr.html_url,
    }));
    renderPRs();
    enableActions();
  } catch (e) {
    els.prList.innerHTML = `<div class="error-box">Failed to fetch PRs:\n${sanitize(e.message)}</div>`;
  } finally {
    setLoading(els.btnFetch, els.ldrFetch, false);
  }
});

function renderPRs() {
  if (!PRS.length) {
    els.prList.innerHTML = `<div class="pr-item"><h3>No open pull requests.</h3></div>`;
    return;
  }
  els.prList.innerHTML = '<h2>Open Pull Requests</h2>' + PRS.map(pr => `
    <div class="pr-item" data-pr="${pr.number}">
      <h3>#${pr.number} – ${sanitize(pr.title)}</h3>
      <div class="meta-line">
        <span>Opened: ${new Date(pr.created_at).toLocaleString()}</span>
        <span>By: ${sanitize(pr.user)}</span>
        <a href="${sanitize(pr.url)}" target="_blank" rel="noopener">View on GitHub ↗</a>
      </div>
    </div>
  `).join('');
}

/* =========================
   Perform AI Code Review
   ========================= */
els.btnReview.addEventListener('click', async () => {
  if (!PRS.length) {
    alert('No PRs to review.');
    return;
  }
  setLoading(els.btnReview, null, true);
  const totalPRs = PRS.length;
  if (totalPRs > 0) {
    const subtitle = totalPRs > 1
      ? `Processing ${totalPRs} pull requests. This may take a minute.`
      : `Analyzing pull request #${PRS[0].number}.`;
    showReviewSpinner('Review in progress…', subtitle);
  }
  if (els.reviewContent) {
    els.reviewContent.innerHTML = '<div class="success-box" data-review-placeholder="true">Review in progress – please wait...</div>';
  }
  REVIEW_RESULTS = {};

  const owner = els.repoOwner.value.trim();
  const repo = els.repoName.value.trim();
  const maxFiles = parseInt(els.maxFiles.value, 10);
  const maxChars = parseInt(els.maxChars.value, 10);
  const geminiModel = normalizeGeminiModel(els.geminiModel?.value);

  if (els.geminiModel) {
    els.geminiModel.value = geminiModel;
  }

  let completed = 0;
  for (const pr of PRS) {
    const subtitle = totalPRs > 1
      ? `Analyzing PR ${completed + 1} of ${totalPRs} (#${pr.number}).`
      : `Analyzing pull request #${pr.number}.`;
    showReviewSpinner('Review in progress…', subtitle);
    try {
      const review = await runMultiAgentReview({
        repoOwner: owner,
        repoName: repo,
        prNumber: pr.number,
        geminiModel,
        maxFiles,
        maxDiffChars: maxChars,
      });
      REVIEW_RESULTS[pr.number] = { data: review };
    } catch (error) {
      REVIEW_RESULTS[pr.number] = { error: error?.message || 'Review failed' };
    }
    renderReview(pr.number);
    completed += 1;
  }

  hideReviewSpinner(700);
  setLoading(els.btnReview, null, false);
});

async function runMultiAgentReview({
  repoOwner,
  repoName,
  prNumber,
  geminiModel,
  maxFiles,
  maxDiffChars,
}) {
  const githubToken = els.ghToken.value.trim();
  const geminiKey = els.geminiKey.value.trim();

  if (!githubToken || !geminiKey) {
    throw new Error('Missing credentials for GitHub or Gemini.');
  }

  const payload = {
    github_token: githubToken,
    gemini_api_key: geminiKey,
    repo_owner: repoOwner,
    repo_name: repoName,
    pr_number: prNumber,
  };

  if (geminiModel) payload.gemini_model = geminiModel;
  if (Number.isFinite(maxFiles) && maxFiles > 0) payload.max_files = maxFiles;
  if (Number.isFinite(maxDiffChars) && maxDiffChars > 0) payload.max_diff_chars = maxDiffChars;

  const res = await fetch('/api/review', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const responseText = await res.text();
  let data;
  if (responseText) {
    try {
      data = JSON.parse(responseText);
    } catch (err) {
      if (res.ok) {
        throw new Error('Received non-JSON response from review service.');
      }
    }
  }

  if (!res.ok) {
    const detail = data?.detail || data?.message || responseText || `Review failed with status ${res.status}`;
    throw new Error(detail);
  }

  if (!data || typeof data !== 'object') {
    throw new Error('Empty response from review service.');
  }

  return data;
}

function renderReview(prNumber) {
  const result = REVIEW_RESULTS[prNumber];
  const prMeta = PRS.find(p => p.number === prNumber);
  const baseId = `review-pr-${prNumber}`;

  let html = `<div class="review-item" id="${baseId}">
    <h3>Review – PR #${prNumber} (${sanitize(prMeta?.title)})</h3>
  `;

  if (!result) {
    html += '<div class="error-box">Review not found.</div></div>';
    appendOrReplace(baseId, html);
    return;
  }

  if (result.error) {
    html += `<div class="error-box">${sanitize(result.error)}</div>`;
    html += '</div>';
    appendOrReplace(baseId, html);
    return;
  }

  const review = result.data || {};
  const metadata = review.metadata || {};
  const sections = Array.isArray(review.sections) ? review.sections : [];

  const metaLines = [];
  if (Number.isFinite(metadata.files_analyzed)) {
    metaLines.push(`Files analyzed: ${metadata.files_analyzed}`);
  }
  if (Number.isFinite(metadata.files_available)) {
    metaLines.push(`Files available: ${metadata.files_available}`);
  }
  if (Array.isArray(metadata.agents_run) && metadata.agents_run.length) {
    metaLines.push(`Agents: ${metadata.agents_run.join(', ')}`);
  }

  if (metaLines.length) {
    html += `<div class="success-box">${metaLines.map(line => sanitize(line)).join('<br />')}</div>`;
  }

  if (!sections.length) {
    html += '<div class="success-box">Review completed but no detailed agent output was returned.</div></div>';
    appendOrReplace(baseId, html);
    return;
  }

  html += '<div class="review-comments">';
  sections.forEach(section => {
    const label = section.label || section.key || 'Agent Output';
    const output = section.output || 'No output provided.';
    html += `<div class="section-card">
      <h4>${sanitize(label)}</h4>
      <div class="section-output">${renderAgentOutput(output)}</div>
    </div>`;
  });
  html += '</div></div>';
  appendOrReplace(baseId, html);
}

function appendOrReplace(id, html) {
  const container = els.reviewContent || els.reviews;
  if (!container) {
    return;
  }

  const placeholder = container.querySelector('[data-review-placeholder="true"]');
  if (placeholder) {
    placeholder.remove();
  }

  const existing = document.getElementById(id);
  if (existing) {
    existing.outerHTML = html;
  } else {
    container.insertAdjacentHTML('beforeend', html);
  }
}

/* Re-enable buttons when inputs change */
['ghToken','geminiKey','geminiModel'].forEach(id => {
  els[id].addEventListener('input', enableActions);
});
