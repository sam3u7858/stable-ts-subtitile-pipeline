"""auto_subtitle_pipeline.py
一鍵完成三步驟：
1. 音檔語音辨識 (stable_whisper)
2. 移除字幕中文字元「,」「、」
3. 修正字幕時間間隔 (<0.5 秒者自動延長)

Usage
-----
python auto_subtitle_pipeline.py \
    --audio 20250604_edited.wav \
    --initial-prompt "魔物獵人,"

Notes
-----
- stable_whisper 需安裝並下載適當模型 (建議 large-v2)。
- 產出檔案將自動循序命名：
    step1_raw.srt -> step2_nocomma.srt -> step3_fixed.srt
"""

import argparse
import pickle
from pathlib import Path
import re
from datetime import datetime, timedelta
from typing import Tuple

try:
    import stable_whisper  # type: ignore
except ImportError as e:  # pragma: no cover
    raise SystemExit("stable_whisper package is required. Install with `pip install stable-whisper`." ) from e

# -------------------------
# Step 1 – Transcription
# -------------------------

def transcribe_audio(
    audio_path: Path,
    pickle_cache: Path,
    initial_prompt: str = "",
    model_size: str = "large-v2",
) -> Path:
    """Transcribe *audio_path* to SRT with *stable_whisper*.

    If *pickle_cache* exists, the cached *result1* will be reused to avoid
    re-transcription.

    Returns the generated *.srt* file path.
    """
    if pickle_cache.exists():
        with pickle_cache.open("rb") as f:
            result1 = pickle.load(f)
            # Reset segmentation and re-split as in original logic
            result1.reset()
            result1 = (
                result1
                .split_by_gap(0.3)
                .split_by_punctuation([('.', ' '), '。', '?', '？'])
            )
    else:
        model = stable_whisper.load_model(model_size)
        result1 = model.transcribe(
            str(audio_path), regroup=False, vad=False, initial_prompt=initial_prompt
        )
        result1 = (
            result1
            .split_by_punctuation([('.', ' '), '。', '?', '？', ',', '，', (',', ' '), '、'])
            .split_by_gap(0.3)
            .split_by_punctuation([('.', ' '), '。', '?', '？'])
        )

    # Export – filename based on audio stem
    srt_path = Path(f"{audio_path.stem}_raw.srt")
    result1.to_srt_vtt(str(srt_path), segment_level=True, word_level=False)

    # Cache
    with pickle_cache.open("wb") as f:
        pickle.dump(result1, f, protocol=pickle.HIGHEST_PROTOCOL)

    return srt_path

# -------------------------
# Step 2 – Remove commas
# -------------------------

def is_timestamp_line(line: str) -> bool:
    return bool(re.match(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}", line))

def remove_commas_from_srt(input_srt: Path, output_srt: Path) -> None:
    with input_srt.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    modified = [line.replace(',', '').replace('、', '') if not is_timestamp_line(line) else line for line in lines]

    with output_srt.open("w", encoding="utf-8") as f:
        f.writelines(modified)

# -------------------------
# Step 3 – Fix subtitle timings
# -------------------------

def _parse_time(ts: str) -> datetime:
    return datetime.strptime(ts, "%H:%M:%S,%f")

def _time_to_str(dt: datetime) -> str:
    return dt.strftime("%H:%M:%S,%f")[:-3]

def fix_timings(input_srt: Path, output_srt: Path, min_gap: float = 0.5) -> None:
    content = input_srt.read_text(encoding="utf-8")
    subtitles = content.split('\n\n')

    for i in range(len(subtitles) - 1):
        current_sub = subtitles[i]
        next_sub = subtitles[i + 1]
        curr_lines = current_sub.split('\n')
        next_lines = next_sub.split('\n')
        if len(curr_lines) < 3 or len(next_lines) < 3:
            continue

        curr_end_str = curr_lines[1].split(' --> ')[1]
        next_start_str = next_lines[1].split(' --> ')[0]

        curr_end = _parse_time(curr_end_str)
        next_start = _parse_time(next_start_str)
        if (next_start - curr_end).total_seconds() < min_gap:
            # overlap – push end time earlier
            curr_lines[1] = curr_lines[1].split(' --> ')[0] + ' --> ' + next_start_str
            subtitles[i] = '\n'.join(curr_lines)

    output_srt.write_text('\n\n'.join(subtitles), encoding="utf-8")

# -------------------------
# Command-line interface
# -------------------------

def main() -> None:  # pragma: no cover
    p = argparse.ArgumentParser(description="Run 3-step subtitle pipeline")
    p.add_argument("--audio", type=Path, required=True, help="Audio file to transcribe (.wav)")
    p.add_argument("--prompt", dest="initial_prompt", default="", help="Initial prompt for transcription")
    p.add_argument("--model", dest="model_size", default="large-v2", help="stable_whisper model size")
    p.add_argument("--min-gap", type=float, default=0.5, help="Minimum gap (sec) between subtitles")
    args = p.parse_args()

    audio_path: Path = args.audio.expanduser().resolve()
    if not audio_path.exists():
        raise SystemExit(f"Audio file {audio_path} not found")

    cache_path = Path("result1.pickle")
    print("[Step 1] Transcribing audio…")
    raw_srt = transcribe_audio(audio_path, cache_path, args.initial_prompt, args.model_size)
    print(f"  ➜ Generated {raw_srt}")

    print("[Step 2] Removing commas/ideographic comma…")
    no_comma_srt = Path(f"{audio_path.stem}_nocomma.srt")
    remove_commas_from_srt(raw_srt, no_comma_srt)
    print(f"  ➜ Generated {no_comma_srt}")

    print("[Step 3] Fixing subtitle timings…")
    fixed_srt = Path(f"{audio_path.stem}_fixed.srt")
    fix_timings(no_comma_srt, fixed_srt, args.min_gap)
    print(f"  ➜ Generated {fixed_srt}\nDone.")

if __name__ == "__main__":
    main() 