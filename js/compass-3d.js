/* ═══════════════════════════════════════════════════════════════════════════
   MB Capital — 3D Compass v1.0 (WebGL / Three.js, lazy & progressive)
   ─────────────────────────────────────────────────────────────────────────
   Auftrag Marco 2026-11-01: Nativer 3D-Kompass im Hero beider Sites
   (DE: N/O/S/W, warmes Antikmessing · EN: N/E/S/W, kuehler oxidiert-maritim).

   Scroll-Choreografie (Vorbild V1-Test):
     1) Kompass dreht sich beim Scrollen deutlich sichtbar mit
     2) Gehaeuse / Zifferblatt / Rose / Nadel / Lager / Glas fahren auseinander
     3) Kompass setzt sich wieder zusammen, bevor der Hero aus dem Bild laeuft

   Haerte-Gates (Fallback = vorhandenes statisches compass-vintage.webp):
     - prefers-reduced-motion: reduce  → kein 3D, statisches Bild bleibt
     - Save-Data / sehr kleine Viewports → kein 3D
     - kein WebGL / Import-Fehler       → kein 3D (still, kein Konsolen-Fehler)
   Performance:
     - Three.js wird erst NACH window.load + requestIdleCallback geladen
       (sichtbarer Seiteninhalt, LCP und Fonts bleiben unangetastet)
     - rAF pausiert, sobald Hero nicht im Viewport / Tab versteckt
     - pointer-events:none → blockiert weder Scrollen noch Touch noch Formular
   ═══════════════════════════════════════════════════════════════════════════ */
