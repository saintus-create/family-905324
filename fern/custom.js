(() => {
  const initNews = () => {
    const track = document.querySelector('[data-live-news-list]');
    const viewport = document.querySelector('.family-home__news-viewport');
    const status = document.querySelector('[data-live-news-status]');
    if (!track || !viewport || track.dataset.initialized === 'true') return;
    track.dataset.initialized = 'true';

    const feed = 'https://raw.githubusercontent.com/saintus-create/family-905324/main/fern/data/live-legal-feed.json';
    const fallback = [
      { title: 'California Courts', source: 'Courts', url: 'https://courts.ca.gov/' },
      { title: 'California Legislative Information', source: 'Legislation', url: 'https://leginfo.legislature.ca.gov/' },
      { title: 'California Family Code', source: 'Family law', url: '/family-code-overview' },
      { title: 'Research Workbench', source: 'Research', url: '/research-workbench' }
    ];

    const escapeHtml = (value) => String(value || '').replace(/[&<>"']/g, (c) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));
    const render = (items) => {
      const stories = items.filter((x) => x && x.title && x.url).slice(0, 8);
      track.innerHTML = stories.map((x) => {
        const external = !String(x.url).startsWith('/');
        return `<a class="family-home__news-item" href="${escapeHtml(x.url)}" ${external ? 'target="_blank" rel="noopener noreferrer"' : ''}><span class="family-home__news-body"><small class="family-home__news-source">${escapeHtml(x.source || 'Source')}</small><strong class="family-home__news-title">${escapeHtml(x.title)}</strong></span></a>`;
      }).join('');
      if (status) status.textContent = 'Live';

      let index = 0;
      const move = (direction) => {
        const card = track.querySelector('.family-home__news-item');
        if (!card) return;
        const step = card.getBoundingClientRect().width + 10;
        const visible = Math.max(1, Math.floor(viewport.clientWidth / 260));
        const max = Math.max(0, stories.length - visible);
        index = Math.max(0, Math.min(max, index + direction));
        track.style.transform = `translateX(-${index * step}px)`;
      };
      viewport.querySelector('[data-news-prev]')?.addEventListener('click', () => move(-1));
      viewport.querySelector('[data-news-next]')?.addEventListener('click', () => move(1));
    };

    fetch(feed, { cache: 'no-store', headers: { Accept: 'application/json' } })
      .then((response) => response.ok ? response.json() : Promise.reject(new Error('feed failed')))
      .then((data) => render(data.items || []))
      .catch(() => render(fallback));
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
    const program = gl.createProgram();
    const vertex = compile(gl.VERTEX_SHADER, vertexSource);
    const fragment = compile(gl.FRAGMENT_SHADER, fragmentSource);
    if (!vertex || !fragment) return;
    gl.attachShader(program, vertex); gl.attachShader(program, fragment); gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) return;
    gl.useProgram(program);

    const count = mobile ? 34 : 68;
    const nodes = Array.from({ length: count }, () => ({
      x: Math.random() * 2 - 1, y: Math.random() * 2 - 1,
      phase: Math.random() * Math.PI * 2, speed: 0.00008 + Math.random() * 0.0001,
      alpha: 0.025 + Math.random() * 0.11, size: 0.8 + Math.random() * 2
    }));
    const positionBuffer = gl.createBuffer(), sizeBuffer = gl.createBuffer(), alphaBuffer = gl.createBuffer();
    const positionLoc = gl.getAttribLocation(program, 'p'), sizeLoc = gl.getAttribLocation(program, 's'), alphaLoc = gl.getAttribLocation(program, 'a');
    let mouseX = 0, mouseY = 0;

    root.addEventListener('pointermove', (event) => {
      const rect = root.getBoundingClientRect();
      mouseX = (event.clientX - rect.left) / rect.width - 0.5;
      mouseY = (event.clientY - rect.top) / rect.height - 0.5;
    }, { passive: true });

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      const ratio = Math.min(window.devicePixelRatio || 1, 1.5);
      canvas.width = Math.max(1, Math.floor(rect.width * ratio));
      canvas.height = Math.max(1, Math.floor(rect.height * ratio));
      gl.viewport(0, 0, canvas.width, canvas.height);
    };
    window.addEventListener('resize', resize, { passive: true });

    const draw = (time) => {
      resize();
      const positions = new Float32Array(count * 2), sizes = new Float32Array(count), alphas = new Float32Array(count);
      nodes.forEach((node, i) => {
        positions[i * 2] = node.x + Math.sin(time * node.speed + node.phase) * 0.018 + mouseX * 0.025;
        positions[i * 2 + 1] = node.y + Math.cos(time * node.speed + node.phase) * 0.014 + mouseY * 0.018;
        sizes[i] = node.size * Math.min(window.devicePixelRatio || 1, 1.5);
        alphas[i] = node.alpha;
      });
      gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT); gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
      [[positionBuffer, positions, positionLoc, 2], [sizeBuffer, sizes, sizeLoc, 1], [alphaBuffer, alphas, alphaLoc, 1]].forEach(([buffer, data, location, width]) => {
        gl.bindBuffer(gl.ARRAY_BUFFER, buffer); gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW); gl.enableVertexAttribArray(location); gl.vertexAttribPointer(location, width, gl.FLOAT, false, 0, 0);
      });
      gl.drawArrays(gl.POINTS, 0, count);
      if (!reduceMotion) requestAnimationFrame(draw);
    };

    requestAnimationFrame(draw);
  };

  const start = () => { initNews(); initAmbient(); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true }); else start();
})();
