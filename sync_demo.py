#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步演示脚本 - 展示逐字显示与音频同步的效果
Synchronization demo script
"""

import time
import sys
from colorama import init, Fore, Back, Style

# 初始化colorama
init(autoreset=True)

def demo_sync_timing():
    """演示同步时间计算"""
    print("=" * 60)
    print("⏱️  同步时间计算演示")
    print("=" * 60)
    
    # 模拟歌词数据
    lyrics_data = [
        (0.0, "沉沦世俗为你的美", 4.0),
        (4.0, "是人是妖还是魔鬼", 6.0),
        (6.0, "为红颜犯下罪", 9.0),
        (9.0, "邪魅 玫瑰", 12.0),
    ]
    
    print("歌词时间分配计算:")
    print("-" * 40)
    
    for start_time, lyric, end_time in lyrics_data:
        duration = end_time - start_time
        char_count = len(lyric)
        
        print(f"\n歌词: {Fore.CYAN}{lyric}")
        print(f"时间: {start_time:.1f}s - {end_time:.1f}s (时长: {duration:.1f}s)")
        print(f"字符数: {char_count}")
        print(f"每字符平均时长: {duration/char_count:.3f}s")
        
        print("字符时间分配:")
        for i, char in enumerate(lyric):
            char_time = start_time + (duration * i / char_count)
            print(f"  '{char}' -> {char_time:.3f}s")

def demo_sync_display_simulation():
    """演示同步显示模拟"""
    print("\n" + "=" * 60)
    print("🎵 同步显示模拟演示")
    print("=" * 60)
    
    # 模拟歌词
    lyric = "她美色妖冶 舞姿在摇曳"
    start_time = 0.0
    end_time = 5.0
    
    print(f"模拟歌词: {Fore.YELLOW}{lyric}")
    print(f"时间范围: {start_time:.1f}s - {end_time:.1f}s")
    print("模拟播放效果 (加速演示):")
    print("-" * 40)
    
    # 计算字符时间
    duration = end_time - start_time
    char_count = len(lyric)
    char_timings = []
    
    for i, char in enumerate(lyric):
        char_time = start_time + (duration * i / char_count)
        char_timings.append((char, char_time))
    
    # 模拟播放过程
    simulation_start = time.time()
    displayed_chars = 0
    
    print(f"{Fore.GREEN}开始模拟播放...")
    
    while displayed_chars < len(char_timings):
        # 模拟当前播放时间 (加速10倍)
        current_sim_time = (time.time() - simulation_start) * 10
        
        # 检查是否该显示下一个字符
        while (displayed_chars < len(char_timings) and 
               current_sim_time >= char_timings[displayed_chars][1]):
            char = char_timings[displayed_chars][0]
            print(f"{Fore.CYAN}{char}", end='', flush=True)
            displayed_chars += 1
        
        if displayed_chars >= len(char_timings):
            break
            
        time.sleep(0.01)  # 10ms检查间隔
    
    print(f"\n{Fore.GREEN}模拟完成!")

def demo_comparison():
    """演示固定延迟 vs 同步显示的对比"""
    print("\n" + "=" * 60)
    print("⚖️  固定延迟 vs 同步显示对比")
    print("=" * 60)
    
    test_lyric = "风声瑟瑟挑灯画下一张脸"
    
    print(f"测试歌词: {Fore.YELLOW}{test_lyric}")
    print(f"假设歌词时长: 6秒")
    
    # 固定延迟方式
    print(f"\n{Fore.RED}1. 固定延迟方式 (0.2秒/字符):")
    print("问题: 不管歌词实际时长，都按固定速度显示")
    fixed_delay = 0.2
    total_fixed_time = len(test_lyric) * fixed_delay
    print(f"   总显示时间: {total_fixed_time:.1f}秒")
    print(f"   与歌词时长差异: {abs(6.0 - total_fixed_time):.1f}秒")
    
    # 同步显示方式
    print(f"\n{Fore.GREEN}2. 同步显示方式:")
    print("优势: 根据歌词实际时长动态调整字符显示速度")
    lyric_duration = 6.0
    char_delay = lyric_duration / len(test_lyric)
    print(f"   动态字符延迟: {char_delay:.3f}秒/字符")
    print(f"   总显示时间: {lyric_duration:.1f}秒")
    print(f"   与歌词时长差异: 0.0秒 (完美同步)")

def demo_real_timing_example():
    """演示真实歌词时间的例子"""
    print("\n" + "=" * 60)
    print("🎼 真实歌词时间示例")
    print("=" * 60)
    
    # 基于实际LRC文件的数据
    real_lyrics = [
        (0.0, "沉沦世俗为你的美", 4.0),
        (4.0, "是人是妖还是魔鬼", 6.0),
        (6.0, "为红颜犯下罪", 9.0),
        (9.0, "邪魅 玫瑰", 12.0),
        (12.0, "她美色妖冶 舞姿在摇曳", 17.0),
    ]
    
    print("真实歌词时间分析:")
    print("-" * 40)
    
    for start_time, lyric, end_time in real_lyrics:
        duration = end_time - start_time
        char_count = len(lyric)
        char_speed = char_count / duration if duration > 0 else 0
        
        print(f"\n{Fore.CYAN}{lyric}")
        print(f"时间: {start_time:.1f}s - {end_time:.1f}s")
        print(f"时长: {duration:.1f}s, 字符数: {char_count}")
        print(f"显示速度: {char_speed:.2f} 字符/秒")
        
        # 显示节奏分析
        if char_speed < 2:
            rhythm = f"{Fore.GREEN}慢节奏"
        elif char_speed < 4:
            rhythm = f"{Fore.YELLOW}中等节奏"
        else:
            rhythm = f"{Fore.RED}快节奏"
        
        print(f"节奏: {rhythm}")

def main():
    """主演示函数"""
    print("🎵 音频同步逐字显示演示")
    print("展示逐字显示如何与音频进度完美同步")
    
    try:
        # 演示同步时间计算
        demo_sync_timing()
        
        # 演示同步显示模拟
        demo_sync_display_simulation()
        
        # 演示对比
        demo_comparison()
        
        # 演示真实时间例子
        demo_real_timing_example()
        
        print(f"\n{Fore.GREEN}✅ 演示完成！")
        print(f"{Fore.YELLOW}💡 运行 synced_player.py 或 simple_player.py 查看实际同步效果")
        
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}演示被用户中断")

if __name__ == "__main__":
    main()
