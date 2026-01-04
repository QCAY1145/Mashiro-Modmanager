"""
面板组件模块
包含批量禁用面板、二分选择面板、高级设置面板、冲突处理面板、标签管理面板
"""
import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QCheckBox, QFileDialog, QFormLayout, QDialog, QScrollArea, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt, QMimeData, QPoint
from PySide6.QtGui import QDrag, QPainter, QColor, QIcon, QPixmap


def _get_project_root():
    """获取项目根目录"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 从models目录返回到项目根目录
    return os.path.dirname(current_dir)


class BinaryDisablePanel(QWidget):
    """批量禁用面板"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 300)
        self.saved_enabled_mods = []
        self.current_enabled_mods = []
        self.result = 0
        self.drag_position = None
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 182, 193, 120);
                border: 2px solid #8B4513;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        self.setLayout(layout)
        
        self.btn_all_disable = QPushButton("全部禁用")
        self.btn_binary_disable = QPushButton("二分禁用")
        self.btn_cancel = QPushButton("取消")
        
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """
        
        self.btn_all_disable.setStyleSheet(button_style)
        self.btn_binary_disable.setStyleSheet(button_style)
        self.btn_cancel.setStyleSheet(button_style)
        
        self.btn_all_disable.clicked.connect(self.accept_all_disable)
        self.btn_binary_disable.clicked.connect(self.accept_binary_disable)
        self.btn_cancel.clicked.connect(self.accept_cancel)
        
        layout.addWidget(self.btn_all_disable)
        layout.addWidget(self.btn_binary_disable)
        layout.addWidget(self.btn_cancel)
        
        self.apply_background()
        
        self.setMouseTracking(True)
        self.mousePressEvent = self.mouse_press_event
        self.mouseMoveEvent = self.mouse_move_event
    
    def mouse_press_event(self, event):
        """鼠标按下事件，用于拖动窗口"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouse_move_event(self, event):
        """鼠标移动事件，用于拖动窗口"""
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
    
    def apply_background(self):
        """应用背景图片"""
        project_root = _get_project_root()
        background_image = os.path.join(project_root, "background", "BinaryDisablePanel.png")
        
        if os.path.exists(background_image):
            background_url = background_image.replace("\\", "/")
            panel_style = f"""
                QWidget {{
                    background-image: url('{background_url}');
                    background-position: center;
                    background-repeat: no-repeat;
                    background-size: cover;
                    background-attachment: fixed;
                    border: 2px solid #8B4513;
                    border-radius: 8px;
                }}
            """
            self.setStyleSheet(panel_style)
    
    def accept_all_disable(self):
        """全部禁用"""
        self.result = 1
        self.hide()
        if hasattr(self, '_exec_loop'):
            self._exec_loop.quit()
    
    def accept_binary_disable(self):
        """二分禁用"""
        self.result = 2
        self.hide()
        if hasattr(self, '_exec_loop'):
            self._exec_loop.quit()
    
    def accept_cancel(self):
        """取消"""
        self.result = 0
        self.hide()
        if hasattr(self, '_exec_loop'):
            self._exec_loop.quit()
    
    def exec(self):
        """执行对话框，返回选择结果"""
        from PySide6.QtCore import QEventLoop
        self._exec_loop = QEventLoop()
        self._exec_loop.exec()
        return self.result


