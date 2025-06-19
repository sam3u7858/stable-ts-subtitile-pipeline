#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sony Camera Auto Fast Copy Script
自動偵測Sony相機存儲卡並快速複製檔案到指定目錄

功能:
- 偵測 H: 磁碟機 (JPEG/影片)
- 偵測 I: 磁碟機 (RAW)
- 自動建立以日期命名的資料夾
- 快速複製檔案到目標目錄
"""

import os
import sys
import shutil
import datetime
from pathlib import Path
import subprocess
import time
from tqdm import tqdm
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class SonyCameraFastCopy:
    def __init__(self):
        self.h_drive = "H:\\"  # JPEG/Video drive
        self.i_drive = "I:\\"  # RAW drive
        self.base_dest = "Z:\\Vod_Eggs\\a7r5 US"
        
    def check_drives_exist(self):
        """檢查H:和I:磁碟機是否存在"""
        h_exists = os.path.exists(self.h_drive)
        i_exists = os.path.exists(self.i_drive)
        
        print(f"H: drive exists: {h_exists}")
        print(f"I: drive exists: {i_exists}")
        
        return h_exists, i_exists
    
    def get_folder_name(self):
        """獲取使用者輸入的資料夾名稱"""
        today = datetime.datetime.now().strftime("%Y%m%d")
        
        print(f"\n當前日期: {today}")
        title = input("請輸入標題 (將建立為 {日期}-{標題} 格式): ").strip()
        
        if not title:
            title = "untitled"
            
        folder_name = f"{today}-{title}"
        return folder_name
    
    def create_destination_folders(self, folder_name):
        """建立目標資料夾"""
        base_folder = os.path.join(self.base_dest, folder_name)
        jpg_folder = os.path.join(base_folder, "JPG")
        mp4_folder = os.path.join(base_folder, "MP4")
        raw_folder = os.path.join(base_folder, "RAW")
        
        folders = [jpg_folder, mp4_folder, raw_folder]
        
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
            print(f"Created folder: {folder}")
            
        return jpg_folder, mp4_folder, raw_folder
    
    def count_files(self, source_path):
        """計算來源資料夾中的檔案數量"""
        try:
            file_count = 0
            total_size = 0
            for root, dirs, files in os.walk(source_path):
                file_count += len(files)
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, IOError):
                        continue
            return file_count, total_size
        except Exception:
            return 0, 0
    
    def format_size(self, size_bytes):
        """格式化檔案大小顯示"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def fast_copy_with_python(self, source, destination, description="", max_workers: int = 8):
        """使用多執行緒 + shutil 複製並以 tqdm 即時顯示進度"""
        if not os.path.exists(source):
            print(f"來源資料夾不存在: {source}")
            return False

        # 收集所有檔案清單
        file_list = []
        for root, dirs, files in os.walk(source):
            for file in files:
                file_list.append(os.path.join(root, file))

        total_files = len(file_list)
        if total_files == 0:
            print(f"來源資料夾為空: {source}")
            return True

        print(f"開始複製 {description}: 共 {total_files} 個檔案 (執行緒: {max_workers})")

        progress_bar = tqdm(
            total=total_files,
            desc=f"複製{description}",
            unit="file",
            bar_format="{desc}: {percentage:3.0f}%|{bar}| {n}/{total} 檔案 [{elapsed}<{remaining}]"
        )

        success = True

        # 定義單檔複製函式 (內部)
        def copy_single(src_path: str):
            nonlocal success
            try:
                rel_path = os.path.relpath(src_path, source)
                dest_path = os.path.join(destination, rel_path)
                dest_dir = os.path.dirname(dest_path)
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(src_path, dest_path)
            except Exception as e:
                print(f"✗ 複製檔案失敗: {src_path} → {dest_path}. 錯誤: {str(e)}")
                success = False
            finally:
                progress_bar.update(1)

        # 使用 ThreadPoolExecutor 進行多執行緒複製
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(copy_single, file_list))

        progress_bar.close()
        return success
    
    def copy_h_drive_content(self, jpg_folder, mp4_folder):
        """複製H:磁碟機的內容 (使用 Python 原生複製)"""
        print("\n--- 開始複製 H: 磁碟機內容 ---")

        # Copy DCIM content to JPG folder
        h_dcim = os.path.join(self.h_drive, "DCIM")
        if os.path.exists(h_dcim):
            success1 = self.fast_copy_with_python(h_dcim, jpg_folder, "JPEG照片")
        else:
            print(f"H: DCIM 資料夾不存在: {h_dcim}")
            success1 = False

        print()  # Add blank line between operations

        # Copy M4ROOT/CLIP content to MP4 folder
        h_clip = os.path.join(self.h_drive, "M4ROOT", "CLIP")
        if os.path.exists(h_clip):
            success2 = self.fast_copy_with_python(h_clip, mp4_folder, "MP4影片")
        else:
            print(f"H: M4ROOT/CLIP 資料夾不存在: {h_clip}")
            success2 = False

        return success1, success2
    
    def copy_i_drive_content(self, raw_folder):
        """複製I:磁碟機的內容 (使用 Python 原生複製)"""
        print("\n--- 開始複製 I: 磁碟機內容 ---")

        i_dcim = os.path.join(self.i_drive, "DCIM")
        if os.path.exists(i_dcim):
            success = self.fast_copy_with_python(i_dcim, raw_folder, "RAW檔案")
        else:
            print(f"I: DCIM 資料夾不存在: {i_dcim}")
            success = False

        return success
    
    def run(self):
        """執行主要複製流程"""
        print("=== Sony Camera Auto Fast Copy Script ===")
        print("檢查相機存儲卡...")
        
        h_exists, i_exists = self.check_drives_exist()
        
        if not h_exists and not i_exists:
            print("\n❌ 未偵測到H:或I:磁碟機，請確認相機存儲卡已正確連接")
            return False
            
        if not h_exists:
            print("\n⚠️  未偵測到H:磁碟機 (JPEG/影片)")
            
        if not i_exists:
            print("\n⚠️  未偵測到I:磁碟機 (RAW)")
            
        # Get folder name from user
        folder_name = self.get_folder_name()
        
        # Create destination folders
        print(f"\n建立目標資料夾: {folder_name}")
        jpg_folder, mp4_folder, raw_folder = self.create_destination_folders(folder_name)
        
        # Copy files
        copy_results = []
        
        if h_exists:
            jpg_success, mp4_success = self.copy_h_drive_content(jpg_folder, mp4_folder)
            copy_results.extend([jpg_success, mp4_success])
            
        if i_exists:
            raw_success = self.copy_i_drive_content(raw_folder)
            copy_results.append(raw_success)
            
        # Summary
        print("\n=== 複製完成總結 ===")
        
        if h_exists:
            print(f"H: DCIM → JPG: {'✓ 成功' if copy_results[0] else '✗ 失敗'}")
            print(f"H: M4ROOT/CLIP → MP4: {'✓ 成功' if copy_results[1] else '✗ 失敗'}")
            
        if i_exists:
            idx = 2 if h_exists else 0
            print(f"I: DCIM → RAW: {'✓ 成功' if copy_results[idx] else '✗ 失敗'}")
            
        all_success = all(copy_results)
        print(f"\n整體結果: {'✓ 全部成功' if all_success else '⚠️  部分失敗'}")
        
        return all_success

def main():
    """主函數"""
    try:
        copier = SonyCameraFastCopy()
        success = copier.run()
        
        input("\n按Enter鍵退出...")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n用戶取消操作")
        return 1
        
    except Exception as e:
        print(f"\n發生錯誤: {str(e)}")
        input("\n按Enter鍵退出...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
