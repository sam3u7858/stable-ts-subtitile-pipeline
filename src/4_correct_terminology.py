import re
import time
from datetime import datetime

# 錯誤-正確詞彙對照字典
correction_dict = {
    "好鬼": "豪鬼",
    "幻團護石": "飯糰護石",
    "索恩龍": "鎖刃龍",
    "斐迪南": "費迪南",
    "天譴砂原": "天塹沙原",
    "暑假": "蘇加",
    "精神斗首": "精神抖擻",
    "鬥技大揮任務": "鬥技大會任務",
    "而塞": "耳塞",
    "很擋路的前螢幕視窗": "全螢幕視窗",
    "參點": "餐點",
    "licon": "ICON",
    "習俗修正": "係數修正",
    "眼咒的攻擊": "演奏的攻擊",
    "狩制響玉": "設置響玉",
    "疊加咒擊": "疊加奏擊",
    "大小晶": "大小金",
    "熔垃穿甲彈": "龍熱穿甲彈",
    "黑石龍": "黑蝕龍",
    "黃雷龍": "煌雷龍",
    "圓樟": "獄焰鱆",
    "洞縫龍": "凍峰龍",
    "進化蜜蟲": "淨化蜜蟲",
    "鬥雞大會": "鬥技大會",
    "赫元獸": "赫猿獸"
}

def read_srt_file(filename):
    """讀取 SRT 檔案"""
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def write_srt_file(filename, content):
    """寫入 SRT 檔案"""
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def parse_srt_blocks(content):
    """解析 SRT 內容為區塊列表"""
    blocks = re.split(r'\n\n+', content.strip())
    parsed_blocks = []
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            index = lines[0]
            timestamp = lines[1]
            text = '\n'.join(lines[2:])
            parsed_blocks.append({
                'index': index,
                'timestamp': timestamp,
                'text': text,
                'original_block': block
            })
        else:
            parsed_blocks.append({
                'index': '',
                'timestamp': '',
                'text': '',
                'original_block': block
            })
    
    return parsed_blocks

def apply_corrections(text):
    """使用字典直接取代錯誤詞彙"""
    corrected_text = text
    corrections_made = []
    
    for wrong_term, correct_term in correction_dict.items():
        if wrong_term in corrected_text:
            corrected_text = corrected_text.replace(wrong_term, correct_term)
            corrections_made.append(f"{wrong_term} -> {correct_term}")
    
    return corrected_text, corrections_made

def write_partial_srt(blocks, filename):
    """即時寫入部分 SRT 內容到檔案"""
    result_blocks = []
    
    for block in blocks:
        if block['text']:
            result_blocks.append(f"{block['index']}\n{block['timestamp']}\n{block['text']}")
        else:
            result_blocks.append(block['original_block'])
    
    content = '\n\n'.join(result_blocks)
    write_srt_file(filename, content)

def process_srt_with_corrections(blocks, output_filename=None):
    """使用字典取代方式處理 SRT 區塊"""
    processed_blocks = []
    total_corrections = 0
    
    for i, block in enumerate(blocks):
        print(f"處理第 {i+1}/{len(blocks)} 個區塊")
        
        if not block['text']:
            processed_blocks.append(block)
            continue
        
        # 直接使用字典取代
        corrected_text, corrections_made = apply_corrections(block['text'])
        
        if corrections_made:
            print(f"  修正: {', '.join(corrections_made)}")
            block['text'] = corrected_text
            total_corrections += len(corrections_made)
        else:
            print(f"  無需修正")
        
        processed_blocks.append(block)
        
        # 即時寫入檔案
        if output_filename and (i + 1) % 10 == 0:  # 每 10 個區塊寫入一次
            write_partial_srt(processed_blocks, output_filename)
            print(f"已更新檔案: {output_filename} (處理到第 {i+1} 個區塊)")
    
    print(f"總共進行了 {total_corrections} 次修正")
    return processed_blocks

def rebuild_srt_content(blocks):
    """重建 SRT 內容並重新編號"""
    result_blocks = []
    valid_index = 1
    
    for block in blocks:
        if block['text']:
            result_blocks.append(f"{valid_index}\n{block['timestamp']}\n{block['text']}")
            valid_index += 1
        else:
            original = block['original_block']
            if re.match(r'^\d+_\d+', original):
                continue
            else:
                result_blocks.append(original)
    
    return '\n\n'.join(result_blocks)

def main():
    """主程式"""
    input_filename = input("請輸入要處理的 SRT 檔案名稱: ").strip()
    if not input_filename:
        input_filename = "fullvoice23_prunedpt2.srt"
    
    try:
        # 讀取 SRT 檔案
        print(f"讀取檔案: {input_filename}")
        content = read_srt_file(input_filename)
        
        # 解析 SRT 區塊
        blocks = parse_srt_blocks(content)
        print(f"找到 {len(blocks)} 個字幕區塊")
        
        # 儲存結果檔案名稱
        output_filename = f"fixed_terms_{input_filename}"
        
        # 使用字典取代處理
        processed_blocks = process_srt_with_corrections(blocks, output_filename=output_filename)
        
        # 最終確保檔案完整性並重新編號
        processed_content = rebuild_srt_content(processed_blocks)
        write_srt_file(output_filename, processed_content)
        
        print(f"處理完成！已儲存至: {output_filename}")
        
    except FileNotFoundError:
        print(f"錯誤: 找不到檔案 {input_filename}")
    except Exception as e:
        print(f"處理過程中發生錯誤: {e}")

if __name__ == "__main__":
    main() 