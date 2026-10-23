// Caffrey Recreation Area — shared site behavior
(function () {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const EMAIL = 'Reservations@caffreyrecreation.com';

  // Header turns solid once the hero scrolls away
  const head = $('.site-head');
  const onScroll = () => head && head.classList.toggle('scrolled', scrollY > 40);
  addEventListener('scroll', onScroll, { passive: true }); onScroll();

  // Full-screen menu
  const burger = $('.burger'), panel = $('.menu-panel');
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
