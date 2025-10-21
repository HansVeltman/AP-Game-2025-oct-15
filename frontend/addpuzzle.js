/* frontend/addpuzzle.js */
(function (global) {
  "use strict";

// zoek en vervang je huidige basisconstanten:
const BASIS_WIDTH  = 200; // overeenkomstig puzzle-buttons2.html
const BASIS_HEIGHT = 202;

// laat schaal groter dan 1 toe (verwijder de cap of zet 'm hoog)
const MIN_SCALE = 0.2;
const MAX_SCALE = 6


  const DEFAULTS = { puzzleUrl: "puzzle-buttons2.html" };

  function init({ imgEl, send, ws = null, puzzleUrl = DEFAULTS.puzzleUrl, heightRatio = 1, onClick = null }) {

    const puzzleDock = document.getElementById("PuzzleDock");
    if (!puzzleDock) {
      console.error("AddPuzzle: #PuzzleDock niet gevonden.");
      return;
    }
    if (!imgEl) {
      console.error("AddPuzzle: imgEl ontbreekt.");
      return;
    }
    if (typeof send !== "function") {
      console.error("AddPuzzle: send(...) ontbreekt of is geen functie.");
      return;
    }

    let wrapper = null;

    async function loadPuzzle() {
      const res = await fetch(puzzleUrl, { cache: "no-cache" });
      if (!res.ok) throw new Error(`Kon puzzel niet laden (${res.status})`);

      const html = await res.text();

      const tmp = document.createElement("div");
      tmp.innerHTML = html;
      document.querySelectorAll('style[data-puzzle-style], link[rel="stylesheet"][data-puzzle-style]')
      .forEach(el => el.remove());

      tmp.querySelectorAll("style").forEach((s, i) => {
          const copy = document.createElement("style");
          copy.setAttribute("data-puzzle-style", "true");
          copy.textContent = s.textContent;
          document.head.appendChild(copy);
        });

      tmp.querySelectorAll('link[rel="stylesheet"]').forEach(linkEl => {
        const href = linkEl.getAttribute("href");
        if (!href) return;
        // voorkom dubbele opname
        if (!document.querySelector(`link[rel="stylesheet"][href="${href}"]`)) {
          const copy = document.createElement("link");
          copy.rel = "stylesheet";
          copy.href = href;
          copy.setAttribute("data-puzzle-style", "true");
          document.head.appendChild(copy);
        }
      });

      // 2) Alleen de .puzzle-wrapper uit de HTML pakken en plaatsen
      wrapper = tmp.querySelector(".puzzle-wrapper");
      if (!wrapper) {
        throw new Error("Kon .puzzle-wrapper niet vinden in puzzle-buttons2.html");
      }

      // basismaat om schaal te berekenen
      wrapper.style.width = BASIS_WIDTH + "px";
      wrapper.style.height = BASIS_HEIGHT + "px";
      wrapper.style.position = "relative"; // belangrijk voor absolute positioned children    
      wrapper.style.visibility = "hidden"; // verberg tot we een zinnige hoogte hebben gemeten

      // clickbare cursor op stukken
      wrapper.querySelectorAll(".puzzle-button").forEach(el => {
        el.classList.add("puzzle-button");
        el.style.cursor = "pointer";
      });

      puzzleDock.innerHTML = ""; // leeg dock en plaats wrapper
      puzzleDock.appendChild(wrapper);

      wirePuzzleClicks(wrapper);
      positionPuzzle();
    }  // end of loadPuzzle()
      
    function wirePuzzleClicks(root) { // Map DOM-class → messagetype
      const mapClassToMsgType = {
        strategy:     "SHOWSTRATEGY",
        process:      "SHOWPROCESS",
        organization: "SHOWORGANIZATION",
        control:      "SHOWCONTROL",
        information:  "SHOWINFORMATION",
      };

      root.querySelectorAll(".puzzle-button").forEach(el => {
        el.addEventListener("click", (e) => {
          e.preventDefault();
          const key = Object.keys(mapClassToMsgType).find(c => el.classList.contains(c));
          if (!key) return;

          const msgType = mapClassToMsgType[key];
          // 1) logregel (als onClick is meegegeven)
          if (typeof onClick === "function") onClick(key, msgType);
          // 2) bericht naar backend
          send({ messagetype: msgType, numbers: {}, texts: {} });
          });
      });
    };

    function positionPuzzle() {
      if (!wrapper) return;

      const rect = imgEl.getBoundingClientRect();
      const scrollX = window.pageXOffset || document.documentElement.scrollLeft || 0;
      const scrollY = window.pageYOffset || document.documentElement.scrollTop  || 0;

      wrapper.style.left = Math.round(rect.left + scrollX) + 'px';
      wrapper.style.top  = Math.round(rect.top  + scrollY) + 'px';

      const imgHeight = rect.height;

      // Als de image nog geen zinnige hoogte heeft (bijv. 0 of ~32px tijdens opstart),
      // wachten we even; laat de puzzel verborgen.
      const MIN_MEANINGFUL = 30; // px
      if (!imgHeight || imgHeight < MIN_MEANINGFUL) {
          wrapper.style.visibility = "hidden";
          return;
      }
      
      // positie rechts op 3% en top 40px boven aan TheMainArea
      puzzleDock.style.position = "fixed";
      puzzleDock.style.right = "3%";
      puzzleDock.style.top = `${rect.top - 40}px`; // zonder scrollY
      puzzleDock.style.zIndex = "1000";
      puzzleDock.style.pointerEvents = "auto";

      wrapper.style.transformOrigin = "top right";
      wrapper.style.pointerEvents = "auto";

      // SCHAAL: (image-hoogte × heightRatio) t.o.v. basis-hoogte van de puzzel
      const targetHeight = imgHeight * (typeof heightRatio === "number" ? heightRatio : 1);
    
      let scale = targetHeight / BASIS_HEIGHT;

      // veiligheids-rails (voorkomt gekke sprongen)
      const MIN_SCALE = 0.2;
      const MAX_SCALE = 1;
      scale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, scale));
      wrapper.style.transformOrigin = "top right";
      wrapper.style.transform = `scale(${scale})`;
      wrapper.style.visibility = "visible";




    } // end of positionPuzzle()

    // events voor herpositioneren
    window.addEventListener("resize", positionPuzzle);
    window.addEventListener("scroll", positionPuzzle);

    // zodra de afbeelding echt geladen is
    imgEl.addEventListener("load", positionPuzzle);

    // luister ook op latere formaatmutaties (andere image gekozen)
    const ro = new ResizeObserver(() => positionPuzzle());
    try { ro.observe(imgEl); } catch (_) {}

    // laden zodra mogelijk
    const kickoff = () => loadPuzzle().catch(err => console.error(err));
    if (ws && ws.readyState === 0) {
      // ws is connecting; wacht tot open
      ws.addEventListener("open", kickoff, { once: true });
    } else {
      // geen ws of al open — gewoon starten
      kickoff();
    }

    // public API (optioneel handig voor debugging of refresh)
    return {
      reload: kickoff,
      position: positionPuzzle
    };

  } // end of init()

  // exporteer globaal
  const AddPuzzle = { init };
  if (typeof module !== "undefined") module.exports = AddPuzzle;
  else global.AddPuzzle = AddPuzzle;

  window.addEventListener('DOMContentLoaded', () => {
  const imgEl = document.getElementById('TheMainArea'); // <<< canvas als anker
  if (!imgEl) { console.error('TheMainArea niet gevonden'); return; }

  AddPuzzle.init({
    imgEl,
    puzzleUrl: '/puzzle-buttons2.html',
    heightRatio: 1, // desgewenst bijstellen
    send: (m)=>console.log('puzzle send', m),
    onClick: (key, t)=>console.log('Puzzle click:', key, t),
  });
});

})(this);
