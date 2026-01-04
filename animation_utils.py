"""
动画工具类 - 提供丝滑的窗口切换动画效果
"""
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QTimer, QParallelAnimationGroup, QRect
from PySide6.QtWidgets import QWidget


class WindowAnimator:
    """窗口动画器 - 提供淡入淡出、滑动等动画效果"""
    
    @staticmethod
    def fade_in(widget, duration=300, callback=None):
        """
        淡入动画 - 使用缩放模拟淡入效果
        
        Args:
            widget: 要动画的控件
            duration: 动画持续时间（毫秒）
            callback: 动画完成后的回调函数
        """
        # 保存原始几何形状
        original_rect = widget.geometry()
        center_x = original_rect.x() + original_rect.width() // 2
        center_y = original_rect.y() + original_rect.height() // 2
        
        # 从中心点开始的小矩形
        start_rect = QRect(
            center_x - 10,
            center_y - 10,
            20, 20
        )
        
        # 创建缩放动画
        fade_animation = QPropertyAnimation(widget, b"geometry")
        fade_animation.setDuration(duration)
        fade_animation.setStartValue(start_rect)
        fade_animation.setEndValue(original_rect)
        fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 连接完成信号
        if callback:
            fade_animation.finished.connect(callback)
        
        # 设置初始位置并显示控件
        widget.setGeometry(start_rect)
        widget.show()
        fade_animation.start()
        
        return fade_animation
    
    @staticmethod
    def fade_out(widget, duration=300, callback=None):
        """
        淡出动画 - 使用缩放模拟淡出效果
        
        Args:
            widget: 要动画的控件
            duration: 动画持续时间（毫秒）
            callback: 动画完成后的回调函数
        """
        # 如果控件已经隐藏，直接执行回调
        if not widget.isVisible():
            if callback:
                callback()
            return None
        
        # 获取当前几何形状
        current_rect = widget.geometry()
        center_x = current_rect.x() + current_rect.width() // 2
        center_y = current_rect.y() + current_rect.height() // 2
        
        # 缩小到中心点
        end_rect = QRect(
            center_x - 5,
            center_y - 5,
            10, 10
        )
        
        # 创建缩放动画
        fade_animation = QPropertyAnimation(widget, b"geometry")
        fade_animation.setDuration(duration)
        fade_animation.setStartValue(current_rect)
        fade_animation.setEndValue(end_rect)
        fade_animation.setEasingCurve(QEasingCurve.InCubic)
        
        # 连接完成信号
        if callback:
            fade_animation.finished.connect(callback)
        
        # 开始动画
        fade_animation.start()
        
        return fade_animation
    
    @staticmethod
    def slide_in_from_right(widget, duration=400, callback=None):
        """
        从右侧滑入动画
        
        Args:
            widget: 要动画的控件
            duration: 动画持续时间（毫秒）
            callback: 动画完成后的回调函数
        """
        parent = widget.parent()
        if parent:
            parent_rect = parent.rect()
            # 获取控件的目标位置（当前位置）
            target_rect = widget.geometry()
            # 从右侧开始滑入
            start_rect = QRect(parent_rect.width(), target_rect.y(), target_rect.width(), target_rect.height())
        else:
            target_rect = widget.geometry()
            start_rect = QRect(widget.width(), target_rect.y(), target_rect.width(), target_rect.height())
        
        # 创建几何动画
        geometry_animation = QPropertyAnimation(widget, b"geometry")
        geometry_animation.setDuration(duration)
        geometry_animation.setStartValue(start_rect)
        geometry_animation.setEndValue(target_rect)
        geometry_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 连接完成信号
        if callback:
            geometry_animation.finished.connect(callback)
        
        # 设置初始位置并显示控件
        widget.setGeometry(start_rect)
        widget.show()
        geometry_animation.start()
        
        return geometry_animation
    
    @staticmethod
    def slide_out_to_right(widget, duration=400, callback=None):
        """
        向右侧滑出动画
        
        Args:
            widget: 要动画的控件
            duration: 动画持续时间（毫秒）
            callback: 动画完成后的回调函数
        """
        parent = widget.parent()
        if parent:
            parent_rect = parent.rect()
            # 获取控件的当前位置
            current_rect = widget.geometry()
            # 滑出到右侧
            end_rect = QRect(parent_rect.width(), current_rect.y(), current_rect.width(), current_rect.height())
        else:
            current_rect = widget.geometry()
            end_rect = QRect(widget.width(), current_rect.y(), current_rect.width(), current_rect.height())
        
        # 创建几何动画
        geometry_animation = QPropertyAnimation(widget, b"geometry")
        geometry_animation.setDuration(duration)
        geometry_animation.setStartValue(current_rect)
        geometry_animation.setEndValue(end_rect)
        geometry_animation.setEasingCurve(QEasingCurve.InCubic)
        
        # 连接完成信号
        if callback:
            geometry_animation.finished.connect(callback)
        
        # 开始动画
        geometry_animation.start()
        
        return geometry_animation
    
    @staticmethod
    def slide_in_from_bottom(widget, duration=400, callback=None):
        """
        从底部滑入动画
        
        Args:
            widget: 要动画的控件
            duration: 动画持续时间（毫秒）
            callback: 动画完成后的回调函数
        """
        parent = widget.parent()
        if parent:
            parent_rect = parent.rect()
            # 获取控件的目标位置（当前位置）
            target_rect = widget.geometry()
            # 从底部开始滑入
            start_rect = QRect(target_rect.x(), parent_rect.height(), target_rect.width(), target_rect.height())
        else:
            target_rect = widget.geometry()
            start_rect = QRect(target_rect.x(), widget.height(), target_rect.width(), target_rect.height())
        
        # 创建几何动画
        geometry_animation = QPropertyAnimation(widget, b"geometry")
        geometry_animation.setDuration(duration)
        geometry_animation.setStartValue(start_rect)
        geometry_animation.setEndValue(target_rect)
        geometry_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 连接完成信号
        if callback:
            geometry_animation.finished.connect(callback)
        
        # 设置初始位置并显示控件
        widget.setGeometry(start_rect)
        widget.show()
        geometry_animation.start()
        
        return geometry_animation
    
    @staticmethod
    def slide_out_to_bottom(widget, duration=400, callback=None):
        """
        向底部滑出动画
        
        Args:
            widget: 要动画的控件
            duration: 动画持续时间（毫秒）
            callback: 动画完成后的回调函数
        """
        parent = widget.parent()
        if parent:
            parent_rect = parent.rect()
            # 获取控件的当前位置
            current_rect = widget.geometry()
            # 滑出到底部
            end_rect = QRect(current_rect.x(), parent_rect.height(), current_rect.width(), current_rect.height())
        else:
            current_rect = widget.geometry()
            end_rect = QRect(current_rect.x(), widget.height(), current_rect.width(), current_rect.height())
        
        # 创建几何动画
        geometry_animation = QPropertyAnimation(widget, b"geometry")
        geometry_animation.setDuration(duration)
        geometry_animation.setStartValue(current_rect)
        geometry_animation.setEndValue(end_rect)
        geometry_animation.setEasingCurve(QEasingCurve.InCubic)
        
        # 连接完成信号
        if callback:
            geometry_animation.finished.connect(callback)
        
        # 开始动画
        geometry_animation.start()
        
        return geometry_animation
    
    @staticmethod
    def scale_in(widget, duration=300, callback=None):
        """
        缩放进入动画
        
        Args:
            widget: 要动画的控件
            duration: 动画持续时间（毫秒）
            callback: 动画完成后的回调函数
        """
        # 获取目标几何形状
        current_rect = widget.geometry()
        center_x = current_rect.x() + current_rect.width() // 2
        center_y = current_rect.y() + current_rect.height() // 2
        
        # 从极小的点开始
        start_rect = QRect(
            center_x - 1,
            center_y - 1,
            2, 2
        )
        
        # 创建缩放动画
        scale_animation = QPropertyAnimation(widget, b"geometry")
        scale_animation.setDuration(duration)
        scale_animation.setStartValue(start_rect)
        scale_animation.setEndValue(current_rect)
        scale_animation.setEasingCurve(QEasingCurve.OutElastic)
        
        # 连接完成信号
        if callback:
            scale_animation.finished.connect(callback)
        
        # 设置初始状态并显示控件
        widget.setGeometry(start_rect)
        widget.show()
        scale_animation.start()
        
        return scale_animation
    
    @staticmethod
    def scale_out(widget, duration=300, callback=None):
        """
        缩放退出动画
        
        Args:
            widget: 要动画的控件
            duration: 动画持续时间（毫秒）
            callback: 动画完成后的回调函数
        """
        # 获取当前几何形状
        current_rect = widget.geometry()
        center_x = current_rect.x() + current_rect.width() // 2
        center_y = current_rect.y() + current_rect.height() // 2
        
        # 缩小到极小的点
        end_rect = QRect(
            center_x - 1,
            center_y - 1,
            2, 2
        )
        
        # 创建缩放动画
        scale_animation = QPropertyAnimation(widget, b"geometry")
        scale_animation.setDuration(duration)
        scale_animation.setStartValue(current_rect)
        scale_animation.setEndValue(end_rect)
        scale_animation.setEasingCurve(QEasingCurve.InElastic)
        
        # 连接完成信号
        if callback:
            scale_animation.finished.connect(callback)
        
        # 开始动画
        scale_animation.start()
        
        return scale_animation


