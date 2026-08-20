(() => {
  const templateHomepage = 'https://saaskit.live/';
  const currentPath = window.location.pathname.replace(/\/+$/, '') || '/';
  if (currentPath === '/' || currentPath === '/welcome') {
    window.location.replace(templateHomepage);
    return;
  }

  const initNews = () => {
    const track = document.querySelector('[data-live-news-list]');
    const viewport = document.querySelector('.family-home__feed-viewport');
    if (!track || !viewport || track.dataset.initialized === 'true') return;
    track.dataset.initialized = 'true';
    const feed = 'https://raw.githubusercontent.com/saintus-create/family-905324/main/fern/data/live-legal-feed.json';
    const fallback = [
      { title: 'California Courts', source: 'Courts', url: 'https://courts.ca.gov/' },
      { title: 'California Legislative Information', source: 'Legislation', url: 'https://leginfo.legislature.ca.gov/' },
      { title: 'California Family Code', source: 'Family law', url: '/family-code-overview' },
      { title: 'Research Workbench', source: 'Research', url: '/research-workbench' }
    ];
    const escapeHtml = (value) => String(value || '').replace(/[&<>\"']/g, (c) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '\"':'&quot;', "'":'&#39;' }[c]));
    const render = (items) => {
      const stories = items.filter((x) => x && x.title && x.url).slice(0, 8);
      track.innerHTML = stories.map((x) => { const external = !String(x.url).startsWith('/'); return `<a class="family-home__news-item" href="${escapeHtml(x.url)}" ${external ? 'target="_blank" rel="noopener noreferrer"' : ''}><span class="family-home__news-body"><small class="family-home__news-source">${escapeHtml(x.source || 'Source')}</small><strong class="family-home__news-title">${escapeHtml(x.title)}</strong></span></a>`; }).join('');
      let index = 0;
      const move = (direction) => { const card = track.querySelector('.family-home__news-item'); if (!card) return; const step = card.getBoundingClientRect().width + 28; const visible = Math.max(1, Math.floor(viewport.clientWidth / Math.max(card.getBoundingClientRect().width, 1))); const max = Math.max(0, stories.length - visible); index = Math.max(0, Math.min(max, index + direction)); track.style.transform = `translateX(-${index * step}px)`; };
      viewport.closest('.family-home__feed')?.querySelector('[data-news-prev]')?.addEventListener('click', () => move(-1));
      viewport.closest('.family-home__feed')?.querySelector('[data-news-next]')?.addEventListener('click', () => move(1));
    };
    fetch(feed, { cache: 'no-store', headers: { Accept: 'application/json' } }).then((response) => response.ok ? response.json() : Promise.reject(new Error('feed failed'))).then((data) => render(data.items || [])).catch(() => render(fallback));
  };

  const initInteractions = () => {
    const root = document.querySelector('[data-family-landing]');
    const input = root?.querySelector('[data-home-search-input]');
    const menu = root?.querySelector('[data-home-menu]');
    const nav = root?.querySelector('.family-home__nav');
    if (!root) return;
    input?.addEventListener('keydown', (event) => { if (event.key === 'Escape') input.blur(); });
    window.addEventListener('keydown', (event) => { if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); input?.focus(); } });
    menu?.addEventListener('click', () => { const open = nav?.classList.toggle('is-open'); menu.setAttribute('aria-expanded', String(Boolean(open))); });
  };

  const initAmbient = () => {
    const root = document.querySelector('[data-family-landing]');
    const canvas = root?.querySelector('[data-research-canvas]');
    if (!root || !canvas || root.dataset.glInitialized === 'true') return;
    root.dataset.glInitialized = 'true';
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const mobile = window.matchMedia('(max-width: 760px)').matches;
    const gl = canvas.getContext('webgl', { alpha: true, antialias: true, powerPreference: 'low-power' });
    if (!gl) return;
    const vertexSource = `attribute vec2 p; attribute float s; attribute float a; varying float v; void main(){gl_Position=vec4(p,0.,1.);gl_PointSize=s;v=a;}`;
    const fragmentSource = `precision mediump float; varying float v; void main(){float d=length(gl_PointCoord-.5);float glow=smoothstep(.5,0.,d);gl_FragColor=vec4(.35,.48,.58,glow*v);}`;
    const compile = (type, source) => { const shader = gl.createShader(type); gl.shaderSource(shader, source); gl.compileShader(shader); return gl.getShaderParameter(shader, gl.COMPILE_STATUS) ? shader : null; };
    const program = gl.createProgram(); const vertex = compile(gl.VERTEX_SHADER, vertexSource); const fragment = compile(gl.FRAGMENT_SHADER, fragmentSource); if (!vertex || !fragment) return;
    gl.attachShader(program, vertex); gl.attachShader(program, fragment); gl.linkProgram(program); if (!gl.getProgramParameter(program, gl.LINK_STATUS)) return; gl.useProgram(program);
    const count = mobile ? 34 : 68;
    const nodes = Array.from({ length: count }, () => ({ x: Math.random() * 2 - 1, y: Math.random() * 2 - 1, phase: Math.random() * Math.PI * 2, speed: 0.00008 + Math.random() * 0.0001, alpha: 0.025 + Math.random() * 0.11, size: 0.8 + Math.random() * 2 }));
    const positionBuffer = gl.createBuffer(), sizeBuffer = gl.createBuffer(), alphaBuffer = gl.createBuffer();
    const positionLoc = gl.getAttribLocation(program, 'p'), sizeLoc = gl.getAttribLocation(program, 's'), alphaLoc = gl.getAttribLocation(program, 'a'); let mouseX = 0, mouseY = 0;
    root.addEventListener('pointermove', (event) => { const rect = root.getBoundingClientRect(); mouseX = (event.clientX - rect.left) / rect.width - 0.5; mouseY = (event.clientY - rect.top) / rect.height - 0.5; }, { passive: true });
    const resize = () => { const rect = canvas.getBoundingClientRect(); const ratio = Math.min(window.devicePixelRatio || 1, 1.5); canvas.width = Math.max(1, Math.floor(rect.width * ratio)); canvas.height = Math.max(1, Math.floor(rect.height * ratio)); gl.viewport(0, 0, canvas.width, canvas.height); };
    window.addEventListener('resize', resize, { passive: true });
    const draw = (time) => { resize(); const positions = new Float32Array(count * 2), sizes = new Float32Array(count), alphas = new Float32Array(count); nodes.forEach((node, i) => { positions[i * 2] = node.x + Math.sin(time * node.speed + node.phase) * 0.018 + mouseX * 0.025; positions[i * 2 + 1] = node.y + Math.cos(time * node.speed + node.phase) * 0.014 + mouseY * 0.018; sizes[i] = node.size * Math.min(window.devicePixelRatio || 1, 1.5); alphas[i] = node.alpha; }); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT); gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA); [[positionBuffer, positions, positionLoc, 2], [sizeBuffer, sizes, sizeLoc, 1], [alphaBuffer, alphas, alphaLoc, 1]].forEach(([buffer, data, location, width]) => { gl.bindBuffer(gl.ARRAY_BUFFER, buffer); gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW); gl.enableVertexAttribArray(location); gl.vertexAttribPointer(location, width, gl.FLOAT, false, 0, 0); }); gl.drawArrays(gl.POINTS, 0, count); if (!reduceMotion) requestAnimationFrame(draw); };
    requestAnimationFrame(draw);
  };

  const initBillCatalog = () => {
    const root = document.querySelector('[data-bill-catalog]');
    if (!root || root.dataset.initialized === 'true') return;
    root.dataset.initialized = 'true';
    const search = root.querySelector('[data-bill-search]');
    const chamber = root.querySelector('[data-bill-chamber]');
    const type = root.querySelector('[data-bill-type]');
    const author = root.querySelector('[data-bill-author]');
    const status = root.querySelector('[data-bill-status]');
    const familyOnly = root.querySelector('[data-bill-family-only]');
    const results = root.querySelector('[data-bill-results]');
    const count = root.querySelector('[data-bill-count]');
    const more = root.querySelector('[data-bill-more]');
    const clear = root.querySelector('[data-bill-clear]');
    const error = root.querySelector('[data-bill-error]');
    const updated = root.querySelector('[data-bill-updated]');
    const pageSize = 60;
    let records = [];
    let filtered = [];
    let visible = pageSize;
    const escapeHtml = (value) => String(value ?? '').replace(/[&<>\"']/g, (character) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '\"':'&quot;', "'":'&#39;' }[character]));
    const normalize = (value) => String(value || '').toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    const addOptions = (select, values) => { [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b)).forEach((value) => { const option = document.createElement('option'); option.value = value; option.textContent = value; select?.appendChild(option); }); };
    const render = () => {
      const query = normalize(search?.value.trim());
      const chamberValue = chamber?.value || '';
      const typeValue = type?.value || '';
      const authorValue = author?.value || '';
      const statusValue = status?.value || '';
      const familyValue = Boolean(familyOnly?.checked);
      filtered = records.filter((record) => { const searchable = normalize(`${record.measure} ${record.measure_display} ${record.subject} ${record.author} ${record.status}`); return (!query || searchable.includes(query)) && (!chamberValue || record.chamber === chamberValue) && (!typeValue || record.measure_type === typeValue) && (!authorValue || record.author === authorValue) && (!statusValue || record.status_group === statusValue) && (!familyValue || record.family_law_relevance); });
      const shown = filtered.slice(0, visible);
      if (count) count.textContent = `${filtered.length.toLocaleString()} measure${filtered.length === 1 ? '' : 's'}`;
      if (results) results.innerHTML = shown.map((record) => `<a class="bill-catalog__item" href="${escapeHtml(record.official_url)}" target="_blank" rel="noopener noreferrer"><div class="bill-catalog__item-top"><strong>${escapeHtml(record.measure)}</strong><span>${escapeHtml(record.measure_type)}</span>${record.family_law_relevance ? '<em>Family-law match</em>' : ''}</div><h2>${escapeHtml(record.subject || 'Subject not listed')}</h2><div class="bill-catalog__item-meta"><span>By ${escapeHtml(record.author)}</span><span>${escapeHtml(record.status)}</span></div><b aria-hidden="true">↗</b></a>`).join('');
      if (more) { more.hidden = visible >= filtered.length; more.textContent = `Show more (${Math.max(0, filtered.length - visible).toLocaleString()} remaining)`; }
    };
    const resetAndRender = () => { visible = pageSize; render(); };
    [search, chamber, type, author, status, familyOnly].forEach((control) => { control?.addEventListener(control === search ? 'input' : 'change', resetAndRender); });
    more?.addEventListener('click', () => { visible += pageSize; render(); });
    clear?.addEventListener('click', () => { if (search) search.value = ''; [chamber, type, author, status].forEach((select) => { if (select) select.value = ''; }); if (familyOnly) familyOnly.checked = false; resetAndRender(); search?.focus(); });
    fetch(root.dataset.source, { headers: { Accept: 'application/json' } }).then((response) => response.ok ? response.json() : Promise.reject(new Error(`HTTP ${response.status}`))).then((data) => { records = Array.isArray(data.records) ? data.records : []; addOptions(type, records.map((record) => record.measure_type)); addOptions(author, records.map((record) => record.author)); const setStat = (selector, value) => { const element = root.querySelector(selector); if (element) element.textContent = Number(value || 0).toLocaleString(); }; setStat('[data-bill-total]', data.counts?.total); setStat('[data-bill-assembly]', data.counts?.assembly); setStat('[data-bill-senate]', data.counts?.senate); setStat('[data-bill-family]', data.counts?.family_law_matches); if (updated && data.retrieved_at) updated.textContent = `Official index retrieved ${new Date(data.retrieved_at).toLocaleString()}`; render(); }).catch(() => { if (count) count.textContent = 'Bill catalog unavailable'; if (error) error.hidden = false; });
  };

  const initResearchAssistant = () => {
    const assistant = document.querySelector('[data-research-assistant]');
    if (!assistant || assistant.dataset.initialized === 'true') return;
    assistant.dataset.initialized = 'true';
    const form = assistant.querySelector('[data-assistant-form]');
    const input = assistant.querySelector('[data-assistant-input]');
    const messages = assistant.querySelector('[data-assistant-messages]');
    const minimize = assistant.querySelector('[data-assistant-minimize]');
    const theme = assistant.querySelector('[data-assistant-theme]');
    minimize?.addEventListener('click', () => assistant.classList.toggle('is-minimized'));
    theme?.addEventListener('click', () => assistant.classList.toggle('is-dark'));
    form?.addEventListener('submit', (event) => { event.preventDefault(); const value = input?.value.trim(); if (!value) return; const user = document.createElement('div'); user.className = 'research-assistant__message research-assistant__message--user'; user.textContent = value; messages?.appendChild(user); input.value = ''; const reply = document.createElement('div'); reply.className = 'research-assistant__message research-assistant__message--assistant'; reply.textContent = 'Research assistant ready. Connect this dialogue to the research/AI endpoint to answer this question with Fern context.'; messages?.appendChild(reply); messages?.parentElement?.scrollTo({ top: messages.parentElement.scrollHeight, behavior: 'smooth' }); });
  };

  const start = () => { initNews(); initInteractions(); initAmbient(); initBillCatalog(); initResearchAssistant(); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true }); else start();
  let refreshQueued = false;
  new MutationObserver(() => { if (refreshQueued) return; refreshQueued = true; requestAnimationFrame(() => { refreshQueued = false; initBillCatalog(); initResearchAssistant(); }); }).observe(document.documentElement, { childList: true, subtree: true });
})();
