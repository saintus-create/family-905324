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
      { title: 'California Family Code', source: 'Family Law', url: '/family-code-overview' },
      { title: 'Research Workbench', source: 'Research', url: '/research-workbench' }
    ];
    const esc = (v) => String(v || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const render = (items) => {
      const stories = items.filter(x => x && x.title && x.url).slice(0, 8);
      track.innerHTML = stories.map(x => `<a class="family-home__news-item" href="${esc(x.url)}" target="${String(x.url).startsWith('/') ? '_self' : '_blank'}" rel="noopener noreferrer"><small>${esc(x.source || 'Source')}</small><strong>${esc(x.title)}</strong><span>→</span></a>`).join('');
      if (status) status.textContent = 'Live';
      let index = 0;
      const move = (d) => { const card = track.querySelector('.family-home__news-item'); if (!card) return; const step = card.getBoundingClientRect().width + 12; const max = Math.max(0, stories.length - Math.max(1, Math.floor(viewport.clientWidth / 280))); index = Math.max(0, Math.min(max, index + d)); track.style.transform = `translateX(-${index * step}px)`; };
      viewport.querySelector('[data-news-prev]')?.addEventListener('click', () => move(-1));
      viewport.querySelector('[data-news-next]')?.addEventListener('click', () => move(1));
    };
    fetch(feed, { cache: 'no-store' }).then(r => r.ok ? r.json() : Promise.reject()).then(d => render(d.items || [])).catch(() => render(fallback));
  };

  const initAmbient = () => {
    const root = document.querySelector('[data-family-landing]');
    const canvas = root?.querySelector('[data-research-canvas]');
    if (!root || !canvas || root.dataset.glInitialized === 'true') return;
    root.dataset.glInitialized = 'true';
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const mobile = window.matchMedia('(max-width: 760px)').matches;
    const gl = canvas.getContext('webgl', { alpha: true, antialias: true });
    if (!gl) return;
    const vs = `attribute vec2 p; attribute float s; attribute float a; varying float v; void main(){gl_Position=vec4(p,0.,1.);gl_PointSize=s;v=a;}`;
    const fs = `precision mediump float; varying float v; void main(){float d=length(gl_PointCoord-.5);float g=smoothstep(.5,0.,d);gl_FragColor=vec4(.35,.48,.58,g*v);}`;
    const shader = (type, source) => { const x=gl.createShader(type); gl.shaderSource(x,source); gl.compileShader(x); return gl.getShaderParameter(x,gl.COMPILE_STATUS)?x:null; };
    const p=gl.createProgram(), v=shader(gl.VERTEX_SHADER,vs), f=shader(gl.FRAGMENT_SHADER,fs); if(!v||!f)return; gl.attachShader(p,v);gl.attachShader(p,f);gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))return;gl.useProgram(p);
    const count=mobile?38:78, nodes=Array.from({length:count},()=>({x:Math.random()*2-1,y:Math.random()*2-1,ph:Math.random()*6.28,sp:.00008+Math.random()*.00012,sz:.8+Math.random()*2.2,al:.025+Math.random()*.12}));
    const bp=gl.createBuffer(), bs=gl.createBuffer(), ba=gl.createBuffer(), lp=gl.getAttribLocation(p,'p'), ls=gl.getAttribLocation(p,'s'), la=gl.getAttribLocation(p,'a');
    const resize=()=>{const r=Math.min(devicePixelRatio||1,1.5),b=canvas.getBoundingClientRect();canvas.width=Math.max(1,b.width*r);canvas.height=Math.max(1,b.height*r);gl.viewport(0,0,canvas.width,canvas.height);};
    let mx=0,my=0; root.addEventListener('pointermove',e=>{const r=root.getBoundingClientRect();mx=(e.clientX-r.left)/r.width-.5;my=(e.clientY-r.top)/r.height-.5},{passive:true});
    const draw=t=>{resize();const pos=new Float32Array(count*2),sizes=new Float32Array(count),alphas=new Float32Array(count);nodes.forEach((n,i)=>{pos[i*2]=n.x+Math.sin(t*n.sp+n.ph)*.018+mx*.025;pos[i*2+1]=n.y+Math.cos(t*n.sp+n.ph)*.014+my*.018;sizes[i]=n.sz*(devicePixelRatio||1);alphas[i]=n.al;});gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.bindBuffer(gl.ARRAY_BUFFER,bp);gl.bufferData(gl.ARRAY_BUFFER,pos,gl.DYNAMIC_DRAW);gl.enableVertexAttribArray(lp);gl.vertexAttribPointer(lp,2,gl.FLOAT,false,0,0);gl.bindBuffer(gl.ARRAY_BUFFER,bs);gl.bufferData(gl.ARRAY_BUFFER,sizes,gl.DYNAMIC_DRAW);gl.enableVertexAttribArray(ls);gl.vertexAttribPointer(ls,1,gl.FLOAT,false,0,0);gl.bindBuffer(gl.ARRAY_BUFFER,ba);gl.bufferData(gl.ARRAY_BUFFER,alphas,gl.DYNAMIC_DRAW);gl.enableVertexAttribArray(la);gl.vertexAttribPointer(la,1,gl.FLOAT,false,0,0);gl.drawArrays(gl.POINTS,0,count);if(!reduce)requestAnimationFrame(draw);};
    requestAnimationFrame(draw);
  };
  const start=()=>{initNews();initAmbient();};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
