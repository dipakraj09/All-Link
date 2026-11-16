// ---------- Theme ----------
const root = document.documentElement;
const toggleBtn = document.getElementById('themeToggle');
let currentTheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
root.setAttribute('data-theme', currentTheme);
toggleBtn.addEventListener('click', () => {
  currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
  root.setAttribute('data-theme', currentTheme);
});

// ---------- Icons ----------
const iconCopy = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>`;
const iconCheck = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 13l4 4L19 7"/></svg>`;

const listEl = document.getElementById('list');

// Purane format (shortLink/destination) bhi chalega
function normalize(item) {
  const url = item.url || item.destination || '';
  const bitly = (item.bitly || item.shortLink || '').replace(/^https?:\/\//, '');
  let title = item.title;
  if (!title) {
    try { title = new URL(url).hostname.replace(/^www\./, ''); } catch { title = bitly || 'Link'; }
  }
  return { title, url, bitly };
}

function makeCopyBtn(kind, text, copyText) {
  const btn = document.createElement('button');
  btn.className = 'copy-btn ' + kind;
  btn.type = 'button';
  btn.innerHTML = `
    <span class="ico"></span>
    <span class="txt"><b>${kind === 'bitly' ? 'BITLY' : 'URL'}</b><small></small></span>`;
  btn.querySelector('small').textContent = text;
  const ico = btn.querySelector('.ico');
  ico.innerHTML = iconCopy;

  btn.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(copyText); }
    catch {
      const ta = document.createElement('textarea');
      ta.value = copyText;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
    btn.classList.add('copied');
    ico.innerHTML = iconCheck;
    setTimeout(() => { btn.classList.remove('copied'); ico.innerHTML = iconCopy; }, 1300);
  });
  return btn;
}

async function loadLinks() {
  try {
    const res = await fetch('links.json', { cache: 'no-store' });
    if (!res.ok) throw new Error('links.json load nahi hua');
    const data = await res.json();
    if (!Array.isArray(data) || !data.length) {
      listEl.innerHTML = '<p class="empty">Abhi koi link nahi hai. links.json mein add karein.</p>';
      return;
    }
    listEl.innerHTML = '';
    data.map(normalize).forEach((item, i) => {
      const card = document.createElement('div');
      card.className = 'card';
      card.style.animationDelay = `${i * 0.04}s`;

      const a = document.createElement('a');
      a.className = 'title';
      a.href = item.url;
      a.target = '_blank';
      a.rel = 'noopener';
      a.textContent = item.title;
      card.appendChild(a);

      const actions = document.createElement('div');
      actions.className = 'actions';
      if (item.bitly) actions.appendChild(makeCopyBtn('bitly', item.bitly, 'https://' + item.bitly));
      if (item.url) actions.appendChild(makeCopyBtn('url', item.url.replace(/^https?:\/\//, ''), item.url));
      card.appendChild(actions);

      listEl.appendChild(card);
    });
  } catch (err) {
    listEl.innerHTML = '<p class="error">Links load karne mein dikkat hui. links.json check karein.</p>';
    console.error(err);
  }
}
loadLinks();
