#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步音乐播放器 - 逐字显示与音频进度完全同步
Synchronized Music Player with character-by-character display synced to audio
"""

import pygame
import time
import re
import os
import sys
import threading
from typing import List, Tuple, Optional
from colorama import init, Fore, Back, Style

# 初始化colorama
init(autoreset=True)

class SyncedLyricsDisplay:
    """同步歌词显示器 - 逐字显示与音频进度同步"""
    
    def __init__(self, lyrics: List[Tuple[float, str]]):
        self.lyrics = lyrics
        self.current_index = 0
        self.displayed_lyrics = set()
        self.is_displaying = False
        self.display_thread = None
        
    def calculate_char_timings(self, lyric: str, start_time: float, end_time: float) -> List[Tuple[str, float]]:
        """计算每个字符的显示时间"""
        if not lyric:
            return []
            
        # 总时长
        total_duration = end_time - start_time
        char_count = len(lyric)
        
        # 为每个字符分配时间
        char_timings = []
        for i, char in enumerate(lyric):
            # 计算该字符应该显示的时间点
            char_time = start_time + (total_duration * i / char_count)
            char_timings.append((char, char_time))
            
        return char_timings
    
    def display_lyric_synced(self, lyric: str, start_time: float, end_time: float, current_audio_time_func):
        """与音频同步的逐字显示"""
        self.is_displaying = True
        
        try:
            # 计算每个字符的显示时间
            char_timings = self.calculate_char_timings(lyric, start_time, end_time)
            
            displayed_chars = 0
            
            while self.is_displaying and displayed_chars < len(char_timings):
                current_time = current_audio_time_func()
                
                # 检查是否该显示下一个字符
                while (displayed_chars < len(char_timings) and 
                       current_time >= char_timings[displayed_chars][1]):
                    
                    char = char_timings[displayed_chars][0]
                    print(f"{Fore.CYAN}{char}", end='', flush=True)
                    displayed_chars += 1
                
                # 如果已经显示完所有字符，退出
                if displayed_chars >= len(char_timings):
                    break
                    
                # 短暂休眠，避免CPU占用过高
                time.sleep(0.01)  # 10ms检查一次
            
            print()  # 换行
            
        except Exception as e:
            print(f"\n显示歌词时出错: {e}")
        finally:
            self.is_displaying = False
    
    def get_current_lyric_info(self, current_time: float) -> Optional[Tuple[str, float, float]]:
        """获取当前时间对应的歌词信息（歌词文本、开始时间、结束时间）"""
        if not self.lyrics:
            return None
            
        # 找到当前时间对应的歌词
        for i, (timestamp, lyric) in enumerate(self.lyrics):
            if current_time >= timestamp:
                self.current_index = i
            else:
                break
                
        if self.current_index < len(self.lyrics):
            timestamp, lyric = self.lyrics[self.current_index]
            
            # 检查是否到了显示时间且未显示过
            if current_time >= timestamp and self.current_index not in self.displayed_lyrics:
                # 计算结束时间（下一句歌词的开始时间，或者当前时间+默认时长）
                if self.current_index + 1 < len(self.lyrics):
                    end_time = self.lyrics[self.current_index + 1][0]
                else:
                    # 最后一句歌词，给予4秒显示时间
                    end_time = timestamp + 4.0
                
                self.displayed_lyrics.add(self.current_index)
                return lyric, timestamp, end_time
                
        return None
    
    def start_display_thread(self, lyric: str, start_time: float, end_time: float, current_audio_time_func):
        """在新线程中开始显示歌词"""
        if self.display_thread and self.display_thread.is_alive():
            self.stop_displaying()
            self.display_thread.join(timeout=0.1)
        
        self.display_thread = threading.Thread(
            target=self.display_lyric_synced,
            args=(lyric, start_time, end_time, current_audio_time_func)
        )
        self.display_thread.daemon = True
        self.display_thread.start()
    
    def stop_displaying(self):
        """停止当前显示"""
        self.is_displaying = False
    
    def reset(self):
        """重置显示状态"""
        self.current_index = 0
        self.displayed_lyrics.clear()
        self.stop_displaying()

def parse_lrc_file(lrc_file: str) -> List[Tuple[float, str]]:
    """解析LRC歌词文件"""
    lyrics = []
    
    if not os.path.exists(lrc_file):
        print(f"歌词文件不存在: {lrc_file}")
        return lyrics
    
    try:
        with open(lrc_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 匹配时间戳格式 [mm:ss.xxx] 或 [mm:ss]
            time_pattern = r'\[(\d{2}):(\d{2})(?:\.(\d{1,3}))?\](.*)$'
            match = re.match(time_pattern, line)
            
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                milliseconds = int(match.group(3) or 0)
                
                # 补齐毫秒位数
                if match.group(3) and len(match.group(3)) < 3:
                    milliseconds = milliseconds * (10 ** (3 - len(match.group(3))))
                
                text = match.group(4).strip()
                
                # 转换为总秒数
                total_seconds = minutes * 60 + seconds + milliseconds / 1000.0
                
                if text:  # 只添加非空歌词
                    lyrics.append((total_seconds, text))
        
        # 按时间排序
        lyrics.sort(key=lambda x: x[0])
        print(f"成功解析歌词，共 {len(lyrics)} 行")
        return lyrics
        
    except Exception as e:
        print(f"解析歌词文件出错: {e}")
        return []

def play_music_with_synced_lyrics(mp3_file: str, lrc_file: str):
    """播放音乐并同步显示歌词"""
    
    # 检查文件
    if not os.path.exists(mp3_file):
        print(f"音乐文件不存在: {mp3_file}")
        return
    
    # 初始化pygame
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
    pygame.mixer.init()
    
    try:
        # 加载音乐
        pygame.mixer.music.load(mp3_file)
        print(f"已加载: {mp3_file}")
        
        # 解析歌词
        lyrics = parse_lrc_file(lrc_file)
        lyrics_display = SyncedLyricsDisplay(lyrics)
        
        # 开始播放
        pygame.mixer.music.play()
        start_time = time.time()
        
        print(f"\n🎵 开始播放...")
        print("逐字显示与音频进度完全同步")
        print("按 Ctrl+C 停止播放")
        print("-" * 50)
        
        # 定义获取当前音频时间的函数
        def get_current_audio_time():
            return time.time() - start_time
        
        # 主循环
        while pygame.mixer.music.get_busy():
            current_time = get_current_audio_time()
            
            # 获取当前歌词信息
            lyric_info = lyrics_display.get_current_lyric_info(current_time)
            if lyric_info:
                lyric, lyric_start_time, lyric_end_time = lyric_info
                # 在新线程中开始同步显示
                lyrics_display.start_display_thread(
                    lyric, lyric_start_time, lyric_end_time, get_current_audio_time
                )
            
            time.sleep(0.05)  # 50ms检查一次
        
        print("\n播放完成！")
        
    except KeyboardInterrupt:
        print("\n\n用户停止播放")
        lyrics_display.stop_displaying()
    except Exception as e:
        print(f"播放出错: {e}")
    finally:
        lyrics_display.stop_displaying()
        pygame.mixer.music.stop()
        pygame.mixer.quit()

def main():
    """主函数"""
    print("=" * 60)
    print("🎵 同步音乐播放器 - 逐字显示与音频完全同步")
    print("=" * 60)
    
    # 文件路径
    mp3_file = "画皮 - 纸砚Zyan.mp3"
    lrc_file = "画皮 - 纸砚Zyan.lrc"
    
    print("特性:")
    print("- 逐字显示歌词")
    print("- 每个字符的显示时间根据音频进度精确计算")
    print("- 无时间戳显示，专注歌词内容")
    print("- 天蓝色文字显示")
    
    # 播放音乐
    play_music_with_synced_lyrics(mp3_file, lrc_file)

if __name__ == "__main__":
    main()
