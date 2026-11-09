# 配音与时间轴

每个 beat 是一个自然意群。长句可在自定义场景中另行安排短字幕和多个动作。终稿写入项目的 `src/film.json` 后再生成或导入配音。更新音频后在 Studio 中复核词头，特别是专名、数字和英文缩写。

**导入自己的配音。** 按全片 beat 顺序命名 `001.wav`、`002.mp3` 等文件，每个序号保留一份。运行：

```bash
python3 audio.py --recordings ./recordings
```

**macOS 本机语音。** 用 `say -v '?'` 查看已安装的语音，选一个中文音色，例如：

```bash
python3 audio.py --mac-voice Tingting
```

**火山 TTS。** 在环境中配置自己的 `VOLC_TTS_API_KEY`，并选择账号有权使用的音色、资源 ID 与模型。先确认稿件再运行此命令，每个 beat 调用一次语音服务：

```bash
python3 audio.py --volc-speaker "$VOLC_TTS_SPEAKER" --volc-resource "$VOLC_TTS_RESOURCE" --volc-model "$VOLC_TTS_MODEL"
```

三种方式都使用 FFmpeg 生成 48 kHz 音轨，按真实时长向上取整到 30 fps。新时间轴在全部片段成功后生效。声音录音和凭据归各使用者管理。