class BinarySelectionPanel(QWidget):
    """二分选择面板"""
    def __init__(self, mod_list, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 250)  # 调整大小，因为没有列表了
        self.mod_list = mod_list
        self.selected_mods = []
        self.result = 0  # 结果值
        self.drag_position = None  # 拖动位置
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        # 设置面板样式 - 整体浅粉色背景，圆角边框
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 182, 193, 120);
                border: 2px solid #8B4513;
                border-radius: 8px;
            }
        """)
        
        # 垂直布局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        self.setLayout(layout)
        
        # 三个按钮
        self.btn_front_half = QPushButton("禁用前半部分")
        self.btn_back_half = QPushButton("禁用后半部分")
        self.btn_cancel_binary = QPushButton("取消二分")
        
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """
        
        self.btn_front_half.setStyleSheet(button_style)
        self.btn_back_half.setStyleSheet(button_style)
        self.btn_cancel_binary.setStyleSheet(button_style)
        
        # 设置按钮固定大小
        for btn in [self.btn_front_half, self.btn_back_half, self.btn_cancel_binary]:
            btn.setFixedHeight(45)
        
        # 注意：按钮事件由主窗口连接，不在这里连接
        
        # 添加到布局
        layout.addWidget(self.btn_front_half)
        layout.addWidget(self.btn_back_half)
        layout.addWidget(self.btn_cancel_binary)
        
        # 设置背景
        self.apply_background()
        
        # 启用鼠标跟踪以支持拖动
        self.setMouseTracking(True)
        self.mousePressEvent = self.mouse_press_event
        self.mouseMoveEvent = self.mouse_move_event
    
    def mouse_press_event(self, event):
        """鼠标按下事件，用于拖动窗口"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouse_move_event(self, event):
        """鼠标移动事件，用于拖动窗口"""
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
    
    def apply_background(self):
        """应用背景图片"""
        project_root = _get_project_root()
        background_image = os.path.join(project_root, "background", "BinarySelectionPanel.png")
        
        if os.path.exists(background_image):
            background_url = background_image.replace("\\", "/")
            panel_style = f"""
                QWidget {{
                    background-image: url('{background_url}');
                    background-position: center;
                    background-repeat: no-repeat;
                    background-size: cover;
                    background-attachment: fixed;
                    border: 2px solid #8B4513;
                    border-radius: 8px;
                }}
            """
            self.setStyleSheet(panel_style)
    
    def select_front_half(self):
        """选择前半部分"""
        half_count = len(self.mod_list) // 2
        self.selected_mods = self.mod_list[:half_count]
        self.result = 1  # 返回1表示选择前半部分
        self.hide()
    
    def select_back_half(self):
        """选择后半部分"""
        half_count = len(self.mod_list) // 2
        self.selected_mods = self.mod_list[half_count:]
        self.result = 2  # 返回2表示选择后半部分
        self.hide()
    
    def reject(self):
        """取消"""
        self.result = 0  # 返回0表示取消
        self.hide()
    
    def get_selected_mods(self):
        """获取选中的Mod"""
        return getattr(self, 'selected_mods', [])


class AdminPermissionPanel(QWidget):
    """管理员权限提示面板"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result = 0
        self.drag_position = None
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setFixedSize(450, 250)
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 182, 193, 120);
                border: 2px solid #8B4513;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        self.setLayout(layout)
        
        title_label = QLabel("需要管理员权限")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #8B4513;
            }
        """)
        layout.addWidget(title_label)
        
        message_label = QLabel(
            "虚拟映射功能需要管理员权限才能创建符号链接。\n\n"
            "请以管理员身份运行程序，或启用Windows开发者模式。"
        )
        message_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #8B4513;
            }
        """)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        self.btn_ok = QPushButton("确定")
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """
        self.btn_ok.setStyleSheet(button_style)
        self.btn_ok.clicked.connect(self.accept_ok)
        layout.addWidget(self.btn_ok)
        
        self.apply_background()
        
        self.setMouseTracking(True)
        self.mousePressEvent = self.mouse_press_event
        self.mouseMoveEvent = self.mouse_move_event
    
    def mouse_press_event(self, event):
        """鼠标按下事件，用于拖动窗口"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouse_move_event(self, event):
        """鼠标移动事件，用于拖动窗口"""
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
    
    def apply_background(self):
        """应用背景图片"""
        project_root = _get_project_root()
        background_image = os.path.join(project_root, "background", "AdminPermissionPanel.png")
        
        if os.path.exists(background_image):
            background_url = background_image.replace("\\", "/")
            panel_style = f"""
                QWidget {{
                    background-image: url('{background_url}');
                    background-position: center;
                    background-repeat: no-repeat;
                    background-size: cover;
                    background-attachment: fixed;
                    border: 2px solid #8B4513;
                    border-radius: 8px;
                }}
            """
            self.setStyleSheet(panel_style)
    
    def accept_ok(self):
        """确定"""
        self.result = 1
        self.hide()
        if hasattr(self, '_exec_loop'):
            self._exec_loop.quit()
    
    def exec(self):
        """执行对话框，返回选择结果"""
        from PySide6.QtCore import QEventLoop
        self._exec_loop = QEventLoop()
        self._exec_loop.exec()
        return self.result


