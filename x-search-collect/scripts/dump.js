// Dump the collected posts so they land on DISK instead of in the chat context.
// X's Content-Security-Policy blocks fetch() to localhost, so the page cannot POST the data to you.
// Instead, return a JSON string padded with a large filler: a tool result this big is written by the harness to
// .../tool-results/<call>.txt and only the path is shown. Then run:  python3 scripts/x_extract.py <that file> <raw dir>
// Run this BEFORE navigating the tab elsewhere (navigation resets window.__xcol).
JSON.stringify({qid: __xcol.qid, n: __xcol.n, items: Object.values(__xcol.items).map(x => [x.id, x.user, x.time, x.text, x.reply, x.rt, x.like, x.replying ? 1 : 0])})
  + '\n__FILLER__' + Array.from({length: 40000}, (_, i) => (i * 7919 % 10007).toString(36)).join(' ')
