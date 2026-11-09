"""Create an independent Remotion project from a Markdown script."""
import argparse
import json
import re
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]

def draft(markdown, fallback):
    front = re.match(r"^---\s*\n(.*?)\n---(?:\n|$)", markdown, re.S)
    body = markdown[front.end():] if front else markdown
    meta_title = re.search(r"^title:\s*(.+)$", front.group(1), re.M) if front else None
    lines = body.splitlines()
    title = next((line[2:].strip() for line in lines if line.startswith('# ')),
                 meta_title.group(1).strip().strip("'\"") if meta_title else fallback)
    chapters = []
    fence = None
    for line in lines:
        text = line.strip()
        if text.startswith(('```','~~~')):
            fence = None if fence and text.startswith(fence) else text[:3]
            continue
        if fence or not text or text.startswith(('!', '|', '<', '---')):
            continue
        if text.startswith('## '):
            chapters.append({'title': text[3:].strip(), 'beats': []})
            continue
        if text.startswith('#'):
            continue
        text = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
        text = re.sub(r'^([-*+] |\d+\. |> )', '', text).replace('**','').replace('`','')
        if not text.strip():
            continue
        if not chapters:
            chapters.append({'title': '开场', 'beats': []})
        for sentence in re.findall(r'[^。！？]+[。！？]?', text.strip()):
            chapters[-1]['beats'].append({'text': sentence.strip(), 'label': chapters[-1]['title'],
                                         'items': [], 'frames': 90})
    chapters = [ch for ch in chapters if ch['beats']]
    if not chapters:
        raise ValueError('稿件缺少可预览的正文。')
    return {'title': title, 'chapters': chapters}

def initialize(source, dest):
    source, dest = Path(source).resolve(), Path(dest).resolve()
    if dest.exists():
        raise ValueError(f'输出目录已存在：{dest}')
    original = source.read_text(encoding='utf-8')
    demo = source == (ROOT/'examples/prefix-cache.md').resolve()
    plan = None if demo else draft(original, source.stem)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=dest.parent) as tmp:
        project = Path(tmp)/'video'
        shutil.copytree(ROOT/'assets/starter', project, ignore=shutil.ignore_patterns('node_modules','.DS_Store','out','output','build'))
        shutil.copy2(source, project/'source.md')
        (project/'public').mkdir(exist_ok=True)
        if plan:
            (project/'src/film.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        shutil.copy2(ROOT/'scripts/audio.py', project/'audio.py')
        project.rename(dest)
    print(dest)

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args=parser.parse_args()
    initialize(args.source,args.output)
