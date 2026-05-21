let lastText = '';

function interesting(text) {
  const terms = ['projeto','tarefa','planejamento','pipeline','automação','execução','continuidade','desenvolvimento','concluir','objetivo'];
  const t = String(text || '').toLowerCase();
  return terms.filter(x => t.includes(x)).length >= 2;
}

async function post(text) {
  if (!text || text === lastText || !interesting(text)) return;
  lastText = text;
  try {
    await fetch('http://127.0.0.1:8765/event', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({source:'browser', title:text.slice(0,80), text:text, at:new Date().toISOString()})
    });
  } catch (_) {}
}

function scan() {
  const all = Array.from(document.querySelectorAll('textarea, [contenteditable="true"]'));
  const active = all.map(x => x.value || x.innerText || '').filter(Boolean).pop();
  post(active);
}

document.addEventListener('input', scan, true);
setInterval(scan, 7000);