class AnimatedTransition:
    """动画过渡管理器 - 管理窗口之间的平滑过渡"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.current_animation = None
        
    def transition_to(self, new_widget, animation_type="fade_in", duration=300, callback=None):
        """
        过渡到新窗口
        
        Args:
            new_widget: 要显示的新窗口
            animation_type: 动画类型 ("fade_in", "slide_in_from_right", "slide_in_from_bottom", "scale_in")
            duration: 动画持续时间
            callback: 完成回调
        """
        # 停止当前动画
        if self.current_animation:
            self.current_animation.stop()
        
        # 根据动画类型选择动画
        if animation_type == "fade_in":
            self.current_animation = WindowAnimator.fade_in(new_widget, duration, callback)
        elif animation_type == "slide_in_from_right":
            self.current_animation = WindowAnimator.slide_in_from_right(new_widget, duration, callback)
        elif animation_type == "slide_in_from_bottom":
            self.current_animation = WindowAnimator.slide_in_from_bottom(new_widget, duration, callback)
        elif animation_type == "scale_in":
            self.current_animation = WindowAnimator.scale_in(new_widget, duration, callback)
        else:
            # 默认淡入
            self.current_animation = WindowAnimator.fade_in(new_widget, duration, callback)
        
        return self.current_animation
    
    def hide_current(self, current_widget, animation_type="fade_out", duration=300, callback=None):
        """
        隐藏当前窗口
        
        Args:
            current_widget: 要隐藏的当前窗口
            animation_type: 动画类型 ("fade_out", "slide_out_to_right", "slide_out_to_bottom", "scale_out")
            duration: 动画持续时间
            callback: 完成回调
        """
        # 根据动画类型选择动画
        if animation_type == "fade_out":
            return WindowAnimator.fade_out(current_widget, duration, callback)
        elif animation_type == "slide_out_to_right":
            return WindowAnimator.slide_out_to_right(current_widget, duration, callback)
        elif animation_type == "slide_out_to_bottom":
            return WindowAnimator.slide_out_to_bottom(current_widget, duration, callback)
        elif animation_type == "scale_out":
            return WindowAnimator.scale_out(current_widget, duration, callback)
        else:
            # 默认淡出
            return WindowAnimator.fade_out(current_widget, duration, callback)
