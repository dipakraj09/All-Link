// ---------- Theme: device ka default follow karega, manual toggle bhi available ----------
const root = document.documentElement;
const toggleBtn = document.getElementById('themeToggle');
const deviceLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
let currentTheme = deviceLight ? 'light' : 'dark';
root.setAttribute('data-theme', currentTheme);

toggleBtn.addEventListener('click', () => {
  currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
  root.setAttribute('data-theme', currentTheme);
});

// ---------- Icons (inline SVG strings) ----------
const iconLink = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 007 0l3-3a5 5 0 00-7-7l-1 1"/><path d="M14 11a5 5 0 00-7 0l-3 3a5 5 0 007 7l1-1"/></svg>`;
const iconCopy = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>`;

// ---------- links.json load aur render karna ----------
const listEl = document.getElementById('list');

async function loadLinks() {
  try {
    const res = await fetch('links.json', { cache: 'no-store' });
    if (!res.ok) throw new Error('links.json load nahi hua');
    const links = await res.json();

    if (!Array.isArray(links) || links.length === 0) {
      listEl.innerHTML = `<p class="empty">Abhi koi link nahi hai. links.json mein add karein.</p>`;
      return;
    }

    listEl.innerHTML = links.map((item, i) => {
      const shortUrl = item.shortLink.startsWith('http')
        ? item.shortLink
        : `https://${item.shortLink}`;

      return `
        <div class="row" style="animation-delay:${i * 0.045}s">
          <a class="open-link" href="${item.destination}" target="_blank" rel="noopener">
            <h3>${escapeHtml(item.title)}</h3>
            <span class="short">${iconLink}${escapeHtml(item.shortLink)}</span>
          </a>
          <button class="copy-btn" data-link="${shortUrl}">
            ${iconCopy}
            <span class="label">Copy</span>
          </button>
        </div>
      `;
    }).join('');

    attachCopyHandlers();
  } catch (err) {
    listEl.innerHTML = `<p class="error">Links load karne mein dikkat hui. links.json file check karein.</p>`;
    console.error(err);
  }
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function attachCopyHandlers() {
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const link = btn.getAttribute('data-link');
      try {
        await navigator.clipboard.writeText(link);
      } catch (e) {
        const ta = document.createElement('textarea');
        ta.value = link;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      }
      const label = btn.querySelector('.label');
      const original = label.textContent;
      btn.classList.add('copied');
      label.textContent = 'Copied';
      setTimeout(() => {
        btn.classList.remove('copied');
        label.textContent = original;
      }, 1400);
    });
  });
}

loadLinks();
