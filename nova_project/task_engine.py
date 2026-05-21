#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE = Path('.nova_project')
STATE = BASE / 'state.json'
INBOX = BASE / 'inbox.jsonl'
OUTBOX = BASE / 'outbox.jsonl'
LOG = BASE / 'events.log'

KEYWORDS = {
    'projeto', 'projetos', 'tarefa', 'tarefas', 'processo', 'processos',
    'planejamento', 'pipeline', 'melhoria', 'melhorias', 'desenvolvimento',
    'concluir', 'objetivo', 'execucao', 'execução', 'automacao', 'automação'
}

ACTIONS = [
    ('planejar', r'\b(plan|planej|estrat)\w*'),
    ('pesquisar', r'\b(pesquis|investig|descobr)\w*'),
    ('construir', r'\b(constru|implemen|criar|gerar)\w*'),
    ('executar', r'\b(execut|rodar|fazer|continu)\w*'),
    ('validar', r'\b(valid|test|auditar|corrig)\w*'),
    ('publicar', r'\b(enviar|entregar|responder|publicar)\w*'),
]

@dataclass
class Step:
    title: str
    status: str = 'pending'
    notes: list[str] = field(default_factory=list)

@dataclass
class WorkItem:
    id: str
    source: str
    title: str
    text: str
    score: float
    status: str = 'pending'
    created_at: str = ''
    updated_at: str = ''
    steps: list[Step] = field(default_factory=list)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure() -> None:
    BASE.mkdir(exist_ok=True)


def load_state() -> dict[str, Any]:
    ensure()
    if STATE.exists():
        return json.loads(STATE.read_text(encoding='utf-8'))
    return {'items': {}, 'seen': [], 'metrics': {'ticks': 0, 'created': 0, 'done': 0}, 'last_tick': None}


def save_state(state: dict[str, Any]) -> None:
    ensure()
    state['last_tick'] = now()
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def log(line: str) -> None:
    ensure()
    with LOG.open('a', encoding='utf-8') as f:
        f.write(f'[{now()}] {line}\n')


def publish(payload: dict[str, Any]) -> None:
    ensure()
    with OUTBOX.open('a', encoding='utf-8') as f:
        f.write(json.dumps(payload, ensure_ascii=False) + '\n')


def score_text(text: str) -> float:
    words = set(re.findall(r'[a-zA-ZÀ-ÿ0-9_-]+', text.lower()))
    kw = len(words.intersection(KEYWORDS))
    act = sum(1 for _, pattern in ACTIONS if re.search(pattern, text, re.I))
    return kw + act * 1.5


def make_steps(text: str) -> list[Step]:
    steps = [Step('Mapear objetivo, contexto e critérios de conclusão')]
    for name, pattern in ACTIONS:
        if re.search(pattern, text, re.I):
            steps.append(Step(f'{name.capitalize()} o objetivo solicitado'))
    steps.extend([
        Step('Executar checkpoint de qualidade'),
        Step('Registrar estado e aprendizados'),
        Step('Publicar progresso e próximo passo'),
    ])
    unique = []
    seen = set()
    for step in steps:
        if step.title not in seen:
            seen.add(step.title)
            unique.append(step)
    return unique


def push_event(event_id: str, source: str, title: str, text: str) -> None:
    ensure()
    with INBOX.open('a', encoding='utf-8') as f:
        f.write(json.dumps({'id': event_id, 'source': source, 'title': title, 'text': text}, ensure_ascii=False) + '\n')


def read_inbox(state: dict[str, Any]) -> int:
    ensure()
    if not INBOX.exists():
        return 0
    count = 0
    for line in INBOX.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        event_id = str(event.get('id') or '')
        if not event_id or event_id in state['seen']:
            continue
        state['seen'].append(event_id)
        text = str(event.get('text') or '').strip()
        sc = score_text(text)
        if sc < 2:
            log(f'ignored {event_id} score={sc:.2f}')
            continue
        item = WorkItem(
            id=event_id,
            source=str(event.get('source') or 'unknown'),
            title=str(event.get('title') or 'Item automático'),
            text=text,
            score=sc,
            created_at=now(),
            updated_at=now(),
            steps=make_steps(text),
        )
        state['items'][item.id] = asdict(item)
        state['metrics']['created'] += 1
        log(f'created {item.id} score={sc:.2f}')
        count += 1
    return count


def advance_item(item: dict[str, Any]) -> None:
    item['status'] = 'in_progress'
    item['updated_at'] = now()
    for step in item.get('steps', []):
        if step['status'] == 'pending':
            step['status'] = 'in_progress'
            step.setdefault('notes', []).append('Iniciado no ciclo atual')
            return
        if step['status'] == 'in_progress':
            step['status'] = 'done'
            step.setdefault('notes', []).append('Concluído no ciclo atual')
            return


def tick(state: dict[str, Any]) -> None:
    state['metrics']['ticks'] += 1
    for item_id, item in state['items'].items():
        if item.get('status') == 'done':
            continue
        advance_item(item)
        if all(step.get('status') == 'done' for step in item.get('steps', [])):
            item['status'] = 'done'
            item['updated_at'] = now()
            state['metrics']['done'] += 1
            publish({'type': 'done', 'id': item_id, 'title': item.get('title')})
            log(f'done {item_id}')
        else:
            publish({'type': 'progress', 'id': item_id, 'title': item.get('title')})
            log(f'progress {item_id}')


def report(state: dict[str, Any]) -> dict[str, Any]:
    items = state.get('items', {})
    active = [x for x in items.values() if x.get('status') != 'done']
    done = [x for x in items.values() if x.get('status') == 'done']
    return {'last_tick': state.get('last_tick'), 'metrics': state.get('metrics'), 'total': len(items), 'active': len(active), 'done': len(done), 'active_titles': [x.get('title') for x in active[:10]]}


def main() -> None:
    parser = argparse.ArgumentParser(description='Nova Project Task Engine')
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('push')
    p.add_argument('--id', required=True)
    p.add_argument('--source', required=True)
    p.add_argument('--title', default='Item automático')
    p.add_argument('--text', required=True)
    sub.add_parser('tick')
    sub.add_parser('status')
    args = parser.parse_args()

    state = load_state()
    if args.cmd == 'push':
        push_event(args.id, args.source, args.title, args.text)
        print('evento enviado')
    elif args.cmd == 'tick':
        read_inbox(state)
        tick(state)
        print(json.dumps(report(state), ensure_ascii=False, indent=2))
    elif args.cmd == 'status':
        print(json.dumps(report(state), ensure_ascii=False, indent=2))
    save_state(state)

if __name__ == '__main__':
    main()
