# Video Factory smoke test

Install Python dependencies with `python -m pip install "jsonschema[format]"`.
Make `ffmpeg` (with libx264) and `ffprobe` available on PATH.

Run from the repository root with an approved constitution and an unused MP4 path in an existing directory.

```powershell
python -B workflows/video_factory/smoke_test.py constitution-approved.json smoke-test.mp4
```

The workflow checks approval before encoding a two-second synthetic video.
It measures the encoded duration with ffprobe and publishes the MP4 only after the production check passes.

## Assemble a shot list

Save an ordered JSON array next to the source clips.

```json
[
  {"source": "opening.mp4", "frames": 96},
  {"source": "garden.mp4", "start_frames": 24, "frames": 72}
]
```

Source paths are relative to the manifest. Frame ranges refer to the source after conversion to 24 fps. The workflow exports a silent 720 × 1280 MP4 and preserves source aspect ratio with padding as needed.

```powershell
python -B workflows/video_factory/assemble.py constitution-approved.json shots.json montage.mp4
```
