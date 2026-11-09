# 开发与本地示例

本页供维护模板的开发者使用。日常制作直接在助手里按 [README 的两句话](../README.md#quickstart)操作。

环境为 Node.js 22、npm、Python 3.9+。配音需要 FFmpeg、ffprobe 和一份录音或已配置的音色。以仓库根目录为起点创建「前缀缓存」示例：

```bash
python3 scripts/init.py examples/prefix-cache.md ./output/cache-demo
cd output/cache-demo
npm ci
python3 audio.py --mac-voice Tingting
```

其他系统可用 `python3 audio.py --recordings ./recordings`。在仓库根目录运行：

```bash
python3 scripts/preview.py --project ./output/cache-demo --chapter 1
```

该命令后台启动本工程的 Studio，等服务响应后返回 `Chapter1` 的链接。再次调用时复用已有进程。启动日志在工程的 `build/preview/`。

导出时进入示例工程运行 `npm run render`，文件位于工程的 `output/video.mp4`。首次渲染会准备浏览器，也可设置 `REMOTION_BROWSER_EXECUTABLE` 指向本机 Chrome。[配音与时间轴](audio.md)
