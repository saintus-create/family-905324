(() => {
  const start = () => {
    const root = document.querySelector('[data-family-landing]');
    if (!root || root.dataset.initialized === 'true') return;
    root.dataset.initialized = 'true';

    const canvas = root.querySelector('[data-research-canvas]');
    if (!canvas) return;

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const isSmall = window.matchMedia('(max-width: 760px)').matches;
    const gl = canvas.getContext('webgl', { alpha: true, antialias: true });
    if (!gl) return;

    const vertex = `
      attribute vec2 a_position;
      attribute float a_size;
      attribute float a_alpha;
      varying float v_alpha;
      void main() {
        gl_Position = vec4(a_position, 0.0, 1.0);
        gl_PointSize = a_size;
        v_alpha = a_alpha;
      }
    `;
    const fragment = `
      precision mediump float;
      varying float v_alpha;
      void main() {
        vec2 p = gl_PointCoord - vec2(0.5);
        float d = length(p);
        float glow = smoothstep(0.5, 0.0, d);
        gl_FragColor = vec4(0.56, 0.71, 0.82, glow * v_alpha);
      }
    `;

    const compile = (type, source) => {
      const shader = gl.createShader(type);
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      return gl.getShaderParameter(shader, gl.COMPILE_STATUS) ? shader : null;
    };

    const program = gl.createProgram();
    const vs = compile(gl.VERTEX_SHADER, vertex);
    const fs = compile(gl.FRAGMENT_SHADER, fragment);
    if (!vs || !fs) return;
    gl.attachShader(program, vs);
    gl.attachShader(program, fs);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) return;
    gl.useProgram(program);

    const position = gl.createBuffer();
    const size = gl.createBuffer();
    const alpha = gl.createBuffer();
    const positionLoc = gl.getAttribLocation(program, 'a_position');
    const sizeLoc = gl.getAttribLocation(program, 'a_size');
    const alphaLoc = gl.getAttribLocation(program, 'a_alpha');

    const count = isSmall ? 70 : 150;
    const nodes = Array.from({ length: count }, (_, i) => ({
      x: Math.random() * 2 - 1,
      y: Math.random() * 2 - 1,
      r: 0.0008 + Math.random() * 0.002,
      phase: Math.random() * Math.PI * 2,
      speed: 0.00015 + Math.random() * 0.00035,
      size: 1.2 + Math.random() * 3.5,
      alpha: 0.12 + Math.random() * 0.55,
      band: i % 6
    }));

    const resize = () => {
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      const rect = canvas.getBoundingClientRect();
      canvas.width = Math.max(1, Math.floor(rect.width * ratio));
      canvas.height = Math.max(1, Math.floor(rect.height * ratio));
      gl.viewport(0, 0, canvas.width, canvas.height);
    };

    const draw = (time) => {
      const t = reduceMotion ? 0 : time;
      resize();
      const positions = new Float32Array(count * 2);
      const sizes = new Float32Array(count);
      const alphas = new Float32Array(count);
      const mx = (window.__familyMouseX || 0) * 0.08;
      const my = (window.__familyMouseY || 0) * 0.05;

      nodes.forEach((n, i) => {
        const wobble = Math.sin(t * n.speed + n.phase) * 0.035;
        const drift = Math.cos(t * n.speed * 0.7 + n.phase) * 0.025;
        positions[i * 2] = n.x + wobble + mx * (0.4 + n.band / 10);
        positions[i * 2 + 1] = n.y + drift + my * (0.3 + n.band / 12);
        sizes[i] = n.size * Math.min(window.devicePixelRatio || 1, 2);
        alphas[i] = n.alpha;
      });

      gl.clearColor(0, 0, 0, 0);
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.enable(gl.BLEND);
      gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

      gl.bindBuffer(gl.ARRAY_BUFFER, position);
      gl.bufferData(gl.ARRAY_BUFFER, positions, gl.DYNAMIC_DRAW);
      gl.enableVertexAttribArray(positionLoc);
      gl.vertexAttribPointer(positionLoc, 2, gl.FLOAT, false, 0, 0);

      gl.bindBuffer(gl.ARRAY_BUFFER, size);
      gl.bufferData(gl.ARRAY_BUFFER, sizes, gl.DYNAMIC_DRAW);
      gl.enableVertexAttribArray(sizeLoc);
      gl.vertexAttribPointer(sizeLoc, 1, gl.FLOAT, false, 0, 0);

      gl.bindBuffer(gl.ARRAY_BUFFER, alpha);
      gl.bufferData(gl.ARRAY_BUFFER, alphas, gl.DYNAMIC_DRAW);
      gl.enableVertexAttribArray(alphaLoc);
      gl.vertexAttribPointer(alphaLoc, 1, gl.FLOAT, false, 0, 0);

      gl.drawArrays(gl.POINTS, 0, count);
      if (!reduceMotion) requestAnimationFrame(draw);
    };

    window.addEventListener('resize', resize, { passive: true });
    root.addEventListener('pointermove', (event) => {
      const rect = root.getBoundingClientRect();
      window.__familyMouseX = (event.clientX - rect.left) / rect.width - 0.5;
      window.__familyMouseY = (event.clientY - rect.top) / rect.height - 0.5;
    }, { passive: true });

    requestAnimationFrame(draw);
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
})();
