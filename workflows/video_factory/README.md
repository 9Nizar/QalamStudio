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

## Render a narrated montage

```powershell
python -B workflows/video_factory/render.py constitution-approved.json shots.json narration.wav narrated.mp4 --subtitles captions.srt --narration-offset-ms 500
```

Use the same shot manifest as the silent assembler. The video sets the output duration. The narration starts at the requested offset in milliseconds (zero by default), and silence fills the rest. Narration that extends past the video is rejected. Optional SRT cues use the video timeline and are burned into the image with FFmpeg's libass filter.

Choose an unused output path in an existing directory. The MP4 is saved only after the production check and a full audio and video decode succeed.
