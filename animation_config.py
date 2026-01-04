"""
动画配置文件 - 统一管理动画参数和预设
"""

# 动画持续时间配置（毫秒）
ANIMATION_DURATION = {
    "fast": 200,      # 快速动画
    "normal": 300,    # 正常速度
    "slow": 400,      # 慢速动画
    "very_slow": 500  # 很慢的动画
}

# 动画类型预设
ANIMATION_PRESETS = {
    # 窗口显示动画
    "window_show": {
        "import_panel": {
            "type": "fade_in",
            "duration": ANIMATION_DURATION["normal"]
        },
        "settings_panel": {
            "type": "scale_in", 
            "duration": ANIMATION_DURATION["slow"]
        },
        "dialog_panel": {
            "type": "slide_in_from_bottom",
            "duration": ANIMATION_DURATION["normal"]
        },
        "selection_panel": {
            "type": "slide_in_from_right",
            "duration": ANIMATION_DURATION["normal"]
        }
    },
    
    # 窗口隐藏动画
    "window_hide": {
        "import_panel": {
            "type": "fade_out",
            "duration": ANIMATION_DURATION["normal"]
        },
        "settings_panel": {
            "type": "scale_out",
            "duration": ANIMATION_DURATION["normal"]
        },
        "dialog_panel": {
            "type": "slide_out_to_bottom",
            "duration": ANIMATION_DURATION["fast"]
        },
        "selection_panel": {
            "type": "slide_out_to_right",
            "duration": ANIMATION_DURATION["fast"]
        }
    },
    
    # 特殊效果动画
    "special_effects": {
        "notification": {
            "type": "slide_in_from_right",
            "duration": ANIMATION_DURATION["fast"]
        },
        "tooltip": {
            "type": "fade_in",
            "duration": ANIMATION_DURATION["fast"]
        },
        "loading": {
            "type": "scale_in",
            "duration": ANIMATION_DURATION["slow"]
        }
    }
}

# 缓动曲线配置
EASING_CURVES = {
    "linear": "Linear",
    "in_quad": "InQuad", 
    "out_quad": "OutQuad",
    "in_out_quad": "InOutQuad",
    "in_cubic": "InCubic",
    "out_cubic": "OutCubic",  # 常用，自然的加速
    "in_out_cubic": "InOutCubic",
    "in_quart": "InQuart",
    "out_quart": "OutQuart",
    "in_out_quart": "InOutQuart",
    "in_elastic": "InElastic",
    "out_elastic": "OutElastic",  # 弹性效果
    "in_out_elastic": "InOutElastic",
    "in_back": "InBack",
    "out_back": "OutBack",  # 回弹效果
    "in_out_back": "InOutBack",
    "in_bounce": "InBounce",
    "out_bounce": "OutBounce",  # 弹跳效果
    "in_out_bounce": "InOutBounce"
}

# 默认动画配置
DEFAULT_ANIMATION = {
    "show_type": "fade_in",
    "hide_type": "fade_out", 
    "duration": ANIMATION_DURATION["normal"],
    "easing": EASING_CURVES["out_cubic"]
}

def get_animation_preset(preset_name, panel_type):
    """
    获取动画预设配置
    
    Args:
        preset_name: 预设名称 ("window_show", "window_hide", "special_effects")
        panel_type: 面板类型 ("import_panel", "settings_panel", "dialog_panel", etc.)
    
    Returns:
        dict: 动画配置字典
    """
    try:
        return ANIMATION_PRESETS[preset_name][panel_type]
    except KeyError:
        # 如果没有找到预设，返回默认配置
        return DEFAULT_ANIMATION.copy()

def get_duration(speed_name):
    """
    获取动画持续时间
    
    Args:
        speed_name: 速度名称 ("fast", "normal", "slow", "very_slow")
    
    Returns:
        int: 持续时间（毫秒）
    """
    return ANIMATION_DURATION.get(speed_name, DEFAULT_ANIMATION["duration"])

# 动画组合配置
ANIMATION_COMBINATIONS = {
    # 对话框动画组合
    "dialog": {
        "show": {"type": "scale_in", "duration": 300},
        "hide": {"type": "scale_out", "duration": 250}
    },
    
    # 侧边栏动画组合
    "sidebar": {
        "show": {"type": "slide_in_from_right", "duration": 400},
        "hide": {"type": "slide_out_to_right", "duration": 300}
    },
    
    # 模态窗口动画组合
    "modal": {
        "show": {"type": "fade_in", "duration": 400},
        "hide": {"type": "fade_out", "duration": 300}
    },
    
    # 通知动画组合
    "notification": {
        "show": {"type": "slide_in_from_right", "duration": 200},
        "hide": {"type": "slide_out_to_right", "duration": 200}
    }
}

def get_animation_combination(combination_name, action):
    """
    获取动画组合配置
    
    Args:
        combination_name: 组合名称 ("dialog", "sidebar", "modal", "notification")
        action: 动作 ("show", "hide")
    
    Returns:
        dict: 动画配置字典
    """
    try:
        return ANIMATION_COMBINATIONS[combination_name][action]
    except KeyError:
        return DEFAULT_ANIMATION.copy()
