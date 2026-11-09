"""Start or reuse this project's Remotion Studio and return a ready chapter URL."""
import argparse
import json
import os
import re
import subprocess
import time
import urllib.request
from pathlib import Path
from tempfile import NamedTemporaryFile

def preview(project: Path, chapter: int) -> str:
    project = project.resolve()
    film = json.loads((project / 'src/film.json').read_text(encoding='utf-8'))
    if not 1 <= chapter <= len(film['chapters']):
        raise ValueError(f'工程中没有 Chapter{chapter}')
    cli = project / 'node_modules/@remotion/cli/remotion-cli.js'
    if not cli.is_file():
        raise RuntimeError('请先在工程目录安装模板依赖。')
    logs = project / 'build/preview'
    logs.mkdir(parents=True, exist_ok=True)
    detached = ({'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS}
                if os.name == 'nt' else {'start_new_session': True})
    with NamedTemporaryFile(dir=logs, suffix='.log', delete=False) as log:
        log_path = Path(log.name)
        process = subprocess.Popen(
            ['node', str(cli), 'studio', 'src/Root.tsx', '--no-open'], cwd=project,
            stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, **detached)
    try:
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            status = log_path.read_text(encoding='utf-8', errors='replace')
            port = re.search(r'(?:https?://(?:localhost|127\.0\.0\.1):|Already running on port )(\d+)', status)
            if port:
                url = f'http://127.0.0.1:{port[1]}/Chapter{chapter}'
                try:
                    with urllib.request.urlopen(url, timeout=2) as response:
                        if response.status == 200 and 'Remotion Studio' in response.read().decode(errors='replace'):
                            return url
                except OSError:
                    pass
            if process.poll() not in (None, 0):
                break
            time.sleep(.25)
        raise RuntimeError(f'Studio 尚未就绪，启动日志：{log_path}\n{status[-1000:]}')
    except BaseException:
        if process.poll() is None:
            process.terminate()
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--chapter', type=int, default=1)
    args = parser.parse_args()
    print(preview(args.project, args.chapter))
