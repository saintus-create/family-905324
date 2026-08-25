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
      if (results) results.innerHTML = shown.map((record) => `<li class="usa-card tablet:grid-col-6"><a class="usa-card__container bill-catalog__item" href="${escapeHtml(record.official_url)}" target="_blank" rel="noopener noreferrer"><div class="usa-card__header"><h2 class="usa-card__heading">${escapeHtml(record.measure)} — ${escapeHtml(record.subject || 'Subject not listed')}</h2></div><div class="usa-card__body"><p>${escapeHtml(record.author)} · ${escapeHtml(record.status)}</p></div><div class="usa-card__footer"><span class="usa-tag">${escapeHtml(record.measure_type)}</span>${record.family_law_relevance ? '<span class="usa-tag">Family law</span>' : ''}</div></a></li>`).join('');
      if (more) { more.hidden = visible >= filtered.length; more.textContent = `Show more (${Math.max(0, filtered.length - visible).toLocaleString()} remaining)`; }
    };
    const resetAndRender = () => { visible = pageSize; render(); };
    [search, chamber, type, author, status, familyOnly].forEach((control) => { control?.addEventListener(control === search ? 'input' : 'change', resetAndRender); });
    more?.addEventListener('click', () => { visible += pageSize; render(); });
    clear?.addEventListener('click', () => { if (search) search.value = ''; [chamber, type, author, status].forEach((select) => { if (select) select.value = ''; }); if (familyOnly) familyOnly.checked = false; resetAndRender(); search?.focus(); });
    fetch(root.dataset.source, { headers: { Accept: 'application/json' } }).then((response) => response.ok ? response.json() : Promise.reject(new Error(`HTTP ${response.status}`))).then((data) => { records = Array.isArray(data.records) ? data.records : []; addOptions(type, records.map((record) => record.measure_type)); addOptions(author, records.map((record) => record.author)); const setStat = (selector, value) => { const element = root.querySelector(selector); if (element) element.textContent = Number(value || 0).toLocaleString(); }; setStat('[data-bill-total]', data.counts?.total); setStat('[data-bill-assembly]', data.counts?.assembly); setStat('[data-bill-senate]', data.counts?.senate); setStat('[data-bill-family]', data.counts?.family_law_matches); if (updated && data.retrieved_at) updated.textContent = `Official index retrieved ${new Date(data.retrieved_at).toLocaleString()}`; render(); }).catch(() => { if (count) count.textContent = 'Bill catalog unavailable'; if (error) error.hidden = false; });
  };

  const breadcrumbItems = () => {
    const path = window.location.pathname.replace(/\/$/, '') || '/';
    const library = { label: 'Library', href: '/' };
    if (path === '/') return [library];
    if (path === '/case-law') return [library, { label: 'Case Law' }];
    if (path === '/family-code-overview' || path.startsWith('/division-')) return [library, { label: 'Family Code', href: '/family-code-overview' }, { label: path === '/family-code-overview' ? 'Overview' : path.slice(1).replaceAll('-', ' ') }];
    if (path === '/court-rules-overview' || path.startsWith('/title-')) return [library, { label: 'Court Rules', href: '/court-rules-overview' }, { label: path === '/court-rules-overview' ? 'Overview' : path.slice(1).replaceAll('-', ' ') }];
    if (path === '/bills-and-measures') return [library, { label: 'Legislation' }, { label: 'Bills and Measures' }];
    if (path.startsWith('/invitations-to-comment')) return [library, { label: 'Legislation', href: '/bills-and-measures' }, { label: 'Invitations to Comment', href: '/invitations-to-comment' }, ...(path.split('/').filter(Boolean).length > 1 ? [{ label: path.split('/').pop().toUpperCase() }] : [])];
    if (path.startsWith('/library/public-records')) return [library, { label: 'Public Records', href: '/library/public-records/public-records' }, { label: path.split('/').pop().replaceAll('-', ' ') }];
    return [library, { label: document.querySelector('.fern-page-heading h1')?.textContent?.trim() || path.slice(1).replaceAll('-', ' ') }];
  };

  const initBreadcrumbs = () => {
    const heading = document.querySelector('.fern-page-heading');
    if (!heading || heading.querySelector('.site-breadcrumbs')) return;
    const nav = document.createElement('nav');
    nav.className = 'site-breadcrumbs';
    nav.setAttribute('aria-label', 'Breadcrumb');
    nav.innerHTML = breadcrumbItems().map((item, index, items) => item.href && index < items.length - 1 ? `<a href="${item.href}">${item.label}</a>` : `<span${index === items.length - 1 ? ' aria-current="page"' : ''}>${item.label}</span>`).join('<b aria-hidden="true">/</b>');
    heading.prepend(nav);
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

  const start = () => { initSiteBanner(); initBreadcrumbs(); initBillCatalog(); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true }); else start();
  let refreshQueued = false;
  new MutationObserver(() => { if (refreshQueued) return; refreshQueued = true; requestAnimationFrame(() => { refreshQueued = false; initSiteBanner(); initBreadcrumbs(); initBillCatalog(); }); }).observe(document.documentElement, { childList: true, subtree: true });
})();
