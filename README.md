# Stable-TS Subtitle Processing Toolkit

A comprehensive toolkit for subtitle processing using stable-whisper for speech recognition, with various post-processing features.

## Project Structure

```
new_version/
├── src/
│   ├── 1_transcribe_audio.py         # Step 1: Audio transcription
│   ├── 2_remove_punctuation.py       # Step 2: Remove punctuation
│   ├── 3_fix_timing_gaps.py          # Step 3: Fix timing gaps
│   ├── 4_correct_terminology.py      # Step 4: Correct terminology
│   ├── 5_llm_split_subtitles.py      # Step 5: LLM-based subtitle splitting
│   ├── pipeline_all_in_one.py        # Integrated pipeline (Steps 1-3)
│   └── sony_camera_fastcopy.py       # Sony camera file copying utility
├── README.md                          # English documentation (this file)
└── README_zh-tw.md                    # Traditional Chinese documentation
```

## Execution Order

### Manual Step-by-Step Execution (Recommended for Fine Control)

1. **1_transcribe_audio.py** - Audio Transcription

   - Uses stable-whisper to convert audio files to subtitles
   - Automatic segmentation and punctuation handling
   - Output: `fullvoicev23.srt`

2. **2_remove_punctuation.py** - Remove Punctuation

   - Removes commas and ideographic commas (「,」「、」) from subtitle text
   - Preserves timestamps unchanged
   - Output: `fullvoice23_prunedpt2.srt`

3. **3_fix_timing_gaps.py** - Fix Timing Gaps

   - Fixes subtitle intervals shorter than 0.5 seconds to prevent overlaps
   - Avoids subtitle display conflicts
   - Output: `processed_fullvoice23_prunedpt2.srt`

4. **4_correct_terminology.py** - Correct Terminology

   - Uses predefined dictionary to correct common terminology errors (e.g., gaming terms)
   - Supports custom dictionary extensions
   - Output: `fixed_terms_processed_fullvoice23_prunedpt2.srt`

5. **5_llm_split_subtitles.py** - LLM-based Subtitle Splitting
   - Uses local LLM to add punctuation and intelligently split long subtitles
   - Automatically segments overly long subtitle segments based on semantics
   - Output: `llm_split_*.srt`

### Automated Pipeline Execution

- **pipeline_all_in_one.py** - One-click execution of Steps 1-3
  - Integrates the functionality of the first three steps
  - Suitable for batch processing or quick basic subtitle generation
  - Supports command-line parameter customization

### Utility Tools

- **sony_camera_fastcopy.py** - Sony Camera File Management
  - Automatically detects Sony camera storage cards (H: and I: drives)
  - Fast copying of JPEG, RAW, and video files to specified directories
  - Supports multi-threaded acceleration for copying

## Usage

### Command Line Execution

```bash
# Step-by-step execution
python src/1_transcribe_audio.py
python src/2_remove_punctuation.py
python src/3_fix_timing_gaps.py
python src/4_correct_terminology.py
python src/5_llm_split_subtitles.py

# One-click pipeline execution
python src/pipeline_all_in_one.py --audio your_audio.wav --prompt "your_prompt"

# Sony camera file copying
python src/sony_camera_fastcopy.py
```

### Pipeline Parameters

```bash
python src/pipeline_all_in_one.py \
    --audio 20250604_edited.wav \          # Audio file path
    --prompt "Monster Hunter," \           # Initial prompt (optional)
    --model large-v2 \                     # Whisper model size
    --min-gap 0.5                          # Minimum time interval (seconds)
```

## Dependencies

```bash
pip install stable-whisper
pip install requests
pip install tqdm
pip install pathlib
```

## System Requirements

- **Operating System**: Windows / macOS / Linux
- **Python Version**: 3.8+
- **Hardware Requirements**:
  - GPU: Recommended 4GB+ VRAM (for Whisper model)
  - RAM: Recommended 8GB+
  - Storage: Sufficient space for audio and subtitle files

## Important Notes

1. **LLM Service**: Step 5 requires a local LLM service running at `http://127.0.0.1:1234`

   - Recommend using LM Studio or similar tools
   - Model recommendation: gemma-3-12b-it-gat or other models with good Chinese support

2. **File Paths**: Ensure audio and output paths are correctly configured

   - Supports both relative and absolute paths
   - Recommend using English paths to avoid encoding issues

3. **Model Download**: First-time use requires downloading stable-whisper models

   - Recommend using large-v2 model (higher accuracy)
   - Use medium or small models if GPU memory is insufficient

4. **Execution Order**: Numbered files represent suggested execution order
   - Steps can be skipped based on requirements
   - Steps 1-3 can be completed in one go using pipeline_all_in_one.py

## Output Files Description

- `fullvoicev23.srt` - Raw transcription results (with full punctuation)
- `fullvoice23_prunedpt2.srt` - After punctuation removal (keeping periods and question marks)
- `processed_fullvoice23_prunedpt2.srt` - After timing correction (no overlaps)
- `fixed_terms_processed_fullvoice23_prunedpt2.srt` - After terminology correction (accurate professional terms)
- `llm_split_*.srt` - Final version after LLM splitting (best readability)

## Troubleshooting

### Common Issues

1. **GPU Memory Insufficient**

   ```bash
   # Solution: Use smaller model
   python src/pipeline_all_in_one.py --model medium --audio your_audio.wav
   ```

2. **LLM Service Connection Failed**

   - Confirm local LLM service is running
   - Check if port number is 1234
   - Ensure model is properly loaded

3. **Inaccurate Subtitle Timing**

   ```bash
   # Solution: Adjust minimum gap parameter
   python src/pipeline_all_in_one.py --min-gap 0.3 --audio your_audio.wav
   ```

4. **Incomplete Terminology Correction**
   - Check dictionary settings in `4_correct_terminology.py`
   - Add custom terminology pairs as needed

### Performance Optimization Tips

- Use GPU acceleration (requires CUDA installation)
- Choose appropriate Whisper model size
- Process large files in batches
- Use SSD storage for improved I/O performance

## License

This project is released under the MIT License.
