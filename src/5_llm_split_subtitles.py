import re
import requests
from datetime import datetime, timedelta
import math
import time

# SRT 讀取

def read_srt_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def write_srt_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

# 時間字串轉 datetime

def parse_time(s):
    return datetime.strptime(s, '%H:%M:%S,%f')

def time_to_str(d):
    return d.strftime('%H:%M:%S,%f')[:-3]

# 呼叫本地 LLM 加入標點符號

def call_llm_add_punctuation(text):
    url = 'http://127.0.0.1:1234/v1/chat/completions'
    headers = {'Content-Type': 'application/json'}
    system_prompt = (
        '你是一個字幕標點符號助手。請為下列字幕文本加入適當的標點符號，包括句號、逗號、問號、驚嘆號等。'
        '保持原文內容不變，只加入標點符號。不要分段或換行，只在一行內加入標點符號。'
        '只回傳加了標點符號的文本，不要加註解。'
    )
    data = {
        "model": "gemma-3-12b-it-gat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.2
    }
    for _ in range(3):  # 最多重試3次
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            time.sleep(1)
    return text  # 若失敗則回傳原文

# 根據標點符號分段

def split_by_punctuation(text):
    """只根據標點符號將文本分段，並移除分段標點符號"""
    # 定義分段用的標點符號
    split_punctuation = ['。', '！', '？']  # 只有這些標點符號會分段
    
    segments = []
    current_segment = ""
    
    for char in text:
        current_segment += char
        
        # 檢查是否遇到分段標點符號
        if char in split_punctuation:
            # 移除標點符號後加入分段
            segment = current_segment[:-1].strip()  # 移除最後的標點符號
            if segment:  # 只添加非空的分段
                segments.append(segment)
            current_segment = ""
    
    # 處理剩餘的文本
    if current_segment.strip():
        segments.append(current_segment.strip())
    
    # 過濾空白段落
    segments = [seg for seg in segments if seg.strip()]
    
    return segments

# 根據詞數調整時間戳

def split_time(start, end, n):
    start_dt = parse_time(start)
    end_dt = parse_time(end)
    total = (end_dt - start_dt).total_seconds()
    if n == 1:
        return [(start, end)]
    step = total / n
    times = []
    for i in range(n):
        seg_start = start_dt + timedelta(seconds=step * i)
        seg_end = start_dt + timedelta(seconds=step * (i + 1)) if i < n - 1 else end_dt
        times.append((time_to_str(seg_start), time_to_str(seg_end)))
    return times

# 主處理流程

def process_srt_lines(content):
    blocks = re.split(r'\n\n+', content.strip())
    new_blocks = []
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            new_blocks.append(block)
            continue
        idx, time_line, *text_lines = lines
        text = ' '.join(text_lines)
        
        if len(text) > 16:
            # 步驟1: 用 LLM 加入標點符號
            punctuated_text = call_llm_add_punctuation(text)
            print(f"原文: {text}")
            print(f"加標點: {punctuated_text}")
            
            # 步驟2: 根據標點符號分段
            segments = split_by_punctuation(punctuated_text)
            print(f"分段結果: {segments}")
            
            if len(segments) > 1:
                # 依分割數調整時間戳
                start, end = time_line.split(' --> ')
                times = split_time(start, end, len(segments))
                
                for i, (seg, (seg_start, seg_end)) in enumerate(zip(segments, times)):
                    new_blocks.append(f"{idx}_{i+1}\n{seg_start} --> {seg_end}\n{seg}")
            else:
                # 如果沒有分段，保持原樣
                new_blocks.append(block)
        else:
            new_blocks.append(block)
    return '\n\n'.join(new_blocks)

if __name__ == '__main__':
    filename = 'fixed_terms_processed_fullvoice23_prunedpt2 copy.srt'
    content = read_srt_file(filename)
    processed_content = process_srt_lines(content)
    output_filename = 'llm_split_' + filename
    write_srt_file(output_filename, processed_content)
    print(f"已儲存分割字幕檔：{output_filename}") 