class BatchImportPanel(QWidget):
    """批量导入面板"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result = 0  # 0=取消, 1=从狩技盒子导入, 2=从导出mods导入
        self.drag_position = None
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setFixedSize(400, 250)
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 182, 193, 120);
                border: 2px solid #8B4513;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        self.setLayout(layout)
        
        self.btn_hunt_box = QPushButton("从狩技盒子导入")
        self.btn_export_mods = QPushButton("从导出mods导入")
        self.btn_cancel = QPushButton("取消")
        
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """
        
        self.btn_hunt_box.setStyleSheet(button_style)
        self.btn_export_mods.setStyleSheet(button_style)
        self.btn_cancel.setStyleSheet(button_style)
        
        # 设置按钮固定大小
        for btn in [self.btn_hunt_box, self.btn_export_mods, self.btn_cancel]:
            btn.setFixedHeight(45)
        
        # 注意：按钮事件由主窗口连接，不在这里连接
        
        layout.addWidget(self.btn_hunt_box)
        layout.addWidget(self.btn_export_mods)
        layout.addWidget(self.btn_cancel)
        
        # 延迟应用背景，等待主题设置传入
        self._theme_settings = None
        
        self.setMouseTracking(True)
        self.mousePressEvent = self.mouse_press_event
        self.mouseMoveEvent = self.mouse_move_event
    
    def mouse_press_event(self, event):
        """鼠标按下事件，用于拖动窗口"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouse_move_event(self, event):
        """鼠标移动事件，用于拖动窗口"""
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
    
    def apply_background(self, theme_settings=None):
        """应用背景图片和主题设置"""
        # 获取主题设置（如果提供）
        if theme_settings:
            primary_color = theme_settings.get('primary_color', '#FFC0CB')
            background_opacity = theme_settings.get('background_opacity', 120)
        else:
            primary_color = '#FFC0CB'
            background_opacity = 120
        
        # 将颜色转换为RGB，并应用透明度
        try:
            from PySide6.QtGui import QColor
            color = QColor(primary_color)
            r, g, b = color.red(), color.green(), color.blue()
        except:
            r, g, b = 255, 182, 193  # 默认粉色
        
        project_root = _get_project_root()
        background_image = os.path.join(project_root, "background", "BatchImportPanel.png")
        
        if os.path.exists(background_image):
            background_url = background_image.replace("\\", "/")
            panel_style = f"""
                QWidget {{
                    background-color: rgba({r}, {g}, {b}, {background_opacity});
                    background-image: url('{background_url}');
                    background-position: center;
                    background-repeat: no-repeat;
                    border: 2px solid #8B4513;
                    border-radius: 8px;
                }}
            """
            self.setStyleSheet(panel_style)
        else:
            # 如果没有背景图，只应用颜色和透明度
            panel_style = f"""
                QWidget {{
                    background-color: rgba({r}, {g}, {b}, {background_opacity});
                    border: 2px solid #8B4513;
                    border-radius: 8px;
                }}
            """
            self.setStyleSheet(panel_style)
    
    def accept_hunt_box(self):
        """从狩技盒子导入"""
        self.result = 1  # 返回1表示从狩技盒子导入
        self.hide()
    
    def accept_export_mods(self):
        """从导出mods导入"""
        self.result = 2  # 返回2表示从导出mods导入
        self.hide()
    
    def reject(self):
        """取消"""
        self.result = 0  # 返回0表示取消
        self.hide()


class UnknownCategoryAuthorPanel(QDialog):
    """未知标签/作者询问面板 - 使用系统自带对话框"""
    def __init__(self, item_name, item_type, parent=None):
        """
        Args:
            item_name: str, 未知的标签或作者名称（单个）
            item_type: str, "标签" 或 "作者"
            parent: 父窗口
        """
        super().__init__(parent)
        self.item_name = item_name
        self.item_type = item_type
        self.result = 0  # 0=取消, 1=保存, 2=忽略
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle(f"检测到未知的{self.item_type}")
        self.setMinimumSize(350, 120)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # 一行提示文字
        hint_text = f"检测到未知{self.item_type}：{self.item_name}，是否保留？"
        hint_label = QLabel(hint_text)
        layout.addWidget(hint_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        
        self.btn_save = QPushButton("保存")
        self.btn_ignore = QPushButton("忽略")
        
        self.btn_save.clicked.connect(self.accept_save)
        self.btn_ignore.clicked.connect(self.accept_ignore)
        
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_ignore)
        layout.addLayout(button_layout)
    
    def accept_save(self):
        """保存未知项"""
        self.result = 1
        self.accept()
    
    def accept_ignore(self):
        """忽略未知项（置空）"""
        self.result = 2
        self.accept()
    
    def exec(self):
        """执行对话框，返回选择结果"""
        super().exec()
        return self.result


class ConflictResolutionPanel(QDialog):
    """冲突处理面板 - 第一个界面"""
    def __init__(self, current_mod, conflicting_mods, parent=None):
        """
        Args:
            current_mod: str, 当前要启用的mod名称
            conflicting_mods: list of str, 发生冲突的mod列表
            parent: 父窗口
        """
        super().__init__(parent)
        self.current_mod = current_mod
        self.conflicting_mods = conflicting_mods
        self.result = 0  # 0=取消启用, 1=直接覆盖, 2=手动修改
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("检测到文件冲突")
        
        # 设置窗口图标
        project_root = _get_project_root()
        icon_path = os.path.join(project_root, "background", "title.png")
        if os.path.exists(icon_path):
            try:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    icon = QIcon(pixmap)
                    self.setWindowIcon(icon)
            except Exception as e:
                print(f"[警告] 设置窗口图标失败: {e}")
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # 显示冲突信息
        conflict_text = f"模组 '{self.current_mod}' 与以下模组发生文件冲突：\n\n"
        for mod in self.conflicting_mods:
            conflict_text += f"  • {mod}\n"
        
        conflict_label = QLabel(conflict_text)
        conflict_label.setWordWrap(True)
        layout.addWidget(conflict_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        
        self.btn_cancel = QPushButton("取消启用")
        self.btn_override = QPushButton("直接覆盖")
        self.btn_manual = QPushButton("手动修改")
        
        # 设置直接覆盖按钮的提示
        self.btn_override.setToolTip("直接覆盖可能导致严重错误，请谨慎使用！")
        
        self.btn_cancel.clicked.connect(self.accept_cancel)
        self.btn_override.clicked.connect(self.accept_override)
        self.btn_manual.clicked.connect(self.accept_manual)
        
        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_override)
        button_layout.addWidget(self.btn_manual)
        layout.addLayout(button_layout)
        
        # 根据内容调整大小（移除固定大小，让窗口自适应内容）
        self.setMinimumWidth(400)  # 设置最小宽度，避免太窄
        self.adjustSize()  # 根据内容调整大小
    
    def accept_cancel(self):
        """取消启用"""
        self.result = 0
        self.accept()
    
    def accept_override(self):
        """直接覆盖"""
        self.result = 1
        self.accept()
    
    def accept_manual(self):
        """手动修改"""
        self.result = 2
        self.accept()
    
    def exec(self):
        """执行对话框，返回选择结果"""
        super().exec()
        return self.result


class PriorityItemWidget(QWidget):
    """优先级调整项（使用按钮上移/下移）"""
    def __init__(self, mod_name, index, parent=None):
        super().__init__(parent)
        self.mod_name = mod_name
        self.index = index
        self.parent_panel = parent
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        # 高度：三行文字大小（14px * 3 + padding ≈ 50px）
        self.setFixedHeight(50)
        # 宽度：15个字的宽度（14px * 15 + padding + 按钮 ≈ 280px）
        self.setFixedWidth(280)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 200);
                border: 2px solid #8B4513;
                border-radius: 4px;
            }
        """)
    
        layout = QHBoxLayout()
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(6)
        
        # Mod名称标签（限制宽度，支持文本截断，居中显示）
        name_label = QLabel(self.mod_name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 文字居中
        name_label.setStyleSheet("""
            QLabel {
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        # 设置文本截断
        name_label.setWordWrap(False)
        # 如果文本太长，截断并显示省略号
        from PySide6.QtGui import QFontMetrics
        font_metrics = QFontMetrics(name_label.font())
        max_width = 200  # 约15个字的宽度减去按钮和间距
        elided_text = font_metrics.elidedText(self.mod_name, Qt.TextElideMode.ElideRight, max_width)
        name_label.setText(elided_text)
        name_label.setToolTip(self.mod_name)  # 完整名称作为提示
        
        layout.addWidget(name_label, stretch=1)
        
        # 上移按钮
        btn_up = QPushButton("↑")
        btn_up.setFixedSize(25, 25)
        btn_up.setToolTip("上移（提高优先级）")
        btn_up.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 3px;
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(157, 0, 255, 200);
                color: white;
            }
            QPushButton:disabled {
                background-color: rgba(200, 200, 200, 200);
                color: #999999;
            }
        """)
        btn_up.clicked.connect(lambda: self.move_up())
        layout.addWidget(btn_up)
        
        # 下移按钮
        btn_down = QPushButton("↓")
        btn_down.setFixedSize(25, 25)
        btn_down.setToolTip("下移（降低优先级）")
        btn_down.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 3px;
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(157, 0, 255, 200);
                color: white;
            }
            QPushButton:disabled {
                background-color: rgba(200, 200, 200, 200);
                color: #999999;
            }
        """)
        btn_down.clicked.connect(lambda: self.move_down())
        layout.addWidget(btn_down)
        
        self.btn_up = btn_up
        self.btn_down = btn_down
        
        self.setLayout(layout)
        self.update_button_states()
    
    def update_index(self, new_index):
        """更新索引"""
        self.index = new_index
        self.update_button_states()
    
    def update_button_states(self):
        """更新按钮状态"""
        if self.parent_panel:
            total_items = len(self.parent_panel.sliders)
            # 第一个不能上移
            self.btn_up.setEnabled(self.index > 0)
            # 最后一个不能下移
            self.btn_down.setEnabled(self.index < total_items - 1)
    
    def move_up(self):
        """上移"""
        if self.parent_panel and self.index > 0:
            self.parent_panel.move_item(self, -1)
    
    def move_down(self):
        """下移"""
        if self.parent_panel and self.index < len(self.parent_panel.sliders) - 1:
            self.parent_panel.move_item(self, 1)


class PriorityAdjustmentPanel(QDialog):
    """手动修改优先级面板 - 使用上移/下移按钮调整优先级"""
    def __init__(self, conflicting_mods, parent=None):
        """
        Args:
            conflicting_mods: list of str, 发生冲突的mod列表（包括当前要启用的mod）
            parent: 父窗口
        """
        super().__init__(parent)
        self.conflicting_mods = conflicting_mods.copy()
        self.sliders = []
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("调整冲突模组优先级")
        self.setMinimumSize(320, 400)
        self.resize(320, 400)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        
        # 提示文字
        hint_label = QLabel("使用 ↑ ↓ 按钮调整优先级顺序（数字越小优先级越高，优先映射）")
        hint_label.setWordWrap(True)
        hint_label.setStyleSheet("""
            QLabel {
                color: #8B4513;
                font-size: 12px;
                padding: 6px;
                background-color: rgba(255, 255, 255, 150);
                border-radius: 4px;
            }
        """)
        layout.addWidget(hint_label)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #8B4513;
                border-radius: 4px;
                background-color: rgba(255, 255, 255, 100);
            }
        """)
        
        # 项目容器
        self.item_container = QWidget()
        self.item_layout = QVBoxLayout()
        self.item_layout.setSpacing(4)
        self.item_layout.setContentsMargins(5, 5, 5, 5)
        self.item_container.setLayout(self.item_layout)
        
        # 创建优先级调整项
        for i, mod_name in enumerate(self.conflicting_mods):
            item = PriorityItemWidget(mod_name, i, self)
            self.sliders.append(item)
            self.item_layout.addWidget(item)
        
        scroll_area.setWidget(self.item_container)
        layout.addWidget(scroll_area, stretch=1)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()
        
        self.btn_confirm = QPushButton("确认")
        self.btn_cancel = QPushButton("取消")
        
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 2px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 15px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: rgba(157, 0, 255, 200);
                color: white;
            }
        """
        
        self.btn_confirm.setStyleSheet(button_style)
        self.btn_cancel.setStyleSheet(button_style)
        
        self.btn_confirm.clicked.connect(self.accept_confirm)
        self.btn_cancel.clicked.connect(self.accept_cancel)
        
        button_layout.addWidget(self.btn_confirm)
        button_layout.addWidget(self.btn_cancel)
        layout.addLayout(button_layout)
    
    def move_item(self, item, direction):
        """移动项目（direction: -1 上移, 1 下移）"""
        current_index = self.sliders.index(item)
        new_index = current_index + direction
        
        # 检查边界
        if new_index < 0 or new_index >= len(self.sliders):
            return
        
        # 交换位置
        self.sliders.remove(item)
        self.sliders.insert(new_index, item)
        
        # 更新mod列表顺序
        mod_name = item.mod_name
        self.conflicting_mods.remove(mod_name)
        self.conflicting_mods.insert(new_index, mod_name)
            
            # 更新布局
            for i, s in enumerate(self.sliders):
            s.update_index(i)
        
        # 重新排列布局中的widget
        for i in range(self.item_layout.count()):
            self.item_layout.removeItem(self.item_layout.itemAt(0))
        
            for s in self.sliders:
            self.item_layout.addWidget(s)
    
    def accept_confirm(self):
        """确认"""
        self.result = 1
        self.accept()
    
    def accept_cancel(self):
        """取消"""
        self.result = 0
        self.accept()
    
    def exec(self):
        """执行对话框，返回选择结果和优先级顺序"""
        super().exec()
        return self.result, self.conflicting_mods if self.result == 1 else None


class CategoryManagementPanel(QDialog):
    """标签管理面板 - 数据库表单样式"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.categories = []  # 标签列表
        self.selected_rows = []  # 选中的行（用于交换）
        self.table = None  # 先初始化为None
        self.rename_mapping = {}  # 记录重命名映射 {old_name: new_name}
        self.setup_ui()  # setup_ui会创建table
        self.load_categories()  # 然后加载数据
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("标签管理")
        self.setMinimumSize(500, 400)
        self.resize(500, 500)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["标签名", "删除", "重命名"])
        # 标签名列：自动拉伸占满剩余空间
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # 删除和重命名按钮列：固定宽度，较宽
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 100)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 100)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.MultiSelection)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: rgba(255, 182, 193, 200);
            }
        """)
        layout.addWidget(self.table)
        
        # 底部按钮区域
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        # 添加按钮（右下方）
        self.btn_add = QPushButton("添加")
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 20px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """)
        self.btn_add.clicked.connect(self.add_category)
        bottom_layout.addWidget(self.btn_add)
        
        # 交换按钮（右下方）
        self.btn_swap = QPushButton("交换")
        self.btn_swap.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 20px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
            QPushButton:disabled {
                background-color: rgba(200, 200, 200, 200);
                color: #999999;
            }
        """)
        self.btn_swap.setEnabled(False)
        self.btn_swap.clicked.connect(self.swap_categories)
        bottom_layout.addWidget(self.btn_swap)
        
        # 保存按钮
        self.btn_save = QPushButton("保存")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 20px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """)
        self.btn_save.clicked.connect(self.save_categories)
        bottom_layout.addWidget(self.btn_save)
        
        # 取消按钮
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 20px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        bottom_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(bottom_layout)
        
        # 连接表格选择变化事件
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
    
    def load_categories(self):
        """加载标签列表"""
        project_root = _get_project_root()
        json_dir = os.path.join(project_root, "json")
        os.makedirs(json_dir, exist_ok=True)
        categories_file = os.path.join(json_dir, "categories.json")
        
        self.categories = []
        
        if os.path.exists(categories_file):
            try:
                with open(categories_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        # 确保去重并保持顺序
                        seen = set()
                        self.categories = []
                        for item in data:
                            # 确保item是字符串且不为空
                            item_str = str(item).strip() if item else ""
                            if item_str and item_str not in seen:
                                self.categories.append(item_str)
                                seen.add(item_str)
                    else:
                        # 如果不是列表格式，尝试转换或使用默认值
                        self.categories = ["邦邦"]
            except Exception as e:
                # 读取失败，使用默认值
                self.categories = ["邦邦"]
        else:
            # 文件不存在，使用默认值
            self.categories = ["邦邦"]
        
        # 如果列表为空，确保至少有一个默认标签
        if not self.categories:
            self.categories = ["邦邦"]
        
        # 如果文件不存在或读取失败，保存默认标签到JSON
        if not os.path.exists(categories_file) or not self.categories:
            try:
                with open(categories_file, 'w', encoding='utf-8') as f:
                    json.dump(self.categories, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
        
        self.refresh_table()
    
    def refresh_table(self):
        """刷新表格显示"""
        if self.table is None:
            return
        
        # 清空表格内容
        self.table.setRowCount(0)
        
        # 过滤掉空标签
        valid_categories = []
        for category in self.categories:
            category_str = str(category).strip() if category else ""
            if category_str:
                valid_categories.append(category_str)
        
        # 设置行数
        self.table.setRowCount(len(valid_categories))
        
        for i, category_str in enumerate(valid_categories):
            # 标签名（第0列）
            name_item = QTableWidgetItem(category_str)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, name_item)
            
            # 删除按钮（第1列）
            btn_delete = QPushButton("删除")
            btn_delete.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 200);
                    border: 1px solid #8B4513;
                    border-radius: 4px;
                    color: #8B4513;
                    font-size: 12px;
                    padding: 4px 12px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 100, 100, 200);
                    color: white;
                }
            """)
            btn_delete.clicked.connect(lambda checked, row=i: self.delete_category(row))
            self.table.setCellWidget(i, 1, btn_delete)
            
            # 重命名按钮（第2列）
            btn_rename = QPushButton("重命名")
            btn_rename.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 200);
                    border: 1px solid #8B4513;
                    border-radius: 4px;
                    color: #8B4513;
                    font-size: 12px;
                    padding: 4px 12px;
                }
                QPushButton:hover {
                    background-color: rgba(100, 100, 255, 200);
                    color: white;
                }
            """)
            btn_rename.clicked.connect(lambda checked, row=i: self.rename_category(row))
            self.table.setCellWidget(i, 2, btn_rename)
    
    def add_category(self):
        """添加新标签"""
        text, ok = QInputDialog.getText(self, "添加标签", "请输入标签名称:")
        if ok and text.strip():
            category = text.strip()
            if category in self.categories:
                QMessageBox.warning(self, "提示", "标签已存在")
                return
            self.categories.append(category)
            self.refresh_table()
    
    def delete_category(self, row):
        """删除标签"""
        if row < 0 or row >= len(self.categories):
            return
        
        category = self.categories[row]
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除标签 '{category}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.categories.pop(row)
            self.refresh_table()
    
    def rename_category(self, row):
        """重命名标签"""
        if row < 0 or row >= len(self.categories):
            return
        
        old_name = self.categories[row]
        text, ok = QInputDialog.getText(self, "重命名标签", "请输入新标签名称:", text=old_name)
        if ok and text.strip():
            new_name = text.strip()
            # 检查：不能和原来的一样
            if new_name == old_name:
                QMessageBox.warning(self, "提示", "新标签名称不能和原来的一样")
                return
            # 检查：不能和现有的标签一样
            if new_name in self.categories:
                QMessageBox.warning(self, "提示", "标签已存在，不能使用相同的名称")
                return
            # 记录重命名映射
            self.rename_mapping[old_name] = new_name
            self.categories[row] = new_name
            self.refresh_table()
    
    def on_selection_changed(self):
        """选择变化时更新交换按钮状态"""
        selected_rows = [index.row() for index in self.table.selectionModel().selectedRows()]
        # 检查是否按住了Ctrl键（通过检查是否选择了多个行）
        if len(selected_rows) == 2:
            self.btn_swap.setEnabled(True)
        else:
            self.btn_swap.setEnabled(False)
    
    def swap_categories(self):
        """交换两个标签的位置"""
        selected_rows = [index.row() for index in self.table.selectionModel().selectedRows()]
        if len(selected_rows) != 2:
            QMessageBox.warning(self, "提示", "请按住Ctrl键选择两个标签进行交换")
            return
        
        row1, row2 = sorted(selected_rows)
        # 交换位置
        self.categories[row1], self.categories[row2] = self.categories[row2], self.categories[row1]
        self.refresh_table()
        # 清除选择
        self.table.clearSelection()
    
    def save_categories(self):
        """保存标签列表"""
        project_root = _get_project_root()
        json_dir = os.path.join(project_root, "json")
        os.makedirs(json_dir, exist_ok=True)
        categories_file = os.path.join(json_dir, "categories.json")
        
        try:
            with open(categories_file, 'w', encoding='utf-8') as f:
                json.dump(self.categories, f, ensure_ascii=False, indent=2)
            
            # 如果有重命名映射，更新所有mod的XML文件中的category字段
            if self.rename_mapping:
                self.update_all_mods_xml_categories(self.rename_mapping)
            
            # 通知主窗口刷新
            try:
                parent = self.parent()
                while parent and not hasattr(parent, 'refresh_category_combo'):
                    parent = parent.parent()
                if parent:
                    if hasattr(parent, 'refresh_category_combo'):
                        parent.refresh_category_combo()
                    if hasattr(parent, 'refresh_mod_list'):
                        parent.refresh_mod_list()
            except Exception:
                pass  # 刷新失败不影响保存
            
            QMessageBox.information(self, "成功", "标签已保存")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存标签失败: {e}")
    
    def update_all_mods_xml_categories(self, rename_mapping):
        """更新所有mod的XML文件中的category字段
        
        Args:
            rename_mapping: 重命名映射字典 {old_name: new_name}
        """
        import xml.etree.ElementTree as ET
        
        project_root = _get_project_root()
        mods_dir = os.path.join(project_root, "mods")
        
        if not os.path.exists(mods_dir):
            return
        
        updated_count = 0
        for mod_folder_name in os.listdir(mods_dir):
            mod_folder_path = os.path.join(mods_dir, mod_folder_name)
            if not os.path.isdir(mod_folder_path):
                continue
            
            modinfo_dir = os.path.join(mod_folder_path, "modinfo")
            xml_file_path = os.path.join(modinfo_dir, "modinfo.xml")
            
            if not os.path.exists(xml_file_path):
                continue
            
            try:
                tree = ET.parse(xml_file_path)
                root = tree.getroot()
                
                category_elem = root.find('category')
                if category_elem is not None and category_elem.text:
                    # 支持多分类（分号分隔）
                    categories = [cat.strip() for cat in category_elem.text.split(';')]
                    updated = False
                    
                    # 替换所有匹配的旧标签名
                    new_categories = []
                    for cat in categories:
                        if cat in rename_mapping:
                            new_categories.append(rename_mapping[cat])
                            updated = True
                        else:
                            new_categories.append(cat)
                    
                    if updated:
                        # 更新category字段
                        category_elem.text = ';'.join(new_categories)
                        tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
                        updated_count += 1
            except Exception:
                # 单个mod更新失败不影响其他mod
                continue


