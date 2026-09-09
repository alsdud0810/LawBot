"""Review staged paths and common credential signatures without printing secrets."""
import re
import subprocess
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    command = ['git', '-c', f'safe.directory={root.as_posix()}']
    def git(*args):
        return subprocess.check_output([*command, *args], cwd=root)
    paths = git('diff', '--cached', '--name-only', '-z').decode().split('\0')
    forbidden, suspicious = [], []
    signature = re.compile(rb'(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
    for name in filter(None, paths):
        path = Path(name)
        parts = path.parts
        if ((path.name.startswith('.env') and path.name != '.env.example')
            or any(p in {'.venv', '.cache', '.sentence_transformers', 'models', '__pycache__'} for p in parts)
            or path.suffix.lower() in {'.pdf', '.faiss', '.safetensors', '.pt', '.pth'}
            or (name.startswith(('data/raw/', 'data/processed/', 'data/vector_index/')) and path.name != '.gitkeep')):
            forbidden.append(name)
        data = git('show', ':' + name)
        if signature.search(data):
            suspicious.append(name)
    print({'staged_files': len(list(filter(None, paths))), 'forbidden_paths': forbidden, 'credential_signature_files': suspicious})
    if forbidden or suspicious:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
