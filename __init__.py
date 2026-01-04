"""
工具函数模块
"""
from .animation_utils import WindowAnimator, AnimatedTransition
from .animation_config import (
    ANIMATION_DURATION, 
    ANIMATION_PRESETS, 
    EASING_CURVES,
    DEFAULT_ANIMATION,
    get_animation_preset,
    get_duration,
    ANIMATION_COMBINATIONS,
    get_animation_combination
)

__all__ = [
    'WindowAnimator', 
    'AnimatedTransition',
    'ANIMATION_DURATION', 
    'ANIMATION_PRESETS', 
    'EASING_CURVES',
    'DEFAULT_ANIMATION',
    'get_animation_preset',
    'get_duration',
    'ANIMATION_COMBINATIONS',
    'get_animation_combination'
]



