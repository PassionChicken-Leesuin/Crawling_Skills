// X search-results collector. Inject with javascript_tool AFTER the search page has rendered (wait 7-10 s).
// Replace __QID__ (query id, e.g. 'q01') and __CAP__ (max posts, e.g. 120) before injecting.
// It scrolls every 1.5 s, harvests every <article data-testid="tweet"> it sees (X virtualises the list, so
// harvesting happens before each scroll), dedupes by status id, and stops after 8 idle rounds, the cap,
// 80 rounds, or an error banner ("Something went wrong" = rate limit). State lives in window.__xcol.
(() => {
  const CAP = __CAP__, QID = '__QID__';
  window.__xcol = { items: {}, n: 0, rounds: 0, idle: 0, done: false, err: '', qid: QID };
  const S = window.__xcol;
  function grab() {
    for (const a of document.querySelectorAll('article[data-testid="tweet"]')) {
      const links = [...a.querySelectorAll('a[href*="/status/"]')];
      let m = null;
      for (const l of links) { const mm = (l.getAttribute('href') || '').match(/^\/([^\/]+)\/status\/(\d+)$/); if (mm) { m = mm; break; } }
      if (!m) continue;
      const id = m[2];
      if (S.items[id]) continue;
      const txt = (a.querySelector('[data-testid="tweetText"]') || {}).innerText || '';
      const time = (a.querySelector('time') || {}).getAttribute?.('datetime') || '';
      const stat = {};
      for (const t of ['reply', 'retweet', 'like']) { const el = a.querySelector('[data-testid="' + t + '"]'); stat[t] = el ? ((el.getAttribute('aria-label') || '').match(/\d[\d,]*/) || ['0'])[0] : ''; }
      const replying = /Replying to/.test(a.innerText.slice(0, 400));
      S.items[id] = { id, user: m[1], time, text: txt, reply: stat.reply, rt: stat.retweet, like: stat.like, replying };
      S.n++;
    }
  }
  const iv = setInterval(() => {
    try {
      const before = S.n; grab(); window.scrollBy(0, 2000); S.rounds++;
      S.idle = (S.n === before) ? S.idle + 1 : 0;
      const bt = document.body.innerText;
      if (bt.includes('Something went wrong') || bt.includes('Try reloading')) S.err = 'error-banner';
      if (S.idle >= 8 || S.n >= CAP || S.rounds >= 80 || S.err) { clearInterval(iv); S.done = true; }
    } catch (e) { S.err = String(e); clearInterval(iv); S.done = true; }
  }, 1500);
  return 'collector started ' + QID;
})()
