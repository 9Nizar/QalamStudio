# Video Factory smoke test

Install Python dependencies with `python -m pip install "jsonschema[format]"`.
Make `ffmpeg` (with libx264) and `ffprobe` available on PATH.

Run from the repository root with an approved constitution and an unused MP4 path in an existing directory.

```powershell
python -B workflows/video_factory/smoke_test.py constitution-approved.json smoke-test.mp4
```

The workflow checks approval before encoding a two-second synthetic video.
It measures the encoded duration with ffprobe and publishes the MP4 only after the production check passes.
