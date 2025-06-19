# Stable-TS 字幕處理工具集

這是一個專門處理字幕檔案的工具集，使用 stable-whisper 進行語音辨識，並包含多種後處理功能。

## 目錄結構

```
new_version/
├── src/
│   ├── 1_transcribe_audio.py         # 步驟1: 音檔語音辨識
│   ├── 2_remove_punctuation.py       # 步驟2: 移除標點符號
│   ├── 3_fix_timing_gaps.py          # 步驟3: 修正時間間隔
│   ├── 4_correct_terminology.py      # 步驟4: 校正專業術語
│   ├── 5_llm_split_subtitles.py      # 步驟5: LLM 分割長字幕
│   ├── pipeline_all_in_one.py        # 整合流水線（步驟1-3）
│   └── sony_camera_fastcopy.py       # Sony 相機檔案快速複製工具
├── README.md                          # 英文版說明
└── README_zh-tw.md                    # 中文版說明（本檔案）
```

## 執行順序說明

### 手動逐步執行（推薦用於精細控制）

1. **1_transcribe_audio.py** - 音檔語音辨識

   - 使用 stable-whisper 將音訊檔案轉換為字幕
   - 自動分段並處理標點符號
   - 產出：`fullvoicev23.srt`

2. **2_remove_punctuation.py** - 移除標點符號

   - 移除字幕文字中的逗號和頓號（「,」「、」）
   - 保留時間戳記不變
   - 產出：`fullvoice23_prunedpt2.srt`

3. **3_fix_timing_gaps.py** - 修正時間間隔

   - 修正字幕間隔小於 0.5 秒的時間重疊問題
   - 避免字幕顯示衝突
   - 產出：`processed_fullvoice23_prunedpt2.srt`

4. **4_correct_terminology.py** - 校正專業術語

   - 使用預設字典修正常見錯誤詞彙（如遊戲術語）
   - 支援自訂字典擴充
   - 產出：`fixed_terms_processed_fullvoice23_prunedpt2.srt`

5. **5_llm_split_subtitles.py** - LLM 分割長字幕
   - 使用本地 LLM 為長字幕添加標點符號並智能分段
   - 根據語意自動切分過長的字幕段落
   - 產出：`llm_split_*.srt`

### 自動化流水線執行

- **pipeline_all_in_one.py** - 一鍵執行步驟 1-3
  - 整合了前三個步驟的功能
  - 適合批量處理或需要快速產出基本字幕的情況
  - 支援命令列參數自訂

### 輔助工具

- **sony_camera_fastcopy.py** - Sony 相機檔案管理
  - 自動偵測 Sony 相機存儲卡（H: 和 I: 磁碟機）
  - 快速複製 JPEG、RAW 和影片檔案到指定目錄
  - 支援多執行緒加速複製

## 使用方式

### 命令行執行

```bash
# 步驟式執行
python src/1_transcribe_audio.py
python src/2_remove_punctuation.py
python src/3_fix_timing_gaps.py
python src/4_correct_terminology.py
python src/5_llm_split_subtitles.py

# 一鍵流水線執行
python src/pipeline_all_in_one.py --audio your_audio.wav --prompt "your_prompt"

# Sony 相機檔案複製
python src/sony_camera_fastcopy.py
```

### 流水線參數說明

```bash
python src/pipeline_all_in_one.py \
    --audio 20250604_edited.wav \          # 音檔路徑
    --prompt "魔物獵人," \                  # 初始提示詞（可選）
    --model large-v2 \                     # Whisper 模型大小
    --min-gap 0.5                          # 最小時間間隔（秒）
```

## 依賴套件

```bash
pip install stable-whisper
pip install requests
pip install tqdm
pip install pathlib
```

## 系統需求

- **作業系統**：Windows / macOS / Linux
- **Python 版本**：3.8+
- **硬體需求**：
  - GPU：建議有 4GB+ VRAM（用於 Whisper 模型）
  - RAM：建議 8GB+
  - 儲存空間：充足空間存放音檔和字幕檔案

## 注意事項

1. **LLM 服務**：步驟 5 需要本地 LLM 服務運行在 `http://127.0.0.1:1234`

   - 建議使用 LM Studio 或類似工具
   - 模型建議：gemma-3-12b-it-gat 或其他中文支援較好的模型

2. **檔案路徑**：確保音檔和輸出路徑正確設定

   - 支援相對路徑和絕對路徑
   - 建議使用英文路徑避免編碼問題

3. **模型下載**：首次使用需要下載 stable-whisper 模型

   - 建議使用 large-v2 模型（精確度較高）
   - 若 GPU 記憶體不足可改用 medium 或 small

4. **執行順序**：數字編號代表建議的執行順序
   - 可根據需求跳過特定步驟
   - 步驟 1-3 可用 pipeline_all_in_one.py 一次完成

## 輸出檔案說明

- `fullvoicev23.srt` - 原始辨識結果（含完整標點符號）
- `fullvoice23_prunedpt2.srt` - 移除標點符號後（保留句號問號）
- `processed_fullvoice23_prunedpt2.srt` - 修正時間間隔後（無重疊）
- `fixed_terms_processed_fullvoice23_prunedpt2.srt` - 校正術語後（專業詞彙正確）
- `llm_split_*.srt` - LLM 分割後的最終版本（最佳可讀性）

## 疑難排解

### 常見問題

1. **GPU 記憶體不足**

   ```bash
   # 解決方案：使用較小的模型
   python src/pipeline_all_in_one.py --model medium --audio your_audio.wav
   ```

2. **LLM 服務連線失敗**

   - 確認本地 LLM 服務正在運行
   - 檢查埠號是否為 1234
   - 確認模型已正確載入

3. **字幕時間不準確**

   ```bash
   # 解決方案：調整最小間隔參數
   python src/pipeline_all_in_one.py --min-gap 0.3 --audio your_audio.wav
   ```

4. **術語修正不完整**
   - 檢查 `4_correct_terminology.py` 中的字典設定
   - 可自行添加需要修正的詞彙對照

### 效能優化建議

- 使用 GPU 加速（需安裝 CUDA）
- 選擇適當的 Whisper 模型大小
- 分批處理大量檔案
- 使用 SSD 儲存提升 I/O 效能

## 授權條款

本專案採用 MIT License 授權條款。
