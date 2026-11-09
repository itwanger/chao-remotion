"""Align a project's beats to supplied audio, or narrate them with a local macOS voice."""
import argparse
import base64
import hashlib
import os
import urllib.request
import uuid
import json
import math
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

def volc_tts(text, target, speaker, resource, model):
    key = os.environ.get('VOLC_TTS_API_KEY')
    if not key or not resource or not model:
        raise ValueError('火山 TTS 需要 API Key、资源 ID 与模型。')
    body = {'user': {'uid': 'chao-remotion'}, 'event': 100, 'namespace': 'BidirectionalTTS',
            'req_params': {'text': text, 'speaker': speaker, 'model': model,
                           'audio_params': {'format': 'mp3', 'sample_rate': 24000, 'speech_rate': 0}}}
    req = urllib.request.Request('https://openspeech.bytedance.com/api/v3/tts/unidirectional/sse',
        data=json.dumps(body).encode(), headers={'Content-Type':'application/json', 'X-Api-Key':key,
        'X-Api-Resource-Id':resource, 'X-Api-Connect-Id':str(uuid.uuid4())}, method='POST')
    with urllib.request.urlopen(req, timeout=90) as response, target.open('wb') as output:
        for line in response:
            if line.startswith(b'data:'):
                chunk = json.loads(line[5:])
                if chunk.get('code', 0) not in (0, 20000000):
                    raise RuntimeError(f"语音服务返回错误 {chunk['code']}")
                if isinstance(chunk.get('data'), str):
                    output.write(base64.b64decode(chunk['data']))
    if not target.stat().st_size:
        raise ValueError('语音服务未返回音频。')

def run(project, recordings, voice, speaker, resource, model):
    project=Path(project).resolve()
    timeline=project/'src/film.json'
    film=json.loads(timeline.read_text())
    beats=[b for ch in film['chapters'] for b in ch['beats']]
    for cmd in ['ffmpeg','ffprobe']+(['say'] if voice else []):
        if not shutil.which(cmd):
            raise SystemExit(f'找不到 {cmd}')
    media=project/'public/audio'
    media.mkdir(parents=True,exist_ok=True)
    with TemporaryDirectory(dir=media) as tmp:
        temp=Path(tmp)
        for i,beat in enumerate(beats,1):
            stem=f'{i:03}'
            if voice:
                src=temp/(stem+'.aiff')
                subprocess.run(['say','-v',voice,'-o',str(src),beat['text']],check=True)
            elif speaker:
                src=temp/(stem+'.mp3')
                volc_tts(beat['text'],src,speaker,resource,model)
            else:
                matches=[p for p in Path(recordings).glob(stem+'.*') if p.suffix.lower() in ('.wav','.mp3','.m4a','.aiff')]
                if len(matches)!=1:
                    raise ValueError(f'{stem} 需要且只需要一份音频。')
                src=matches[0]
            wave=temp/(stem+'-voice.wav')
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-vn','-ac','1','-ar','48000',str(wave)],check=True)
            secs=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(wave)],text=True)
            name=f'{stem}-{hashlib.sha256(wave.read_bytes()).hexdigest()[:12]}.wav'
            wave.rename(temp/name)
            beat.update(audio='audio/'+name,frames=max(1,math.ceil(float(secs)*30)))
        new_plan=temp/'film.json'
        new_plan.write_text(json.dumps(film,ensure_ascii=False,indent=2)+'\n')
        for beat in beats:
            name=Path(beat['audio']).name
            (temp/name).replace(media/name)
        new_plan.replace(timeline)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,default=Path.cwd())
    options=parser.add_mutually_exclusive_group(required=True)
    options.add_argument('--recordings',type=Path)
    options.add_argument('--mac-voice')
    options.add_argument('--volc-speaker')
    parser.add_argument('--volc-resource')
    parser.add_argument('--volc-model')
    args=parser.parse_args()
    run(args.project,args.recordings,args.mac_voice,args.volc_speaker,args.volc_resource,args.volc_model)
