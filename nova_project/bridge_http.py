#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = ROOT / 'nova_project' / 'task_engine.py'
spec = importlib.util.spec_from_file_location('task_engine', ENGINE_PATH)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)

class Bridge(BaseHTTPRequestHandler):
    def reply(self, code, payload):
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.reply(200, {'ok': True})

    def do_GET(self):
        self.reply(200, {'ok': True, 'service': 'nova-project-bridge'})

    def do_POST(self):
        size = int(self.headers.get('Content-Length', '0'))
        raw = self.rfile.read(size).decode('utf-8')
        data = json.loads(raw or '{}')
        text = str(data.get('text') or '').strip()
        if not text:
            self.reply(400, {'ok': False})
            return
        state = engine.load_state()
        engine.push_event('browser-' + str(int(time.time() * 1000)), str(data.get('source') or 'browser'), str(data.get('title') or 'ChatGPT task'), text)
        engine.read_inbox(state)
        engine.tick(state)
        engine.save_state(state)
        self.reply(200, {'ok': True})

if __name__ == '__main__':
    print('Nova Project Bridge em http://127.0.0.1:8765')
    HTTPServer(('127.0.0.1', 8765), Bridge).serve_forever()
