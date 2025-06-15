#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版音乐播放器 - 支持MP3播放和歌词同步显示
Simple Music Player with synchronized lyrics display
"""

import pygame
import time
import re
import os
import threading
import sys
from typing import List, Tuple, Optional
from colorama import init, Fore, Back, Style

# 初始化colorama
init(autoreset=True)

def display_lyric_synced(lyric: str, start_time: float, end_time: float, get_current_time_func):
    """与音频同步的逐字显示歌词"""
    if not lyric:
        return

    # 计算总时长和每个字符的显示时间
    total_duration = end_time - start_time
    char_count = len(lyric)

    if char_count == 0:
        return

    # 为每个字符计算显示时间点
    char_timings = []
    for i, char in enumerate(lyric):
        char_time = start_time + (total_duration * i / char_count)
        char_timings.append((char, char_time))

    # 逐字显示
    displayed_chars = 0
    while displayed_chars < len(char_timings):
        current_time = get_current_time_func()

        # 检查是否该显示下一个字符
        while (displayed_chars < len(char_timings) and
               current_time >= char_timings[displayed_chars][1]):
            char = char_timings[displayed_chars][0]
            print(f"{Fore.CYAN}{char}", end='', flush=True)
            displayed_chars += 1

        # 如果显示完所有字符，退出
        if displayed_chars >= len(char_timings):
            break

        # 短暂休眠
        time.sleep(0.01)

    print()  # 换行

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

def play_music_with_lyrics(mp3_file: str, lrc_file: str):
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
        
        # 开始播放
        pygame.mixer.music.play()
        start_time = time.time()
        
        print("\n🎵 开始播放...")
        print("按 Ctrl+C 停止播放")
        print("-" * 50)
        
        displayed_lyrics = set()  # 记录已显示的歌词

        # 定义获取当前音频时间的函数
        def get_current_audio_time():
            return time.time() - start_time

        # 主循环
        while pygame.mixer.music.get_busy():
            current_time = get_current_audio_time()

            # 查找当前时间对应的歌词
            for i, (timestamp, lyric) in enumerate(lyrics):
                if (current_time >= timestamp and
                    i not in displayed_lyrics and
                    (i == len(lyrics) - 1 or current_time < lyrics[i + 1][0])):

                    # 计算歌词结束时间
                    if i + 1 < len(lyrics):
                        end_time = lyrics[i + 1][0]
                    else:
                        end_time = timestamp + 4.0  # 最后一句给4秒

                    # 与音频同步的逐字显示
                    display_lyric_synced(lyric, timestamp, end_time, get_current_audio_time)
                    displayed_lyrics.add(i)
                    break

            time.sleep(0.05)  # 50ms检查一次
        
        print("\n播放完成！")
        
    except KeyboardInterrupt:
        print("\n\n用户停止播放")
    except Exception as e:
        print(f"播放出错: {e}")
    finally:
        pygame.mixer.music.stop()
        pygame.mixer.quit()

def main():
    """主函数"""
    print("=" * 50)
    print("🎵 简化版音乐播放器")
    print("=" * 50)
    
    # 文件路径
    mp3_file = "画皮 - 纸砚Zyan.mp3"
    lrc_file = "画皮 - 纸砚Zyan.lrc"
    
    # 播放音乐
    play_music_with_lyrics(mp3_file, lrc_file)

if __name__ == "__main__":
    main()
