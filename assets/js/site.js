// Caffrey Recreation Area — shared site behavior
(function () {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const EMAIL = 'Reservations@caffreyrecreation.com';

  // Full-screen menu (phones and tablets)
  const burger = $('.menu-btn'), panel = $('.menu-panel');
  const setMenu = open => {
    panel.classList.toggle('open', open);
    document.body.classList.toggle('menu-open', open);
    burger.setAttribute('aria-expanded', open);
    if (open) $('.menu-close', panel).focus(); else burger.focus();
  };
  if (burger && panel) {
    burger.addEventListener('click', () => setMenu(true));
    $('.menu-close', panel).addEventListener('click', () => setMenu(false));
    addEventListener('keydown', e => { if (e.key === 'Escape' && panel.classList.contains('open')) setMenu(false); });
    $$('.menu a', panel).forEach(a => a.addEventListener('click', () => setMenu(false)));
  }

  // Fade sections in as they scroll into view
  const reveals = $$('.reveal');
  // ?static shows everything at once (used for full-page mockup screenshots)
  if (!/[?&]static\b/.test(location.search) && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => entries.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
    }), { rootMargin: '0px 0px -8% 0px' });
    reveals.forEach(el => io.observe(el));
    // Fallback for fast jumps (anchor links, flick scrolls): show anything already reached
    const catchUp = () => reveals.forEach(el => {
      if (!el.classList.contains('in') && el.getBoundingClientRect().top < innerHeight) el.classList.add('in');
    });
    addEventListener('scroll', catchUp, { passive: true });
    addEventListener('hashchange', catchUp);
  } else reveals.forEach(el => el.classList.add('in'));

  // Sliders: one slide visible, prev/next arrows and a "1 / N" counter
  $$('[data-slider]').forEach(sl => {
    const slides = $$('.slide', sl), count = $('[data-count]', sl);
    let i = 0;
    const show = n => {
      i = (n + slides.length) % slides.length;
      slides.forEach((s, k) => s.classList.toggle('on', k === i));
      if (count) count.textContent = `${i + 1} / ${slides.length}`;
    };
    $('[data-prev]', sl).addEventListener('click', () => show(i - 1));
    $('[data-next]', sl).addEventListener('click', () => show(i + 1));
    show(0);
  });

  // Booking bar: Fri & Sat nights at weekend rates, other nights regular.
  // Rates from caffreyrecreation.com/regular-camping-rates (holiday rates quoted on request).
  const bar = $('[data-book]');
  if (bar) {
    const RATES = { rv: { reg: 52, wkd: 58, hol: 65, label: 'RV / Trailer' }, tent: { reg: 40, wkd: 46, hol: 48, label: 'Tent' } };
    const f = name => $(`[name=${name}]`, bar);
    const iso = dt => new Date(dt.getTime() - dt.getTimezoneOffset() * 6e4).toISOString().slice(0, 10);
    const parse = v => { const [y, m, dd] = v.split('-').map(Number); return new Date(y, m - 1, dd); };
    // Default to the coming Friday → Sunday
    const fri = new Date(); fri.setHours(0, 0, 0, 0); fri.setDate(fri.getDate() + ((5 - fri.getDay() + 7) % 7 || 7));
    const sun = new Date(fri); sun.setDate(fri.getDate() + 2);
    f('arrive').value = iso(fri); f('depart').value = iso(sun);
    f('arrive').min = f('depart').min = iso(new Date());
    const guests = { adults: 2, kids: 0 };
    $$('[data-count-of]', bar).forEach(c => {
      const k = c.dataset.countOf, out = $('span', c), [dn, up] = $$('button', c);
      const set = v => {
        const other = k === 'adults' ? guests.kids : guests.adults;
        guests[k] = Math.max(k === 'adults' ? 1 : 0, Math.min(v, 8 - other)); // max 8 per site
        out.textContent = `${guests[k]} ${k === 'adults' ? (guests[k] === 1 ? 'Adult' : 'Adults') : (guests[k] === 1 ? 'Kid' : 'Kids')}`;
        render();
      };
      dn.addEventListener('click', () => set(guests[k] - 1));
      up.addEventListener('click', () => set(guests[k] + 1));
      out.textContent = `${guests[k]} ${k === 'adults' ? 'Adults' : 'Kids'}`;
    });
    function render() {
      const r = RATES[f('site').value], a = parse(f('arrive').value), b = parse(f('depart').value);
      let nights = 0, wkd = 0;
      for (const t = new Date(a); t < b; t.setDate(t.getDate() + 1)) { nights++; if (t.getDay() === 5 || t.getDay() === 6) wkd++; }
      const boat = f('boat').checked && nights ? 10 : 0;
      // Holiday stays: every night at the holiday rate, three-night deposit
      const hol = f('holiday').checked;
      // 4 guests included; kids under 5 free
      const extra = Math.max(0, guests.adults - 4) * 10 * nights;
      const lodging = hol ? nights * r.hol : wkd * r.wkd + (nights - wkd) * r.reg;
      const total = lodging + extra + boat;
      const dep = !nights ? 0 : hol ? Math.min(3, nights) * r.hol : (wkd ? r.wkd : r.reg);
      const detail = hol ? 'holiday rate' : wkd ? `${wkd} weekend` : '';
      $('[data-est]', bar).innerHTML = nights > 0
        ? `<span><b>$${total}</b> est. for ${nights} night${nights > 1 ? 's' : ''}${detail ? ` (${detail})` : ''}</span><span>Deposit to hold your site: $${dep}</span>`
        : '<span>Choose a departure date after your arrival date</span>';
      $('[data-request]', bar).href = `mailto:${EMAIL}?subject=${encodeURIComponent(`Reservation request: ${r.label} site, ${f('arrive').value} to ${f('depart').value}`)}&body=${encodeURIComponent(
        `Hi Caffrey team,\n\nI'd like to request a ${r.label} site.\n\nArrive: ${f('arrive').value}\nDepart: ${f('depart').value} (${nights} night${nights === 1 ? '' : 's'})\nAdults: ${guests.adults}\nKids under 5: ${guests.kids}\nBoat launch: ${f('boat').checked ? 'Yes' : 'No'}\nHoliday stay: ${f('holiday').checked ? 'Yes' : 'No'}\nEstimated total: $${total}\n\nName:\nPhone:\n`)}`;
    }
    // Keep departure after arrival
    f('arrive').addEventListener('change', () => {
      if (f('depart').value <= f('arrive').value) { const d = parse(f('arrive').value); d.setDate(d.getDate() + 1); f('depart').value = iso(d); }
      f('depart').min = f('arrive').value;
    });
    ['site', 'arrive', 'depart', 'boat', 'holiday'].forEach(n => f(n).addEventListener('change', render));
    render();
  }

  // Photo gallery lightbox: click a photo to view it large; arrows and Escape work
  $$('[data-gallery]').forEach(g => {
    const links = $$('a', g);
    const box = document.createElement('div');
    box.className = 'lightbox';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-label', 'Photo viewer');
    box.innerHTML = '<img alt=""><button class="lb-close" aria-label="Close">×</button><button class="lb-prev" aria-label="Previous photo">‹</button><button class="lb-next" aria-label="Next photo">›</button>';
    document.body.appendChild(box);
    const img = $('img', box);
    let i = 0;
    const show = n => { i = (n + links.length) % links.length; img.src = links[i].href; img.alt = $('img', links[i]).alt; };
    const close = () => { box.classList.remove('open'); document.body.classList.remove('menu-open'); links[i].focus(); };
    links.forEach((a, k) => a.addEventListener('click', e => {
      e.preventDefault(); show(k); box.classList.add('open'); document.body.classList.add('menu-open'); $('.lb-close', box).focus();
    }));
    $('.lb-close', box).addEventListener('click', close);
    $('.lb-prev', box).addEventListener('click', () => show(i - 1));
    $('.lb-next', box).addEventListener('click', () => show(i + 1));
    box.addEventListener('click', e => { if (e.target === box) close(); });
    addEventListener('keydown', e => {
      if (!box.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(i - 1);
      if (e.key === 'ArrowRight') show(i + 1);
    });
  });

  // Newsletter → pre-filled email (no backend)
  $$('[data-news]').forEach(fm => fm.addEventListener('submit', e => {
    e.preventDefault();
    const em = $('input[type=email]', fm).value;
    location.href = `mailto:${EMAIL}?subject=${encodeURIComponent('Add me to the Caffrey list')}&body=${encodeURIComponent(`Please add ${em} to holiday-weekend and season updates.`)}`;
  }));

  // Hours: Sun 9-5, Mon-Wed closed, Thu 9-5, Fri-Sat 9-6 (store/office)
  const H = [[9, 17], null, null, null, [9, 17], [9, 18], [9, 18]];
  const NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const now = new Date(), d = now.getDay(), h = now.getHours() + now.getMinutes() / 60, today = H[d];
  const open = !!(today && h >= today[0] && h < today[1]);
  $$('[data-status]').forEach(el => {
    $('.dot', el).classList.toggle('open', open);
    $('.txt', el).textContent = open ? `Open now · until ${today[1] - 12} PM` : 'Closed now · call to reserve';
  });
  $$('[data-hours]').forEach(el => {
    el.innerHTML = NAMES.map((n, i) =>
      `<div class="${H[i] ? '' : 'closed'} ${i === d ? 'today' : ''}"><b>${n}</b>${H[i] ? `${H[i][0]}–${H[i][1] - 12}` : 'Closed'}</div>`).join('');
  });

  // Trip calculator — rates from caffreyrecreation.com/regular-camping-rates
  const calc = $('[data-calc]');
  if (calc) {
    const R = { rv: { reg: 52, wkd: 58, hol: 65 }, tent: { reg: 40, wkd: 46, hol: 48 } };
    const st = { type: 'rv', reg: 0, wkd: 2, hol: 0, guests: 4, boat: false };
    const lim = { reg: [0, 30], wkd: [0, 10], hol: [0, 5], guests: [1, 8] };
    const render = () => {
      const r = R[st.type], n = st.reg + st.wkd + st.hol;
      const extra = Math.max(0, st.guests - 4) * 10 * n;
      const boat = st.boat && n ? 10 : 0;
      const total = st.reg * r.reg + st.wkd * r.wkd + st.hol * r.hol + extra + boat;
      // 1-night deposit; 3 nights for holiday stays
      const dep = st.hol ? 3 * r.hol : n ? (st.wkd ? r.wkd : r.reg) : 0;
      $('[data-total]', calc).textContent = '$' + total;
      $('[data-deposit]', calc).textContent = '$' + dep;
      const parts = [];
      if (st.reg) parts.push(`${st.reg}×$${r.reg}`);
      if (st.wkd) parts.push(`${st.wkd}×$${r.wkd}`);
      if (st.hol) parts.push(`${st.hol}×$${r.hol}`);
      if (extra) parts.push(`+$${extra} extra guests`);
      if (boat) parts.push('+$10 boat');
      $('[data-breakdown]', calc).textContent = n ? parts.join(' · ') : 'Add at least one night';
      const label = st.type === 'rv' ? 'RV/Trailer' : 'Tent';
      $('[data-request]', calc).href = `mailto:${EMAIL}?subject=${encodeURIComponent(`Reservation request: ${label} site, ${n} nights`)}&body=${encodeURIComponent(
        `Hi Caffrey team,\n\nI'd like to request a ${label} site.\n\nNights: ${st.reg} weeknight, ${st.wkd} weekend, ${st.hol} holiday\nGuests: ${st.guests}\nBoat launch: ${st.boat ? 'Yes' : 'No'}\nEstimated total: $${total}\n\nPreferred dates:\nName:\nPhone:\n`)}`;
    };
    $$('[data-step]', calc).forEach(s => {
      const k = s.dataset.step, [dn, up] = $$('button', s), out = $('output', s);
      const set = v => { st[k] = Math.min(lim[k][1], Math.max(lim[k][0], v)); out.textContent = st[k]; render(); };
      dn.addEventListener('click', () => set(st[k] - 1));
      up.addEventListener('click', () => set(st[k] + 1));
    });
    $$('.seg button', calc).forEach(b => b.addEventListener('click', () => {
      $$('.seg button', calc).forEach(x => x.setAttribute('aria-pressed', x === b));
      st.type = b.dataset.type; render();
    }));
    const boatBtn = $('[data-boat]', calc);
    boatBtn.addEventListener('click', () => { st.boat = !st.boat; boatBtn.setAttribute('aria-pressed', st.boat); render(); });
    render();
  }

  // Contact form → opens a pre-filled email (no backend needed)
  const form = $('[data-contact]');
  if (form) form.addEventListener('submit', e => {
    e.preventDefault();
    const f = Object.fromEntries(new FormData(form));
    const body = `Name: ${f.name}\nPhone: ${f.phone}\nArrive: ${f.arrive}\nDepart: ${f.depart}\nSite: ${f.site}\nGuests: ${f.guests}\n\n${f.message}`;
    location.href = `mailto:${EMAIL}?subject=${encodeURIComponent('Reservation request — ' + f.name)}&body=${encodeURIComponent(body)}`;
  });

  $$('[data-year]').forEach(el => el.textContent = now.getFullYear());
})();
