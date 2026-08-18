(() => {
  const initNews = () => {
    const track = document.querySelector('[data-live-news-list]');
    const status = document.querySelector('[data-live-news-status]');
    const viewport = document.querySelector('.family-landing__news-viewport');
    const prev = document.querySelector('[data-news-prev]');
    const next = document.querySelector('[data-news-next]');
    if (!track || track.dataset.initialized === 'true') return;
    track.dataset.initialized = 'true';

    // The GitHub Actions feed is refreshed independently every 15 minutes.
    // Reading the generated JSON avoids browser-side news scraping and gives
    // the homepage a deterministic fallback when an external feed is slow.
    const feedUrl = 'https://raw.githubusercontent.com/saintus-create/family-905324/main/fern/data/live-legal-feed.json';
    const fallback = [
      { title: 'Leadership Perspectives: Judge Steven Jahr on 100 Years of the Judicial Council', source: 'California Courts', url: 'https://newsroom.courts.ca.gov/news/leadership-perspectives-judge-steven-jahr-100-years-judicial-council', image: 'https://newsroom.courts.ca.gov/sites/default/files/newsroom/styles/max_650x650/public/2026-08/Judge_Steven_Jahr_Judicial_Council_100th_anniverary_banner.png' },
      { title: 'Judicial Ethics Committee Issues Formal Opinion on Appointing Attorney Spouse of Judicial Colleague as Minor’s Counsel', source: 'California Courts', url: 'https://newsroom.courts.ca.gov/news/judicial-ethics-committee-issues-formal-opinion-appointing-attorney-spouse-judicial-colleague', image: 'https://newsroom.courts.ca.gov/sites/default/files/newsroom/styles/max_650x650/public/2026-06/CJEO%20Logo%202026%20Greyscale.png' },
      { title: 'Commission Confirms Four Appointments to Courts of Appeal', source: 'California Courts', url: 'https://newsroom.courts.ca.gov/news/commission-confirms-four-appointments-courts-appeal', image: 'https://newsroom.courts.ca.gov/sites/default/files/newsroom/styles/max_650x650/public/2026-08/CODY.JPG' },
      { title: 'Assembly Floor Session', source: 'California Legislature', url: 'https://leginfo.legislature.ca.gov/faces/billResultsClient.xhtml?location=AFLOOR&agendadate=08%2F18%2F2026&description=Assembly+Floor+Session', image: 'https://leginfo.legislature.ca.gov/resources/images/header_img.png' }
    ];

    const escapeHtml = (value) => String(value || '').replace(/[&<>"']/g, (c) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));
    const render = (articles) => {
      const stories = articles.filter((article) => article && article.title && article.url).slice(0, 8);
      if (!stories.length) throw new Error('No stories');
      track.innerHTML = stories.map((article) => {
        const title = escapeHtml(article.title);
        const url = escapeHtml(article.url);
        const domain = escapeHtml(article.source || article.domain || 'Source');
        const image = escapeHtml(article.image || article.socialimage || article.socialImage || '');
        return `<a class="family-landing__news-item" href="${url}" target="_blank" rel="noopener noreferrer">${image ? `<img class="family-landing__news-image" src="${image}" alt="" loading="lazy" referrerpolicy="no-referrer">` : '<span class="family-landing__news-image--empty" aria-hidden="true"></span>'}<span class="family-landing__news-body"><small class="family-landing__news-source">${domain}</small><strong class="family-landing__news-title">${title}</strong></span></a>`;
      }).join('');
      if (status) status.textContent = 'Live';
      let index = 0;
      const step = () => Math.min(3, Math.max(1, Math.floor(viewport.clientWidth / 245)));
      const move = (direction) => {
        const max = Math.max(0, stories.length - step());
        index = Math.max(0, Math.min(max, index + direction));
        const first = track.querySelector('.family-landing__news-item');
        if (first) track.style.transform = `translateX(-${index * (first.getBoundingClientRect().width + 10)}px)`;
      };
      prev?.addEventListener('click', () => move(-1));
      next?.addEventListener('click', () => move(1));
      let timer = null;
      const start = () => {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || stories.length <= step()) return;
        timer = window.setInterval(() => { const max = Math.max(0, stories.length - step()); if (index >= max) index = -1; move(1); }, 5000);
      };
      const stop = () => { if (timer) window.clearInterval(timer); timer = null; };
      viewport?.addEventListener('mouseenter', stop); viewport?.addEventListener('mouseleave', start); viewport?.addEventListener('focusin', stop); viewport?.addEventListener('focusout', start); start();
    };

    fetch(feedUrl, { cache: 'no-store', headers: { Accept: 'application/json' } })
      .then((response) => { if (!response.ok) throw new Error('Feed request failed'); return response.json(); })
      .then((data) => render(data.items || []))
      .catch(() => render(fallback));
  };

  const start = () => {
    initNews();
    const root = document.querySelector('[data-family-landing]');
    if (!root || root.dataset.initialized === 'true') return;
    root.dataset.initialized = 'true';
    const canvas = root.querySelector('[data-research-canvas]');
    if (!canvas) return;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const isSmall = window.matchMedia('(max-width: 760px)').matches;
    const gl = canvas.getContext('webgl', { alpha: true, antialias: true });
    if (!gl) return;
    const vertex = `attribute vec2 a_position; attribute float a_size; attribute float a_alpha; varying float v_alpha; void main(){gl_Position=vec4(a_position,0.0,1.0);gl_PointSize=a_size;v_alpha=a_alpha;}`;
    const fragment = `precision mediump float; varying float v_alpha; void main(){vec2 p=gl_PointCoord-vec2(0.5);float d=length(p);float glow=smoothstep(0.5,0.0,d);gl_FragColor=vec4(0.56,0.71,0.82,glow*v_alpha);}`;
    const compile = (type, source) => { const shader=gl.createShader(type); gl.shaderSource(shader,source); gl.compileShader(shader); return gl.getShaderParameter(shader,gl.COMPILE_STATUS)?shader:null; };
    const program=gl.createProgram(); const vs=compile(gl.VERTEX_SHADER,vertex); const fs=compile(gl.FRAGMENT_SHADER,fragment); if(!vs||!fs)return; gl.attachShader(program,vs); gl.attachShader(program,fs); gl.linkProgram(program); if(!gl.getProgramParameter(program,gl.LINK_STATUS))return; gl.useProgram(program);
    const position=gl.createBuffer(), size=gl.createBuffer(), alpha=gl.createBuffer(); const positionLoc=gl.getAttribLocation(program,'a_position'), sizeLoc=gl.getAttribLocation(program,'a_size'), alphaLoc=gl.getAttribLocation(program,'a_alpha');
    const count=isSmall?58:118; const nodes=Array.from({length:count},(_,i)=>({x:Math.random()*2-1,y:Math.random()*2-1,phase:Math.random()*Math.PI*2,speed:0.00012+Math.random()*0.00022,size:1.1+Math.random()*2.8,alpha:0.07+Math.random()*0.34,band:i%6}));
    const sparks=Array.from({length:isSmall?3:6},(_,i)=>({lane:i%4,phase:Math.random()*Math.PI*2,speed:0.000035+Math.random()*0.000025,length:0.15+Math.random()*0.18}));
    const resize=()=>{const ratio=Math.min(window.devicePixelRatio||1,2);const rect=canvas.getBoundingClientRect();canvas.width=Math.max(1,Math.floor(rect.width*ratio));canvas.height=Math.max(1,Math.floor(rect.height*ratio));gl.viewport(0,0,canvas.width,canvas.height);};
    const draw=(time)=>{const t=reduceMotion?0:time;resize();const positions=new Float32Array((count+sparks.length)*2),sizes=new Float32Array(count+sparks.length),alphas=new Float32Array(count+sparks.length);const mx=(window.__familyMouseX||0)*0.055,my=(window.__familyMouseY||0)*0.04;nodes.forEach((n,i)=>{const wobble=Math.sin(t*n.speed+n.phase)*0.028,drift=Math.cos(t*n.speed*0.72+n.phase)*0.021;positions[i*2]=n.x+wobble+mx*(0.35+n.band/12);positions[i*2+1]=n.y+drift+my*(0.25+n.band/14);sizes[i]=n.size*Math.min(window.devicePixelRatio||1,2);alphas[i]=n.alpha;});sparks.forEach((s,j)=>{const i=count+j,progress=(Math.sin(t*s.speed+s.phase)+1)/2,lane=s.lane-1.5;positions[i*2]=-0.95+progress*1.9;positions[i*2+1]=lane*0.22+Math.sin(progress*Math.PI*2+s.phase)*0.035;sizes[i]=(1.8+Math.sin(progress*Math.PI)*2.2)*Math.min(window.devicePixelRatio||1,2);alphas[i]=Math.pow(Math.sin(progress*Math.PI),7)*0.52;});gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.bindBuffer(gl.ARRAY_BUFFER,position);gl.bufferData(gl.ARRAY_BUFFER,positions,gl.DYNAMIC_DRAW);gl.enableVertexAttribArray(positionLoc);gl.vertexAttribPointer(positionLoc,2,gl.FLOAT,false,0,0);gl.bindBuffer(gl.ARRAY_BUFFER,size);gl.bufferData(gl.ARRAY_BUFFER,sizes,gl.DYNAMIC_DRAW);gl.enableVertexAttribArray(sizeLoc);gl.vertexAttribPointer(sizeLoc,1,gl.FLOAT,false,0,0);gl.bindBuffer(gl.ARRAY_BUFFER,alpha);gl.bufferData(gl.ARRAY_BUFFER,alphas,gl.DYNAMIC_DRAW);gl.enableVertexAttribArray(alphaLoc);gl.vertexAttribPointer(alphaLoc,1,gl.FLOAT,false,0,0);gl.drawArrays(gl.POINTS,0,count+sparks.length);if(!reduceMotion)requestAnimationFrame(draw);};
    window.addEventListener('resize',resize,{passive:true}); root.addEventListener('pointermove',(event)=>{const rect=root.getBoundingClientRect();window.__familyMouseX=(event.clientX-rect.left)/rect.width-0.5;window.__familyMouseY=(event.clientY-rect.top)/rect.height-0.5;},{passive:true}); requestAnimationFrame(draw);
  };
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