class ExportSelectionPanel(QWidget):
    """导出选择面板"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 250)
        self.result = 0  # 0=取消, 1=导出为mod, 2=导出为mods
        self.drag_position = None
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 182, 193, 120);
                border: 2px solid #8B4513;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        self.setLayout(layout)
        
        self.btn_export_as_mod = QPushButton("导出为mod")
        self.btn_export_as_mods = QPushButton("导出为mods")
        self.btn_cancel = QPushButton("取消")
        
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """
        
        self.btn_export_as_mod.setStyleSheet(button_style)
        self.btn_export_as_mods.setStyleSheet(button_style)
        self.btn_cancel.setStyleSheet(button_style)
        
        self.btn_export_as_mod.clicked.connect(self.accept_export_as_mod)
        self.btn_export_as_mods.clicked.connect(self.accept_export_as_mods)
        self.btn_cancel.clicked.connect(self.accept_cancel)
        
        layout.addWidget(self.btn_export_as_mod)
        layout.addWidget(self.btn_export_as_mods)
        layout.addWidget(self.btn_cancel)
        
        self.apply_background()
        
        self.setMouseTracking(True)
        self.mousePressEvent = self.mouse_press_event
        self.mouseMoveEvent = self.mouse_move_event
    
    def mouse_press_event(self, event):
        """鼠标按下事件，用于拖动窗口"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouse_move_event(self, event):
        """鼠标移动事件，用于拖动窗口"""
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
    
    def apply_background(self):
        """应用背景图片"""
        project_root = _get_project_root()
        background_image = os.path.join(project_root, "background", "BinaryDisablePanel.png")
        
        if os.path.exists(background_image):
            background_url = background_image.replace("\\", "/")
            panel_style = f"""
                QWidget {{
                    background-image: url('{background_url}');
                    background-position: center;
                    background-repeat: no-repeat;
                    background-size: cover;
                    background-attachment: fixed;
                    border: 2px solid #8B4513;
                    border-radius: 8px;
                }}
            """
            self.setStyleSheet(panel_style)
    
    def accept_export_as_mod(self):
        """导出为mod"""
        self.result = 1
        self.hide()
        if hasattr(self, '_exec_loop'):
            self._exec_loop.quit()
    
    def accept_export_as_mods(self):
        """导出为mods"""
        self.result = 2
        self.hide()
        if hasattr(self, '_exec_loop'):
            self._exec_loop.quit()
    
    def accept_cancel(self):
        """取消"""
        self.result = 0
        self.hide()
        if hasattr(self, '_exec_loop'):
            self._exec_loop.quit()
    
    def exec(self):
        """执行对话框，返回选择结果"""
        from PySide6.QtCore import QEventLoop
        self._exec_loop = QEventLoop()
        self._exec_loop.exec()
        return self.result
