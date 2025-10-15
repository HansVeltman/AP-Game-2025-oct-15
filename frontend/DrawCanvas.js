
/**
 * DrawCanvas.js
 * Renderer voor TheMainArea: tekent images, rechthoeken, driehoeken en pijlen
 * Gebruik in app.js:
 *   const renderer = DrawCanvas.createRenderer(document.querySelector('#TheMainArea'));
 *   // later, bij binnenkomend WS-bericht:
 *   await renderer.render(messageFromBackend);
 */
(function (global) {
  'use strict';

  function createRenderer(canvas) {
    if (!canvas) throw new Error('DrawCanvas: canvas element is required');
    const ctx = canvas.getContext('2d');

    // Client-side cache op bestandsnaam → ImageBitmap
    const imageCache = new Map();

    function loadFromPayload(filename, b64) {
      if (imageCache.has(filename)) return imageCache.get(filename);
      const p = new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = reject;
        img.src = "data:image/png;base64," + b64;
      });
      imageCache.set(filename, p);
      return p;
    }

    // ---- Helpers ----------------------------------------------------------
    function applyLineType(ctx, linetype) {
      if (linetype === 'DASHED') ctx.setLineDash([8, 6]);
      else if (linetype === 'DOTTED') ctx.setLineDash([2, 4]);
      else ctx.setLineDash([]);
    }

    async function ensureImageBitmap(filename, b64) {
      if (imageCache.has(filename)) return imageCache.get(filename);
      if (!b64) return null;
      const resp = await fetch(`data:image/png;base64,${b64}`);
      const blob = await resp.blob();
      const bmp = await createImageBitmap(blob);
      imageCache.set(filename, bmp);
      return bmp;
    }

    function clear() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    // ---- Rendering --------------------------------------------------------
    async function render(msg) {
      // msg: { images, rectangles, triangles, arrows, png_payloads, ... }
      clear();

      // 0) Images cachen
      const pngs = msg.png_payloads || {};
      const images = msg.images || [];
      
      if (msg.png_payloads) { // Cache bijwerken met evt. nieuwe payloads
        for (const [fn, b64] of Object.entries(msg.png_payloads)) {
          // alleen nieuw cachen; overschrijven kan ook als je versiebeheer wilt
          if (!imageCache.has(fn)) loadFromPayload(fn, b64);
        }
      }

      // 1) Canvas leegmaken
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 2) Rechthoeken
      for (const r of msg.rectangles || []) {
        ctx.save();
        applyLineType = (ctx, r.linetype);
        ctx.lineWidth = r.linewidth || 1;
        ctx.strokeStyle = r.stroke || '#000';
        ctx.fillStyle = r.fill || 'rgba(0,0,0,0)';
        ctx.beginPath();
        ctx.rect(r.x, r.y, r.w, r.h);
        ctx.fill();
        ctx.stroke();
        if (r.text) {
          ctx.font = `${r.fontsize || 14}px ${r.font || 'Arial'}`;
          ctx.fillStyle = r.textcolor || '#000';
          ctx.fillText(r.text, r.x + 8, r.y + (r.fontsize || 14) + 4);
        }
        ctx.restore();
      }

      // 3) Driehoeken (top, rechts-onder, links-onder)
      for (const t of msg.triangles || []) {
        ctx.save();
        applyLineType = (ctx, t.linetype);
        ctx.lineWidth = t.linewidth || 1;
        ctx.strokeStyle = t.stroke || '#000';
        ctx.fillStyle = t.fill || 'rgba(0,0,0,0)';
        ctx.beginPath();
        ctx.moveTo(t.x, t.y);
        ctx.lineTo(t.x + t.w, t.y);
        ctx.lineTo(t.x + t.w/2, t.y + t.h);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        if (t.text) {
          ctx.font = `${t.fontsize || 14}px ${t.font || 'Arial'}`;
          ctx.fillStyle = t.textcolor || '#000';
          ctx.fillText(t.text, t.x + 8, t.y + t.h / 2);
        }
        ctx.restore();
      }

      // 4) Pijlen (met optionele pijlpunt)
      for (const a of msg.arrows || []) {
        ctx.save();
        applyLineType = (ctx, a.linetype);
        ctx.lineWidth = a.linewidth || 1;
        ctx.strokeStyle = a.stroke || '#000';

        // lijn
        ctx.beginPath();
        ctx.moveTo(a.x1, a.y1);
        ctx.lineTo(a.x2, a.y2);
        ctx.stroke();

        // pijlpunt
        const L = a.arrow || 0;
        if (L > 0) {
          const ang = Math.atan2(a.y2 - a.y1, a.x2 - a.x1);
          const left = { x: a.x2 - L * Math.cos(ang - Math.PI / 6), y: a.y2 - L * Math.sin(ang - Math.PI / 6) };
          const right = { x: a.x2 - L * Math.cos(ang + Math.PI / 6), y: a.y2 - L * Math.sin(ang + Math.PI / 6) };
          ctx.beginPath();
          ctx.moveTo(a.x2, a.y2);
          ctx.lineTo(left.x, left.y);
          ctx.moveTo(a.x2, a.y2);
          ctx.lineTo(right.x, right.y);
          ctx.stroke();
        }

        if (a.text) {
          ctx.font = `${a.fontsize || 12}px ${a.font || 'Arial'}`;
          ctx.fillStyle = a.textcolor || '#000';
          ctx.fillText(a.text, a.x1 + 25, (a.y1 + a.y2) / 2 -4 );
        }
        ctx.restore();
      }

            // 5) Images afbeeldingen
      if (Array.isArray(msg.images)) {
        // laad alle benodigde images eerst
        const toLoad = msg.images
          .filter(im => im.filename)
          .map(im => imageCache.get(im.filename));

        // wacht op alles wat nog bezig is
        await Promise.all(toLoad);

        for (const im of msg.images) {
          if (!im.filename) continue;
          const img = await imageCache.get(im.filename);
          if (!img) continue;
          ctx.drawImage(img, im.x || 0, im.y || 0, im.w || img.width, im.h || img.height);
        }
      }
    }

    return {render, clear, imageCache, resetCache() { imageCache.clear(); } // handig als je ooit wilt resetten
      
    };
  }

  const DrawCanvas = { createRenderer };
  if (typeof module !== 'undefined') module.exports = DrawCanvas;
  else global.DrawCanvas = DrawCanvas;
})(this);