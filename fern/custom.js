(function() {
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
    const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[character]));
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

  const initSiteBanner = () => {
    if (document.getElementById('site-status-banner')) return;
    const header = document.querySelector('header');
    if (!header) return;
    const banner = document.createElement('section');
    banner.id = 'site-status-banner';
    banner.className = 'usa-banner research-site-banner';
    banner.setAttribute('aria-label', 'Site status');
    banner.innerHTML = '<div class="usa-banner__inner"><div class="usa-banner__header-text"><p><strong>Independent public-interest research site.</strong> Not an official website of the United States government.</p></div></div>';
    header.parentNode?.insertBefore(banner, header);
  };

  const start = () => { initSiteBanner(); initBillCatalog(); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true }); else start();
  let refreshQueued = false;
  new MutationObserver(() => { if (refreshQueued) return; refreshQueued = true; requestAnimationFrame(() => { refreshQueued = false; initSiteBanner(); initBillCatalog(); }); }).observe(document.documentElement, { childList: true, subtree: true });
})();
