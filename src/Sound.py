import pygame as _pygame
import pathlib
from typing import Optional

from . import Profile
from .Log import *

class AudioManager:
    """
    Default volume:
        \tSE - 0.2\n
        \tBGM - 0.2\n
    Be careful with your ears.
    """

    se_stack: list[tuple[str, _pygame.mixer.Sound]] = []
    bgm_stack: list[tuple[str, _pygame.mixer.Sound]] = []
    playing_bgm_index = -1

    __se_volume = 0.2
    __bgm_volume = 0.2

    @staticmethod
    def load_se(name: str, filepath: str | pathlib.Path):
        sound = _pygame.mixer.Sound(filepath)
        AudioManager.se_stack.append((name, sound))

    @staticmethod
    def load_bgm(name: str, filepath: str | pathlib.Path):
        sound = _pygame.mixer.Sound(filepath)
        AudioManager.bgm_stack.append((name, sound))

    @staticmethod
    def play_se(name: str, max_time: int = 0, fade_ms: int = 0):
        index = [name for name, sound in AudioManager.se_stack].index(name)
        sound = AudioManager.se_stack[index][1]
        
        sound.set_volume(AudioManager.__se_volume)
        sound.play(maxtime=max_time, fade_ms=fade_ms)

        AudioManager.se_stack[index][1].play(maxtime=max_time, fade_ms=fade_ms)

    @staticmethod
    def play_bgm(name: str):
        if AudioManager.playing_bgm_index != -1:
            AudioManager.bgm_stack[AudioManager.playing_bgm_index][1].stop()
        index = [name for name, sound in AudioManager.bgm_stack].index(name)
        sound = AudioManager.bgm_stack[index][1]

        sound.set_volume(AudioManager.__bgm_volume)
        sound.play(-1)
        AudioManager.playing_bgm_index = index

    @staticmethod
    def stop_bgm():
        if AudioManager.playing_bgm_index == -1:
            Log.error("AudioManager.stop_bgm", "No BGM is played yet.")
            return
        AudioManager.bgm_stack[AudioManager.playing_bgm_index][1].stop()

    @staticmethod
    def set_se_volume(value: float):
        """
        Be careful with your ears.
        """
        if value > 1:
            Log.error("AudioManager.set_se_volume", f"invalid value: {value} > 1")
            return
        AudioManager.__se_volume = value

    @staticmethod
    def set_bgm_volume(value: float):
        """
        Be careful with your ears.
        """
        if value > 1:
            Log.error("AudioManager.set_bgm_volume", f"invalid value: {value} > 1")
            return
        AudioManager.__bgm_volume = value