(() => {
  'use strict';

  /* ── Gates ─────────────────────────────────────────────────────────────── */
  let reduceMotion = false;
  try { reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  if (reduceMotion) return;
  try { if (navigator.connection && navigator.connection.saveData) return; } catch (e) {}

  const backdrop = document.getElementById('compass-backdrop');
  const hero = document.getElementById('hero');
  if (!backdrop || !hero) return;

  let glOK = false;
  try {
    const probe = document.createElement('canvas');
    glOK = !!(probe.getContext('webgl2') || probe.getContext('webgl'));
  } catch (e) { glOK = false; }
  if (!glOK) return;

  const isEN = (document.documentElement.lang || 'de').toLowerCase().indexOf('en') === 0;

  /* ── Varianten ─────────────────────────────────────────────────────────── */
  const CFG = isEN ? {
    /* EN — dunkleres, leicht oxidiertes Metall, kuehlere Farbstimmung, maritim */
    cardinals: ['N', 'E', 'S', 'W'],
    brass:       0x64604c,
    brassBright: 0x9a9176,
    brassDark:   0x33352b,
    patina:      '#4f6f5f',   /* Verdigris-Oxidation */
    parchmentHi: '#d5d0b8',
    parchmentLo: '#a89f7e',
    engrave:     '#26281f',
    needleN:     0xb9c4ce,    /* kuehler Stahl statt Gold */
    needleS:     0x2e3236,
    keyColor: 0xdfe9f4, keyInt: 2.6,
    rimColor: 0x7fb2d9, rimInt: 26.0,
    ambColor: 0x232830, ambInt: 1.15,
    tilt: 0.98, camY: 0.62, camZ: 3.75,
    explodeDir: 1, explodeMul: 1.18   /* EN: weiter auseinander, maritim-luftiger */
  } : {
    /* DE — dunkles Antikmessing mit Patina, Pergament, warme Gold-Stimmung */
    cardinals: ['N', 'O', 'S', 'W'],
    brass:       0x8a6a2f,
    brassBright: 0xc9a24e,
    brassDark:   0x4d3a17,
    patina:      '#54431f',
    parchmentHi: '#d9c793',
    parchmentLo: '#a5905c',
    engrave:     '#332917',
    needleN:     0xd4af37,    /* MB-Gold */
    needleS:     0x3a3f45,
    keyColor: 0xffe3b3, keyInt: 2.8,
    rimColor: 0xd4af37, rimInt: 24.0,
    ambColor: 0x2a2216, ambInt: 1.1,
    tilt: 0.86, camY: 0.55, camZ: 3.65,
    explodeDir: 1, explodeMul: 1.0
  };

  /* ── Lazy-Boot: erst nach sichtbarem Inhalt ────────────────────────────── */
  const boot = () => {
    const idle = window.requestIdleCallback || ((cb) => setTimeout(cb, 900));
    idle(() => {
      /* DE: assets/js/compass-3d.js -> ../vendor/ · EN: js/compass-3d.js -> ./vendor/ */
      const rel = ['../vendor/three.module.min.js', './vendor/three.module.min.js'];
      const load = (i) => import(new URL(rel[i], import.meta.url).href)
        .then((THREE) => { try { init(THREE); } catch (e) { /* stiller Fallback */ } })
        .catch(() => { if (i + 1 < rel.length) load(i + 1); });
      load(0);
    }, { timeout: 2500 });
  };
  if (document.readyState === 'complete') boot();
  else window.addEventListener('load', boot, { once: true });

  /* ══════════════════════════════════════════════════════════════════════ */
  function init(THREE) {
    const dprCap = window.innerWidth < 768 ? 1.5 : 1.75;
    const dpr = Math.min(window.devicePixelRatio || 1, dprCap);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'low-power' });
    renderer.setClearColor(0x000000, 0);
    const canvas = renderer.domElement;
    canvas.className = 'compass-3d-canvas';
    canvas.setAttribute('aria-hidden', 'true');
    backdrop.appendChild(canvas);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 20);
    camera.position.set(0, CFG.camY, CFG.camZ);
    camera.lookAt(0, 0.02, 0);

    /* ── Licht ─────────────────────────────────────────────────────────── */
    scene.add(new THREE.AmbientLight(CFG.ambColor, CFG.ambInt));
    const key = new THREE.DirectionalLight(CFG.keyColor, CFG.keyInt);
    key.position.set(2.2, 3.4, 2.0);
    scene.add(key);
    const rim = new THREE.PointLight(CFG.rimColor, CFG.rimInt, 9, 2);
    rim.position.set(-1.9, 1.2, 1.8);
    scene.add(rim);

    /* ── Patina-Roughness (prozedural, keine externen Assets) ──────────── */
    const patinaTex = (() => {
      const c = document.createElement('canvas'); c.width = c.height = 256;
      const g = c.getContext('2d');
      g.fillStyle = '#8a8a8a'; g.fillRect(0, 0, 256, 256);
      for (let i = 0; i < 2600; i++) {
        const x = Math.random() * 256, y = Math.random() * 256, r = 1 + Math.random() * 5;
        g.fillStyle = Math.random() < 0.5 ? 'rgba(40,40,40,0.25)' : 'rgba(210,210,210,0.20)';
        g.beginPath(); g.arc(x, y, r, 0, 6.2832); g.fill();
      }
      /* Oxidations-Flecken */
      for (let i = 0; i < 34; i++) {
        const x = Math.random() * 256, y = Math.random() * 256, r = 6 + Math.random() * 20;
        g.fillStyle = CFG.patina + '55';
        g.beginPath(); g.arc(x, y, r, 0, 6.2832); g.fill();
      }
      const t = new THREE.CanvasTexture(c);
      t.wrapS = t.wrapT = THREE.RepeatWrapping;
      return t;
    })();

    const matBrass = new THREE.MeshStandardMaterial({
      color: CFG.brass, metalness: 0.88, roughness: 0.52,
      roughnessMap: patinaTex
    });
    const matBrassBright = new THREE.MeshStandardMaterial({
      color: CFG.brassBright, metalness: 0.92, roughness: 0.34,
      roughnessMap: patinaTex
    });
    const matBrassDark = new THREE.MeshStandardMaterial({
      color: CFG.brassDark, metalness: 0.8, roughness: 0.6,
      roughnessMap: patinaTex
    });

    /* ── Zifferblatt-Textur: Pergament + Gravuren + Himmelsrichtungen ──── */
    const dialTex = (() => {
      const S = 1024, C = S / 2;
      const c = document.createElement('canvas'); c.width = c.height = S;
      const g = c.getContext('2d');

      const rg = g.createRadialGradient(C, C, 60, C, C, C);
      rg.addColorStop(0, CFG.parchmentHi);
      rg.addColorStop(0.72, CFG.parchmentLo);
      rg.addColorStop(1, shade(CFG.parchmentLo, -28));
      g.fillStyle = rg;
      g.beginPath(); g.arc(C, C, C, 0, 6.2832); g.fill();

      /* Pergament-Sprengsel */
      for (let i = 0; i < 1400; i++) {
        const a = Math.random() * 6.2832, r = Math.random() * C;
        g.fillStyle = 'rgba(90,70,40,' + (0.02 + Math.random() * 0.05) + ')';
        g.beginPath(); g.arc(C + r * Math.cos(a), C + r * Math.sin(a), 0.6 + Math.random() * 2.2, 0, 6.2832); g.fill();
      }

      /* Vignette: Rand abdunkeln (Lesbarkeit + Vintage-Look) */
      const vg = g.createRadialGradient(C, C, C * 0.35, C, C, C);
      vg.addColorStop(0, 'rgba(30,22,10,0)');
      vg.addColorStop(0.8, 'rgba(30,22,10,0.18)');
      vg.addColorStop(1, 'rgba(20,14,6,0.45)');
      g.fillStyle = vg;
      g.beginPath(); g.arc(C, C, C, 0, 6.2832); g.fill();

      const ENGRAVE = CFG.engrave;
      /* Gravur-Ringe */
      [0.985, 0.90, 0.545].forEach((rr, i) => {
        g.strokeStyle = ENGRAVE; g.globalAlpha = i === 1 ? 0.75 : 0.55;
        g.lineWidth = i === 0 ? 7 : 3;
        g.beginPath(); g.arc(C, C, C * rr, 0, 6.2832); g.stroke();
      });
      g.globalAlpha = 1;

      /* Skalenstriche: 72 fein / 12 grob / 4 Kardinal */
      for (let i = 0; i < 72; i++) {
        const a = i * 5 * Math.PI / 180;
        const card = i % 18 === 0, maj = i % 6 === 0;
        const r1 = C * 0.90, r2 = C * (card ? 0.74 : maj ? 0.795 : 0.85);
        g.strokeStyle = ENGRAVE; g.globalAlpha = card ? 1 : maj ? 0.9 : 0.55;
        g.lineWidth = card ? 9 : maj ? 4.5 : 2;
        g.beginPath();
        g.moveTo(C + r1 * Math.sin(a), C - r1 * Math.cos(a));
        g.lineTo(C + r2 * Math.sin(a), C - r2 * Math.cos(a));
        g.stroke();
      }
      g.globalAlpha = 1;

      /* Gradzahlen alle 30° — +180° versetzt gezeichnet, weil die CircleGeometry-
         Abbildung die Textur gedreht (nicht gespiegelt) auf -Z/+X legt */
      g.fillStyle = ENGRAVE; g.globalAlpha = 0.8;
      g.font = '600 34px Georgia, "Times New Roman", serif';
      g.textAlign = 'center'; g.textBaseline = 'middle';
      for (let d = 30; d < 360; d += 30) {
        if (d % 90 === 0) continue;
        const a = (d + 180) * Math.PI / 180, r = C * 0.665;
        g.save();
        g.translate(C + r * Math.sin(a), C - r * Math.cos(a));
        g.rotate(a);
        g.fillText(String(d), 0, 0);
        g.restore();
      }

      /* Kardinal-Buchstaben N/O/E/S/W — gleiche 180°-Versetzung */
      g.globalAlpha = 1;
      g.font = '700 118px Georgia, "Times New Roman", serif';
      CFG.cardinals.forEach((lbl, i) => {
        const a = (i * 90 + 180) * Math.PI / 180, r = C * 0.665;
        g.save();
        g.translate(C + r * Math.sin(a), C - r * Math.cos(a));
        g.rotate(a);
        /* Gravur-Eindruck: dunkler Kern + heller Versatz */
        g.fillStyle = 'rgba(255,250,230,0.35)'; g.fillText(lbl, 2, 3);
        g.fillStyle = ENGRAVE; g.fillText(lbl, 0, 0);
        g.restore();
      });

      const t = new THREE.CanvasTexture(c);
      t.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
      t.colorSpace = THREE.SRGBColorSpace;
      return t;
    })();

    /* ── Aufbau: Y = Kompass-Normale ───────────────────────────────────── */
    const spin = new THREE.Group();           /* Scroll- + Idle-Drehung */
    const tilt = new THREE.Group();           /* fixe 3D-Neigung */
    tilt.rotation.x = CFG.tilt;
    tilt.add(spin);
    scene.add(tilt);

    const parts = [];
    const addPart = (mesh, y0, explode, dx = 0, dz = 0) => {
      mesh.position.y = y0;
      spin.add(mesh);
      parts.push({ mesh, y0, explode, dx, dz });
      return mesh;
    };

    /* Gehaeuse: Bodentopf + Seitenwand */
    const caseBody = new THREE.Mesh(
      new THREE.CylinderGeometry(1.0, 1.06, 0.16, 96, 1, false),
      matBrass
    );
    addPart(caseBody, -0.05, -0.62 * CFG.explodeDir, 0.15, -0.1);

    /* Zifferblatt */
    /* Zifferblatt: flache Scheibe (CircleGeometry => planare, NICHT gespiegelte UVs;
       Zylinder-Deckflaechen spiegeln die Textur) + duenner Messingkern fuer die Kante */
    const dial = new THREE.Group();
    const dialCore = new THREE.Mesh(
      new THREE.CylinderGeometry(0.9, 0.9, 0.05, 96),
      matBrassDark
    );
    dial.add(dialCore);
    const dialFace = new THREE.Mesh(
      new THREE.CircleGeometry(0.9, 96).rotateX(-Math.PI / 2),
      new THREE.MeshStandardMaterial({
        map: dialTex, metalness: 0.05, roughness: 0.9
      })
    );
    dialFace.position.y = 0.027;
    dial.add(dialFace);
    addPart(dial, 0.045, -0.10 * CFG.explodeDir);

    /* Kompassrose: 8-strahlig, hell/dunkel doppelt gelegt */
    const star = (rLong, rShort, waist, mat) => {
      const sh = new THREE.Shape();
      for (let i = 0; i < 8; i++) {
        const a = i * Math.PI / 4;
        const tip = i % 2 === 0 ? rLong : rShort;
        const w = 10 * Math.PI / 180;
        const p = [
          [waist * Math.sin(a - w), waist * Math.cos(a - w)],
          [tip * Math.sin(a), tip * Math.cos(a)],
          [waist * Math.sin(a + w), waist * Math.cos(a + w)]
        ];
        p.forEach(([x, y], k) => { (i === 0 && k === 0) ? sh.moveTo(x, y) : sh.lineTo(x, y); });
      }
      sh.closePath();
      const geo = new THREE.ExtrudeGeometry(sh, { depth: 0.02, bevelEnabled: false });
      geo.rotateX(-Math.PI / 2);
      return new THREE.Mesh(geo, mat);
    };
    const rose = new THREE.Group();
    rose.add(star(0.60, 0.33, 0.13, matBrassBright));
    const roseInner = star(0.30, 0.17, 0.07, matBrassDark);
    roseInner.rotation.y = Math.PI / 8;
    roseInner.position.y = 0.012;
    rose.add(roseInner);
    addPart(rose, 0.085, 0.52 * CFG.explodeDir, 0.28, -0.22);

    /* Magnetnadel: Nord-Haelfte gold/stahl, Sued dunkel */
    const needleShape = (dir) => {
      const sh = new THREE.Shape();
      sh.moveTo(0, 0.70 * dir);
      sh.lineTo(-0.052, 0);
      sh.lineTo(0.052, 0);
      sh.closePath();
      const geo = new THREE.ExtrudeGeometry(sh, { depth: 0.024, bevelEnabled: false });
      geo.rotateX(-Math.PI / 2);
      return geo;
    };
    const needle = new THREE.Group();
    needle.add(new THREE.Mesh(needleShape(1), new THREE.MeshStandardMaterial({
      color: CFG.needleN, metalness: 0.9, roughness: 0.3
    })));
    needle.add(new THREE.Mesh(needleShape(-1), new THREE.MeshStandardMaterial({
      color: CFG.needleS, metalness: 0.75, roughness: 0.45
    })));
    addPart(needle, 0.125, 0.88 * CFG.explodeDir, -0.18, -0.30);

    /* Lager-Kappe mit dezentem MB-Monogramm */
    const capTex = (() => {
      const c = document.createElement('canvas'); c.width = c.height = 256;
      const g = c.getContext('2d');
      g.fillStyle = isEN ? '#3c3e33' : '#4d3a17';
      g.beginPath(); g.arc(128, 128, 128, 0, 6.2832); g.fill();
      g.strokeStyle = 'rgba(240,225,180,0.5)'; g.lineWidth = 5;
      g.beginPath(); g.arc(128, 128, 112, 0, 6.2832); g.stroke();
      g.font = 'italic 700 96px Georgia, serif';
      g.textAlign = 'center'; g.textBaseline = 'middle';
      g.fillStyle = isEN ? '#cfd8de' : '#e8d9a8';
      g.fillText('MB', 128, 134);
      const t = new THREE.CanvasTexture(c);
      t.colorSpace = THREE.SRGBColorSpace;
      return t;
    })();
    const bearing = new THREE.Group();
    bearing.add(new THREE.Mesh(
      new THREE.CylinderGeometry(0.088, 0.098, 0.055, 48),
      matBrassBright
    ));
    const bearTop = new THREE.Mesh(
      new THREE.CircleGeometry(0.084, 48).rotateX(-Math.PI / 2),
      new THREE.MeshStandardMaterial({ map: capTex, metalness: 0.6, roughness: 0.45 })
    );
    bearTop.position.y = 0.029;
    bearing.add(bearTop);
    addPart(bearing, 0.155, 1.28 * CFG.explodeDir, -0.55, 0.38);

    /* Glas: klare Scheibe + feiner Reflexionsbogen */
    const glass = new THREE.Group();
    glass.add(new THREE.Mesh(
      new THREE.CircleGeometry(0.94, 72).rotateX(-Math.PI / 2),
      new THREE.MeshPhysicalMaterial({
        color: 0xffffff, transparent: true, opacity: 0.10,
        roughness: 0.06, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.08,
        side: THREE.DoubleSide, depthWrite: false
      })
    ));
    const glint = new THREE.Mesh(
      new THREE.TorusGeometry(0.62, 0.018, 8, 64, 1.15).rotateX(-Math.PI / 2),
      new THREE.MeshBasicMaterial({
        color: 0xffffff, transparent: true, opacity: 0.16,
        blending: THREE.AdditiveBlending, depthWrite: false
      })
    );
    glint.rotation.y = isEN ? -0.7 : -0.5;
    glint.position.y = 0.004;
    glass.add(glint);
    addPart(glass, 0.185, 1.72 * CFG.explodeDir, 0.60, 0.30);

    /* Luenette (vorderer Messingring) */
    const bezel = new THREE.Mesh(
      new THREE.TorusGeometry(0.965, 0.07, 24, 96).rotateX(-Math.PI / 2),
      matBrassBright
    );
    addPart(bezel, 0.135, -0.32 * CFG.explodeDir, -0.34, -0.18);

    /* ── Groesse/Resize ────────────────────────────────────────────────── */
    const fit = () => {
      const w = backdrop.clientWidth || 600, h = backdrop.clientHeight || w;
      /* Backing-Store deckeln (max. ~1600px Kante) — haelt schwache Geraete fluessig */
      let eff = dpr;
      if (w * eff > 1600) eff = 1600 / w;
      renderer.setPixelRatio(eff);
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    };
    fit();
    window.addEventListener('resize', fit, { passive: true });

    /* ── Sichtbarkeit: gepinnt (fixed) → nur ueber Scroll-Phase + Tab steuern ── */
    let last = performance.now(), idleSpin = 0;

    /* ── Scroll-Choreografie ─────────────────────────────────────────────
       Strecke: 2,2 Hero-Hoehen — der Kompass ist fixiert und bleibt sichtbar,
       waehrend der Hero-Inhalt wegscrollt (V1-Verhalten):
         0,00–0,32  Drehung baut auf, Teile fahren auseinander (Peak ~0,45)
         0,55–0,80  Teile setzen sich wieder zusammen
         0,82–0,97  sanftes Ausblenden, danach Render-Stopp                  */
    const RANGE = 2.2;
    const clamp01 = (v) => v < 0 ? 0 : v > 1 ? 1 : v;
    const smooth = (a, b, x) => {
      const t = clamp01((x - a) / (b - a));
      return t * t * (3 - 2 * t);
    };

    let live = false;
    const mobScale = () => (window.innerWidth < 768 ? 0.62 : 1);

    const frame = (now) => {
      requestAnimationFrame(frame);
      const heroH = hero.offsetHeight || window.innerHeight;
      const p = clamp01((window.scrollY || 0) / (heroH * RANGE));

      /* Nach Choreografie-Ende: vollstaendig ausblenden + Render pausieren */
      if (p >= 1) {
        if (live) { backdrop.style.opacity = '0'; }
        last = now;
        return;
      }
      if (document.hidden) { last = now; return; }
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;

      /* Explosions-Huellkurve: rein 8→32 %, halten, raus 55→80 % */
      const e = smooth(0.08, 0.32, p) * (1 - smooth(0.55, 0.80, p));
      const m = mobScale();

      /* deutlich sichtbare Scroll-Drehung (~300°) + ruhige Idle-Rotation */
      idleSpin += dt * 0.06 * (1 - e);
      spin.rotation.y = p * Math.PI * 1.66 + idleSpin;

      for (const pt of parts) {
        pt.mesh.position.y = pt.y0 + pt.explode * e * m * CFG.explodeMul;
        pt.mesh.position.x = pt.dx * e * m;
        pt.mesh.position.z = pt.dz * e * m;
      }
      /* Nadel dreht sich im Explodieren dramatisch mit */
      needle.rotation.y = e * Math.PI * 2.4 + Math.sin(now / 640) * 0.03;
      rose.rotation.y = -e * Math.PI * 0.7;
      glass.rotation.y = e * Math.PI * 0.4;
      glint.rotation.y = (isEN ? -0.7 : -0.5) + e * 1.2;

      /* Fade erst am Ende der Strecke — Zusammensetzen bleibt voll sichtbar.
         Sobald der Hero weggescrollt ist (p > ~0,45), wird der Kompass hinter dem
         Folge-Content zusaetzlich auf 55% gedimmt (Lesbarkeit).
         Mobil gedeckelt (Text-Lesbarkeit, Paritaet mit bisheriger .22-.32-Daempfung). */
      const maxOp = window.innerWidth < 768 ? 0.42 : 1;
      const dim = 1 - 0.62 * smooth(0.30, 0.50, p);
      const fade = (1 - smooth(0.82, 0.97, p)) * maxOp * dim;
      backdrop.style.opacity = fade.toFixed(3);

      renderer.render(scene, camera);

      if (!live) {
        live = true;
        /* Erst NACH dem ersten echten Frame umschalten: Bild ausblenden */
        backdrop.classList.add('is-3d');
        document.body.classList.add('compass-3d-live');
      }
    };
    requestAnimationFrame(frame);
  }

  /* kleine Helfer */
  function shade(hex, amt) {
    const n = parseInt(hex.slice(1), 16);
    const r = Math.max(0, Math.min(255, (n >> 16) + amt));
    const g = Math.max(0, Math.min(255, ((n >> 8) & 255) + amt));
    const b = Math.max(0, Math.min(255, (n & 255) + amt));
    return '#' + ((r << 16) | (g << 8) | b).toString(16).padStart(6, '0');
  }
})();
