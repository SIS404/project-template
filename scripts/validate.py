#!/usr/bin/env python3
"""Portable baseline checks; external URLs and complete secret detection are out of scope."""
import os
import posixpath
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

ROOT = Path.cwd()
MODE = 'template'
REQUIRED = '''README.md CLAUDE.md AGENTS.md CHANGELOG.md LICENSE docs/architecture.md docs/development.md docs/roadmap.md
docs/decisions/.gitkeep src/.gitkeep tests/.gitkeep assets/.gitkeep scripts/validate-structure.sh scripts/validate.py
.github/workflows/validate.yml .github/ISSUE_TEMPLATE/config.yml .github/ISSUE_TEMPLATE/bug.yml .github/ISSUE_TEMPLATE/feature.yml
.github/PULL_REQUEST_TEMPLATE.md .gitignore .editorconfig .env.example'''.split()
ALLOWED = set('docs src tests scripts assets .github'.split())
LIMIT = 10 * 1024 * 1024
SPECIAL = set('README.md CLAUDE.md AGENTS.md AI_CONTEXT.md CURRENT.md PROJECTS.md CHANGELOG.md INDEX.md LICENSE PULL_REQUEST_TEMPLATE.md .gitignore .env.example .gitkeep .editorconfig'.split())
JUNK = re.compile(r'^(?:final\d*|new\d*|test\d+|untitled|new-project)$', re.I)
SENSITIVE = re.compile(r'^(?:\.env(?:\..*)?|credentials(?:\..*)?|secrets(?:\..*)?|token\.txt|id_rsa|id_ed25519)$|\.(?:key|pem|p12|mobileprovision)$', re.I)
PATTERNS = [
    ('private-key', re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----')),
    ('github-token', re.compile(rb'\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{30,}\b')),
    ('api-key', re.compile(rb'\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}\b')),
    ('aws-access-id', re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b')),
    ('slack-token', re.compile(rb'\bxox[baprs]-[A-Za-z0-9-]{20,}\b')),
    ('credential-assignment', re.compile(rb'''(?im)^\s*(?:api[_-]?key|access[_-]?token|password|client[_-]?secret|cookie)\s*[:=]\s*["']?[A-Za-z0-9+/=_-]{16,}''')),
]
errors = []
def fail(scope, path, category):
    errors.append(f'{scope}: {path}: {category}')

def visible_markdown(text):
    text = re.sub(r'(?ms)^\s*(`{3,}|~{3,}).*?^\s*\1\s*$', '', text)
    return re.sub(r'`[^`\n]+`', '', text)

def anchors(data):
    text = visible_markdown(data.decode('utf-8', errors='replace'))
    result, counts = set(), {}
    for heading in re.findall(r'(?m)^#{1,6}\s+(.+?)\s*#*\s*$', text):
        slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(slug + (f'-{count}' if count else ''))
    result.update(re.findall(r'(?:id|name)=["\']([^"\']+)["\']', text))
    return result

def check_links(scope, path, data, files):
    text = visible_markdown(data.decode('utf-8', errors='replace'))
    definitions = {key.strip().lower(): value for key, value in re.findall(r'(?m)^\s*\[([^\]]+)\]:\s*(\S+)', text)}
    destinations = re.findall(r'!?\[[^\]\n]*\]\(\s*(<[^>]*>|[^\s)]+)(?:\s+["\'][^\n]*?["\'])?\s*\)', text)
    destinations += list(definitions.values())
    for label, reference in re.findall(r'\[([^\]\n]+)\]\[([^\]\n]*)\]', text):
        key = (reference or label).strip().lower()
        if key not in definitions:
            fail(scope, path, 'undefined Markdown reference')
    for destination in destinations:
        destination = destination.strip('<>')
        try:
            url = urlsplit(destination)
        except ValueError:
            fail(scope, path, 'malformed URL')
            continue
        if url.scheme in ('http', 'https'):
            if not url.hostname or '.' not in url.hostname or any(ch.isspace() for ch in destination):
                fail(scope, path, 'malformed external URL')
            continue
        if url.scheme in ('mailto',):
            continue
        if url.scheme or destination.startswith('//'):
            fail(scope, path, 'unsupported link scheme')
            continue
        target = posixpath.normpath(posixpath.join(posixpath.dirname(path), unquote(url.path))) if url.path else path
        if target.startswith('../') or target.startswith('/'):
            fail(scope, path, 'local link escapes repository')
        elif target not in files and not any(p.startswith(target.rstrip('/') + '/') for p in files):
            fail(scope, path, 'missing local link target')
        elif url.fragment and target in files and target.endswith('.md') and unquote(url.fragment) not in anchors(files[target]):
            fail(scope, path, 'missing Markdown heading anchor')

def validate(scope, files, directories):
    for required in REQUIRED:
        if required not in files:
            fail(scope, required, 'required file missing')
    for directory in directories:
        parts = PurePosixPath(directory).parts
        if parts[0] not in ALLOWED:
            fail(scope, directory, 'illegal top-level directory')
        for part in parts:
            if part not in ('.github', 'ISSUE_TEMPLATE') and not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', part):
                fail(scope, directory, 'invalid directory name')
            if JUNK.fullmatch(part):
                fail(scope, directory, 'junk directory name')
    for path, data in files.items():
        name = PurePosixPath(path).name
        if JUNK.fullmatch(PurePosixPath(path).stem):
            fail(scope, path, 'junk file name')
        if name not in SPECIAL and not re.fullmatch(r'ADR-\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*\.md', name) and not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+)*', name):
            fail(scope, path, 'invalid file name')
        if name != '.env.example' and SENSITIVE.search(name):
            fail(scope, path, 'secret-like filename')
        if len(data) > LIMIT:
            fail(scope, path, 'file exceeds size limit')
        if PurePosixPath(path).suffix.lower() in ('.mp4','.mov','.mp3','.wav','.psd','.zip','.safetensors','.ckpt','.onnx','.pt'):
            fail(scope, path, 'raw media, archive or model is not allowed')
        for category, pattern in PATTERNS:
            if pattern.search(data):
                fail(scope, path, category)
        if name == '.env.example':
            for line in data.decode('utf-8', errors='replace').splitlines():
                if line.strip() and not line.lstrip().startswith('#') and not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*=\s*', line):
                    fail(scope, path, '.env.example must contain empty values only')
        if path.endswith('.md'):
            check_links(scope, path, data, files)

files, directories = {}, set()
for parent, dirs, names in os.walk(ROOT, followlinks=False):
    dirs[:] = [d for d in dirs if d != '.git']
    for d in dirs:
        p = Path(parent) / d
        relative = p.relative_to(ROOT).as_posix()
        directories.add(relative)
        if p.is_symlink():
            fail('working-tree', relative, 'symlink not allowed')
    for name in names:
        p = Path(parent) / name
        relative = p.relative_to(ROOT).as_posix()
        if p.is_symlink():
            fail('working-tree', relative, 'symlink not allowed')
        else:
            files[relative] = p.read_bytes()
validate('working-tree', files, directories)
# Check Git's index independently: an unstaged fix must not hide a staged secret or broken structure.
if (ROOT / '.git').exists():
    staged = {}
    entries = subprocess.check_output(['git', 'ls-files', '--stage', '-z']).split(b'\0')
    for entry in entries:
        if not entry:
            continue
        meta, path = entry.split(b'\t', 1)
        mode, oid, stage = meta.split()
        name = os.fsdecode(path)
        if mode not in (b'100644', b'100755') or stage != b'0':
            fail('index', name, 'non-regular file or unresolved merge')
            continue
        staged[name] = subprocess.check_output(['git', 'cat-file', 'blob', oid.decode()])
    if staged:
        staged_dirs = {str(parent) for path in staged for parent in PurePosixPath(path).parents if str(parent) != '.'}
        validate('index', staged, staged_dirs)
if errors:
    print('\n'.join(sorted(set(errors))))
    print(f'FAIL: {len(set(errors))} finding(s). Matched values are never printed.')
    sys.exit(1)
print(f'PASS: {MODE}; {len(files)} working-tree files; structure, local links, filenames, size and selected secret patterns checked.')
print('External URLs and exhaustive secret detection require separate verification.')
