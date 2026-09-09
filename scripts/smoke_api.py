"""Exercise a real local Uvicorn server; optionally load a measured index."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default='data/vector_index')
    parser.add_argument('--output', type=Path, default=Path('evaluation/api_smoke.json'))
    args = parser.parse_args()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    env = {**os.environ, 'VECTOR_INDEX_DIR': args.index, 'LLM_API_KEY': '', 'LLM_MODEL': ''}
    log = Path('data/api_smoke.log')
    with log.open('w', encoding='utf-8') as handle:
        process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', str(port)],
                                   env=env, stdout=handle, stderr=handle)
        try:
            base = f'http://127.0.0.1:{port}'
            for _ in range(180):
                if process.poll() is not None:
                    raise RuntimeError(f'Uvicorn exited {process.returncode}; see {log}')
                try:
                    with urllib.request.urlopen(base + '/health', timeout=2) as response:
                        health = json.load(response)
                    break
                except OSError:
                    time.sleep(1)
            else:
                raise TimeoutError('Uvicorn startup timed out')
            assert health == {'status': 'ok'}
            bodies = []
            for language, question in [('ko', '퇴직 후 임금은 언제 지급하나요?'), ('en', 'When must wages be paid after retirement?')]:
                req = urllib.request.Request(base + '/api/v1/chat',
                    data=json.dumps({'question': question, 'language': language}).encode(),
                    headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=120) as response:
                    body = json.load(response)
                assert body['language'] == language and body['answer']
                if (Path(args.index) / 'index.faiss').exists():
                    assert body['sources'] and all(s['url'] for s in body['sources'])
                bodies.append(body)
            report = {'health': health, 'chat': bodies, 'index': args.index,
                      'generator': 'DeterministicGenerator (no paid LLM)', 'http_verified': True}
            args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
            print('HTTP health and Korean/English chat verified')
        finally:
            process.terminate()
            process.wait(timeout=15)


if __name__ == '__main__':
    main()
