"""
面板组件模块
包含批量禁用面板、二分选择面板、高级设置面板、冲突处理面板、标签管理面板
"""
import os
import json
import shutil
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QCheckBox, QFileDialog, QFormLayout, QDialog, QScrollArea, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog, QMessageBox,
    QTextEdit, QPlainTextEdit, QSplitter
)
from PySide6.QtCore import Qt, QMimeData, QPoint, QThread, Signal, QTimer
from PySide6.QtGui import QDrag, QPainter, QColor, QIcon, QPixmap, QCloseEvent


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
    """冲突处理面板"""
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
        conflict_text = f"检测到与以下模组发生文件冲突：\n\n"
        for mod in self.conflicting_mods:
            conflict_text += f"  • {mod}\n"
        
        conflict_label = QLabel(conflict_text)
        conflict_label.setWordWrap(True)
        layout.addWidget(conflict_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        
        self.btn_ok = QPushButton("我知道了")
        self.btn_ok.clicked.connect(self.accept)
        
        button_layout.addWidget(self.btn_ok)
        layout.addLayout(button_layout)
        
        # 根据内容调整大小（移除固定大小，让窗口自适应内容）
        self.setMinimumWidth(400)  # 设置最小宽度，避免太窄
        self.adjustSize()  # 根据内容调整大小
    
    def exec(self):
        """执行对话框"""
        super().exec()
        return True


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
        # 删除和重命名按钮列：自动拉伸铺满剩余空间
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.MultiSelection)
        # 设置默认行高（增加30%）
        self.table.verticalHeader().setDefaultSectionSize(int(self.table.verticalHeader().defaultSectionSize() * 1.3))
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


class VirtualMappingPriorityPanel(QDialog):
    """虚拟映射优先级调整面板 - 仿照标签管理界面"""
    def __init__(self, conflicting_mods, parent=None):
        """
        Args:
            conflicting_mods: list of str, 发生冲突的mod列表（从高到低，第一个优先级最高）
            parent: 父窗口
        """
        super().__init__(parent)
        self.mod_list = conflicting_mods.copy()  # mod列表（从高到低）
        self.table = None
        self.setup_ui()
        self.refresh_table()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("调整虚拟映射优先级")
        self.setMinimumSize(500, 400)
        self.resize(500, 500)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # 提示文字
        hint_label = QLabel("优先级从高到低排列（上方优先级高，优先映射）\n选择两个mod后点击交换按钮可以交换位置")
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
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Mod名称（优先级从高到低）"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
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
        
        # 交换按钮
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
        self.btn_swap.clicked.connect(self.swap_mods)
        bottom_layout.addWidget(self.btn_swap)
        
        # 确定按钮（原保存按钮）
        self.btn_save = QPushButton("确定")
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
        self.btn_save.clicked.connect(self.save_priority)
        bottom_layout.addWidget(self.btn_save)
        
        layout.addLayout(bottom_layout)
        
        # 连接表格选择变化事件
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
    
    def refresh_table(self):
        """刷新表格显示"""
        if self.table is None:
            return
        
        # 清空表格内容
        self.table.setRowCount(0)
        
        # 填充数据
        for i, mod_name in enumerate(self.mod_list):
            self.table.insertRow(i)
            
            # Mod名称（第0列）
            item = QTableWidgetItem(mod_name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, item)
    
    def on_selection_changed(self):
        """选择变化时更新交换按钮状态"""
        selected_rows = [index.row() for index in self.table.selectionModel().selectedRows()]
        # 检查是否选择了两个行
        if len(selected_rows) == 2:
            self.btn_swap.setEnabled(True)
        else:
            self.btn_swap.setEnabled(False)
    
    def swap_mods(self):
        """交换两个mod的位置"""
        selected_rows = [index.row() for index in self.table.selectionModel().selectedRows()]
        if len(selected_rows) != 2:
            QMessageBox.warning(self, "提示", "请选择两个mod进行交换")
            return
        
        row1, row2 = sorted(selected_rows)
        # 交换位置
        self.mod_list[row1], self.mod_list[row2] = self.mod_list[row2], self.mod_list[row1]
        self.refresh_table()
        # 清除选择
        self.table.clearSelection()
    
    def save_priority(self):
        """保存优先级并刷新虚拟链接"""
        # 通知父窗口刷新虚拟链接（异步）
        parent = self.parent()
        if parent and hasattr(parent, 'refresh_virtual_mapping_async'):
            # 使用QTimer延迟执行，避免阻塞UI
            from PySide6.QtCore import QTimer
            mod_list_copy = self.mod_list.copy()  # 复制列表，避免lambda闭包问题
            QTimer.singleShot(0, lambda: parent.refresh_virtual_mapping_async(mod_list_copy))
        
        self.accept()
    
    def closeEvent(self, event: QCloseEvent):
        """重写关闭事件，阻止用户通过X按钮关闭窗口"""
        event.ignore()  # 忽略关闭事件，不允许关闭
    
    def exec(self):
        """执行对话框，返回选择结果和优先级顺序"""
        result = super().exec()
        return result, self.mod_list if result == QDialog.DialogCode.Accepted else None


class DictionarySelectionPanel(QDialog):
    """字典选择面板"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_dictionary = None
        self._ignore_selection_change = False
        self._pressed_row_state = {}  # 记录按下时的选中状态 {row: was_selected}
        self.setup_ui()
        self.load_dictionaries()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("字典管理")
        self.setMinimumSize(400, 500)
        self.resize(400, 500)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # 标题和导入按钮
        title_layout = QHBoxLayout()
        title_label = QLabel("选择字典")
        title_label.setStyleSheet("""
            QLabel {
                color: #8B4513;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 0;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        self.btn_import = QPushButton("导入字典")
        self.btn_import.setStyleSheet("""
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
        self.btn_import.clicked.connect(self.import_dictionary)
        title_layout.addWidget(self.btn_import)
        layout.addLayout(title_layout)
        
        # 使用自定义的表格类来完全控制选中行为
        class CustomTableWidget(QTableWidget):
            def __init__(self, parent_panel):
                super().__init__()
                self.parent_panel = parent_panel
            
            def mousePressEvent(self, event):
                """重写鼠标按下事件，实现点击切换选中"""
                if event.button() == Qt.LeftButton:
                    item = self.itemAt(event.pos())
                    if item:
                        row = item.row()
                        # 检查当前行是否已选中
                        selected_rows = [index.row() for index in self.selectionModel().selectedRows()]
                        if row in selected_rows:
                            # 如果已选中，取消选中
                            self.clearSelection()
                        else:
                            # 如果未选中，选中该项
                            self.selectRow(row)
                        event.accept()
                        return
                super().mousePressEvent(event)
        
        # 字典列表表格
        self.table = CustomTableWidget(self)
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["字典名"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setFocusPolicy(Qt.NoFocus)  # 移除焦点，避免黑色框
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: rgba(255, 182, 193, 200);
            }
            QTableWidget::item:focus {
                outline: none;
                border: none;
            }
            QTableWidget::item:selected:focus {
                outline: none;
                border: none;
            }
        """)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.table)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        self.btn_open = QPushButton("打开")
        self.btn_open.setStyleSheet("""
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
        self.btn_open.setEnabled(False)
        self.btn_open.clicked.connect(self.open_dictionary)
        bottom_layout.addWidget(self.btn_open)
        
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
        
        # 连接选择变化事件
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
    
    def load_dictionaries(self):
        """加载字典列表"""
        project_root = _get_project_root()
        dictionary_dir = os.path.join(project_root, "dictionary")
        
        dictionaries = []
        if os.path.exists(dictionary_dir):
            for filename in os.listdir(dictionary_dir):
                if filename.endswith('.json'):
                    dict_name = filename[:-5]  # 去掉.json后缀
                    dictionaries.append(dict_name)
        
        dictionaries.sort()
        
        self.table.setRowCount(len(dictionaries))
        for i, dict_name in enumerate(dictionaries):
            item = QTableWidgetItem(dict_name)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, item)
    
    def on_selection_changed(self):
        """选择变化时更新按钮状态"""
        selected = self.table.selectionModel().hasSelection()
        self.btn_open.setEnabled(selected)
    
    
    def on_item_double_clicked(self, item):
        """双击打开字典"""
        self.open_dictionary()
    
    def open_dictionary(self):
        """打开选中的字典"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        dict_name = self.table.item(row, 0).text()
        self.selected_dictionary = dict_name
        self.accept()
    
    def import_dictionary(self):
        """导入字典文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择要导入的JSON文件",
            "",
            "JSON文件 (*.json);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            # 读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 获取文件名（不含扩展名）作为字典名
            filename = os.path.basename(file_path)
            dict_name = os.path.splitext(filename)[0]
            
            # 检查字典是否已存在
            project_root = _get_project_root()
            dictionary_dir = os.path.join(project_root, "dictionary")
            os.makedirs(dictionary_dir, exist_ok=True)
            dictionary_file = os.path.join(dictionary_dir, f"{dict_name}.json")
            
            if os.path.exists(dictionary_file):
                reply = QMessageBox.question(
                    self,
                    "字典已存在",
                    f"字典 '{dict_name}' 已存在，是否覆盖？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            
            # 保存字典文件
            with open(dictionary_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 刷新字典列表
            self.load_dictionaries()
            
            QMessageBox.information(self, "成功", f"字典 '{dict_name}' 导入成功！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入字典失败: {str(e)}")


class DictionaryEditPanel(QDialog):
    """字典编辑面板"""
    def __init__(self, dictionary_name, parent=None, selection_panel=None):
        super().__init__(parent)
        self.dictionary_name = dictionary_name
        self.original_data = []
        self.current_data = []
        self.is_nested_dict = False  # 是否嵌套字典结构（自动检测）
        self.navigation_path = []  # 导航路径栈，记录当前所在的层级路径，如 ["第一层", "第二层A", "第三层A1"]
        self.nested_data = {}  # 嵌套字典数据（完整数据）
        self.selection_panel = selection_panel  # 保存字典选择面板的引用，用于返回
        self.setup_ui()
        self.load_dictionary()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle(f"编辑字典: {self.dictionary_name}")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # 顶部布局（返回按钮和搜索框在同一行）
        top_layout = QHBoxLayout()
        
        # 返回按钮（总是创建，根据字典类型显示/隐藏）
        self.btn_back = QPushButton("← 返回")
        self.btn_back.setStyleSheet("""
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
        # 初始隐藏，load_dictionary后会根据结构显示
        self.btn_back.setVisible(False)
        self.btn_back.clicked.connect(self.back_to_selection)  # 返回到字典选择页面
        top_layout.addWidget(self.btn_back)
        
        # 添加值按钮（总是创建，根据页面类型显示/隐藏）
        self.btn_add_value = QPushButton("添加值")
        self.btn_add_value.setStyleSheet("""
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
        self.btn_add_value.clicked.connect(self.add_value)
        self.btn_add_value.setVisible(False)  # 初始隐藏
        top_layout.addWidget(self.btn_add_value)
        
        # 删除值按钮（总是创建，根据页面类型显示/隐藏）
        self.btn_delete_value = QPushButton("删除值")
        self.btn_delete_value.setStyleSheet("""
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
        self.btn_delete_value.clicked.connect(self.delete_value)
        self.btn_delete_value.setVisible(False)  # 初始隐藏
        top_layout.addWidget(self.btn_delete_value)
        
        # 添加弹性空间，将搜索框推到右侧
        top_layout.addStretch()
        
        # 搜索框（总是创建）
        self.search_label = QLabel("搜索:")
        self.search_label.setStyleSheet("""
            QLabel {
                color: #8B4513;
                font-size: 14px;
                padding-right: 5px;
            }
        """)
        top_layout.addWidget(self.search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索路径或含义...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
                padding: 5px 10px;
                min-width: 200px;
            }
        """)
        self.search_input.textChanged.connect(self.on_search_changed)
        top_layout.addWidget(self.search_input)
        
        layout.addLayout(top_layout)
        
        # 表格（初始状态，load_dictionary后会更新）
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["路径", "含义"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 200)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setFocusPolicy(Qt.NoFocus)
        # 连接Ctrl+Tab键事件
        self.table.installEventFilter(self)
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
            QTableWidget::item:focus {
                outline: none;
                border: none;
            }
            QTableWidget::item:selected:focus {
                outline: none;
                border: none;
            }
        """)
        layout.addWidget(self.table)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        # 底部按钮（总是创建保存和取消，确定按钮在需要时创建）
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
        self.btn_save.clicked.connect(self.save_dictionary)
        bottom_layout.addWidget(self.btn_save)
        
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
        self.btn_cancel.clicked.connect(self.back_to_selection)
        bottom_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(bottom_layout)
    
    def detect_structure(self, data):
        """自动检测JSON结构"""
        if isinstance(data, dict) and len(data) > 0:
            # 检查是否是嵌套字典：递归检查所有值是否都是字典
            first_value = list(data.values())[0]
            if isinstance(first_value, dict):
                # 检查内层字典的值是否都是字符串或简单类型（到达最底层）
                if len(first_value) > 0:
                    inner_value = list(first_value.values())[0]
                    if isinstance(inner_value, (str, int, float, bool)) or inner_value is None:
                        return 'nested_dict'  # 两层嵌套
                    elif isinstance(inner_value, dict):
                        return 'nested_dict'  # 多层嵌套（继续递归）
            return 'dict'
        elif isinstance(data, list):
            if len(data) > 0 and isinstance(data[0], list) and len(data[0]) >= 2:
                return 'list_of_lists'  # [[key, value], ...]
            return 'list'
        return 'unknown'
    
    def get_current_level_data(self):
        """根据导航路径获取当前层级的数据"""
        data = self.nested_data
        for key in self.navigation_path:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return {}
        return data if isinstance(data, dict) else {}
    
    def is_leaf_level(self, data):
        """检查当前层级是否是叶子节点（包含实际数据）"""
        if not isinstance(data, dict) or len(data) == 0:
            return True
        
        # 检查所有值：如果所有值都是简单类型，则是叶子节点
        # 如果所有值都是字典，则不是叶子节点（还有下一层）
        all_simple = True
        all_dict = True
        
        for value in data.values():
            is_simple = isinstance(value, (str, int, float, bool)) or value is None
            is_dict = isinstance(value, dict)
            
            if not is_simple:
                all_simple = False
            if not is_dict:
                all_dict = False
        
        # 如果所有值都是简单类型，则是叶子节点
        if all_simple:
            return True
        
        # 如果所有值都是字典，则不是叶子节点（还有过渡页）
        if all_dict:
            return False
        
        # 混合情况：默认不是叶子节点（需要进一步判断，但这种情况不应该出现）
        return False
    
    def update_ui_for_nested(self):
        """更新UI为嵌套字典模式"""
        current_data = self.get_current_level_data()
        is_leaf = self.is_leaf_level(current_data)
        
        if is_leaf:
            # 显示详情表格（叶子节点）
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(["路径", "含义"])
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
            self.table.setColumnWidth(1, 200)
            if hasattr(self, 'search_input'):
                self.search_input.setVisible(True)
            if hasattr(self, 'search_label'):
                self.search_label.setVisible(True)
            # 显示添加值和删除值按钮
            if hasattr(self, 'btn_add_value'):
                self.btn_add_value.setVisible(True)
            if hasattr(self, 'btn_delete_value'):
                self.btn_delete_value.setVisible(True)
        else:
            # 显示类别列表（中间层）
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["字典名"])
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            if hasattr(self, 'search_input'):
                self.search_input.setVisible(False)
            if hasattr(self, 'search_label'):
                self.search_label.setVisible(False)
            # 显示添加值和删除值按钮
            if hasattr(self, 'btn_add_value'):
                self.btn_add_value.setVisible(True)
            if hasattr(self, 'btn_delete_value'):
                self.btn_delete_value.setVisible(True)
    
    def update_ui_for_flat(self):
        """更新UI为扁平字典模式"""
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["路径", "含义"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 200)
        # 显示添加值和删除值按钮
        if hasattr(self, 'btn_add_value'):
            self.btn_add_value.setVisible(True)
        if hasattr(self, 'btn_delete_value'):
            self.btn_delete_value.setVisible(True)
        if hasattr(self, 'search_input'):
            self.search_input.setVisible(True)
        if hasattr(self, 'search_label'):
            self.search_label.setVisible(True)
    
    def refresh_categories(self):
        """刷新类别列表（显示当前层级的选项）"""
        if not self.is_nested_dict:
            return
        
        current_data = self.get_current_level_data()
        is_leaf = self.is_leaf_level(current_data)
        
        if is_leaf:
            # 叶子节点：显示实际数据
            items = current_data
            self.current_data = [[str(v), str(k)] for k, v in items.items()]
            self.original_data = [[str(v), str(k)] for k, v in items.items()]
            self.refresh_table()
        else:
            # 中间层：显示子类别列表
            categories = sorted(current_data.keys())
            self.table.setRowCount(len(categories))
            
            for i, category in enumerate(categories):
                item = QTableWidgetItem(category)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(i, 0, item)
    
    def load_dictionary(self):
        """加载字典数据"""
        project_root = _get_project_root()
        dictionary_dir = os.path.join(project_root, "dictionary")
        dictionary_file = os.path.join(dictionary_dir, f"{self.dictionary_name}.json")
        
        if not os.path.exists(dictionary_file):
            QMessageBox.warning(self, "错误", f"字典文件不存在: {dictionary_file}")
            self.reject()
            return
        
        try:
            with open(dictionary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 自动检测结构
            structure = self.detect_structure(data)
            
            if structure == 'nested_dict':
                # 嵌套字典结构（支持无限嵌套）
                self.is_nested_dict = True
                self.nested_data = data
                self.navigation_path = []  # 初始在根层级
                # 更新返回按钮
                self.btn_back.setVisible(True)
                self.btn_back.clicked.disconnect()
                self.btn_back.clicked.connect(self.back_to_selection)
                # 检查当前层级是否是叶子节点
                current_data = self.get_current_level_data()
                is_leaf = self.is_leaf_level(current_data)
                if not is_leaf:
                    # 隐藏保存和取消，显示确定按钮
                    self.btn_save.setVisible(False)
                    self.btn_cancel.setVisible(False)
                    # 创建确定按钮
                    bottom_layout = QHBoxLayout()
                    bottom_layout.addStretch()
                    self.btn_ok = QPushButton("确定")
                    self.btn_ok.setStyleSheet("""
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
                    self.btn_ok.clicked.connect(self.on_category_confirm)
                    self.btn_ok.setEnabled(False)
                    bottom_layout.addWidget(self.btn_ok)
                    layout = self.layout()
                    layout.addLayout(bottom_layout)
                    # 连接选择变化事件
                    self.table.selectionModel().selectionChanged.connect(self.on_category_selection_changed)
                else:
                    # 叶子节点，显示保存和取消
                    self.btn_save.setVisible(True)
                    self.btn_cancel.setVisible(True)
                self.update_ui_for_nested()
                self.refresh_categories()
            elif structure == 'list_of_lists':
                # 列表格式：[[key, value], ...]
                self.is_nested_dict = False
                self.original_data = data.copy()
                self.current_data = data.copy()
                # 隐藏返回按钮，显示保存和取消
                self.btn_back.setVisible(False)
                self.btn_save.setVisible(True)
                self.btn_cancel.setVisible(True)
                self.update_ui_for_flat()
                self.refresh_table()
            elif structure == 'dict':
                # 普通字典：{key: value}，转换为列表格式
                self.is_nested_dict = False
                self.original_data = [[k, v] for k, v in data.items()]
                self.current_data = [[k, v] for k, v in data.items()]
                # 隐藏返回按钮，显示保存和取消
                self.btn_back.setVisible(False)
                self.btn_save.setVisible(True)
                self.btn_cancel.setVisible(True)
                self.update_ui_for_flat()
                self.refresh_table()
            elif structure == 'list':
                # 简单列表，转换为 [[index, value], ...]
                self.is_nested_dict = False
                self.original_data = [[str(i), str(v)] for i, v in enumerate(data)]
                self.current_data = [[str(i), str(v)] for i, v in enumerate(data)]
                # 隐藏返回按钮，显示保存和取消
                self.btn_back.setVisible(False)
                self.btn_save.setVisible(True)
                self.btn_cancel.setVisible(True)
                self.update_ui_for_flat()
                self.refresh_table()
            else:
                QMessageBox.warning(self, "错误", "无法识别的字典文件格式")
                self.reject()
                return
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载字典失败: {str(e)}")
            self.reject()
    
    def on_category_selection_changed(self):
        """类别选择变化时更新确定按钮状态"""
        if hasattr(self, 'btn_ok'):
            selected = self.table.selectionModel().hasSelection()
            self.btn_ok.setEnabled(selected)
    
    def on_category_confirm(self):
        """点击确定按钮，进入选中的类别"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        category_item = self.table.item(row, 0)
        if not category_item:
            return
        
        category = category_item.text()
        self.enter_category(category)
    
    def enter_category(self, category):
        """进入指定类别的下一层"""
        # 添加到导航路径
        self.navigation_path.append(category)
        
        # 获取当前层级数据
        current_data = self.get_current_level_data()
        is_leaf = self.is_leaf_level(current_data)
        
        # 更新返回按钮功能：返回上一层
        self.btn_back.clicked.disconnect()
        if len(self.navigation_path) > 0:
            self.btn_back.clicked.connect(self.back_to_categories)
        else:
            self.btn_back.clicked.connect(self.reject)
        self.btn_back.setVisible(True)
        
        # 更新UI
        self.update_ui_for_nested()
        
        # 如果是叶子节点，显示保存和取消按钮；否则显示确定按钮
        if is_leaf:
            # 隐藏确定按钮，显示保存和取消按钮
            if hasattr(self, 'btn_ok'):
                self.btn_ok.setVisible(False)
            self.btn_save.setVisible(True)
            self.btn_cancel.setVisible(True)
        else:
            # 显示确定按钮，隐藏保存和取消
            self.btn_save.setVisible(False)
            self.btn_cancel.setVisible(False)
            if not hasattr(self, 'btn_ok'):
                # 创建确定按钮
                layout = self.layout()
                bottom_layout = QHBoxLayout()
                bottom_layout.addStretch()
                self.btn_ok = QPushButton("确定")
                self.btn_ok.setStyleSheet("""
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
                self.btn_ok.clicked.connect(self.on_category_confirm)
                self.btn_ok.setEnabled(False)
                bottom_layout.addWidget(self.btn_ok)
                layout.addLayout(bottom_layout)
                self.table.selectionModel().selectionChanged.connect(self.on_category_selection_changed)
            else:
                self.btn_ok.setVisible(True)
                self.btn_ok.setEnabled(False)
        
        # 刷新显示
        self.refresh_categories()
    
    def back_to_selection(self):
        """返回到字典选择页面"""
        self.accept()  # 使用accept而不是reject，这样主窗口可以检测到需要返回选择页面
    
    def back_to_categories(self):
        """返回上一层"""
        if len(self.navigation_path) > 0:
            # 移除最后一层
            self.navigation_path.pop()
        
        # 获取当前层级数据
        current_data = self.get_current_level_data()
        is_leaf = self.is_leaf_level(current_data)
        
        # 更新返回按钮功能
        self.btn_back.clicked.disconnect()
        if len(self.navigation_path) > 0:
            self.btn_back.clicked.connect(self.back_to_categories)
        else:
            self.btn_back.clicked.connect(self.back_to_selection)
        self.btn_back.setVisible(True)
        
        # 更新UI
        self.update_ui_for_nested()
        
        # 如果是叶子节点，显示保存和取消；否则显示确定按钮
        if is_leaf:
            if hasattr(self, 'btn_ok'):
                self.btn_ok.setVisible(False)
            self.btn_save.setVisible(True)
            self.btn_cancel.setVisible(True)
        else:
            self.btn_save.setVisible(False)
            self.btn_cancel.setVisible(False)
            if hasattr(self, 'btn_ok'):
                self.btn_ok.setVisible(True)
                self.btn_ok.setEnabled(False)
        
        # 清除搜索
        if hasattr(self, 'search_input'):
            self.search_input.clear()
        
        # 刷新显示
        self.refresh_categories()
        
        # 如果不是叶子节点，需要连接选择变化事件
        if not is_leaf:
            if hasattr(self, 'btn_ok'):
                # 断开之前的连接（如果存在）
                try:
                    self.table.selectionModel().selectionChanged.disconnect(self.on_category_selection_changed)
                except:
                    pass
                # 重新连接
                self.table.selectionModel().selectionChanged.connect(self.on_category_selection_changed)
    
    def refresh_table(self):
        """刷新表格显示"""
        # 如果是嵌套字典且正在显示类别列表（非叶子节点），不处理
        if self.is_nested_dict:
            current_data = self.get_current_level_data()
            if not self.is_leaf_level(current_data):
                return
        
        search_text = self.search_input.text().strip().lower()
        
        # 过滤数据
        filtered_data = []
        for item in self.current_data:
            if len(item) >= 2:
                # 对于武器字典，第一列是武器名，第二列是地址
                # 对于普通字典，第一列是路径，第二列是含义
                col1 = str(item[0]).lower()
                col2 = str(item[1]).lower()
                if not search_text or search_text in col1 or search_text in col2:
                    # 创建新的列表副本，避免引用同一个对象
                    filtered_data.append([str(item[0]), str(item[1])])
        
        self.table.setRowCount(len(filtered_data))
        
        for i, item in enumerate(filtered_data):
            # 第一列（可编辑）
            col1_item = QTableWidgetItem(item[0])
            col1_item.setFlags(col1_item.flags() | Qt.ItemIsEditable)
            self.table.setItem(i, 0, col1_item)
            
            # 第二列（可编辑）
            col2_item = QTableWidgetItem(item[1])
            col2_item.setFlags(col2_item.flags() | Qt.ItemIsEditable)
            self.table.setItem(i, 1, col2_item)
    
    def on_search_changed(self):
        """搜索文本变化时刷新表格"""
        self.refresh_table()
    
    def save_dictionary(self):
        """保存字典数据"""
        if self.is_nested_dict:
            # 保存嵌套字典的当前层级
            self.save_nested_category()
        else:
            # 保存普通字典
            self.save_normal_dictionary()
    
    def save_nested_category(self):
        """保存嵌套字典类别的修改"""
        # 从表格读取所有显示的数据：路径在前，含义在后
        displayed_data = []
        
        for row in range(self.table.rowCount()):
            value_item = self.table.item(row, 0)  # 路径（值）
            name_item = self.table.item(row, 1)  # 含义（名称）
            if value_item and name_item:
                value = value_item.text().strip()
                name = name_item.text().strip()
                if value and name:
                    displayed_data.append([value, name])
        
        # 根据导航路径更新对应层级的数据
        # 需要递归更新嵌套字典，保留其他部分的数据
        def update_nested_dict(data, path, new_items):
            """递归更新嵌套字典，保留其他部分的数据"""
            # 深拷贝数据，避免修改原数据
            result = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    result[key] = value.copy()
                else:
                    result[key] = value
            
            if len(path) == 0:
                # 到达目标层级，更新数据
                return {item[1]: item[0] for item in new_items}
            else:
                # 继续递归
                key = path[0]
                if key in result:
                    result[key] = update_nested_dict(result[key], path[1:], new_items)
                else:
                    result[key] = update_nested_dict({}, path[1:], new_items)
                return result
        
        # 更新数据
        self.nested_data = update_nested_dict(self.nested_data, self.navigation_path, displayed_data)
        
        # 保存到文件
        project_root = _get_project_root()
        dictionary_dir = os.path.join(project_root, "dictionary")
        dictionary_file = os.path.join(dictionary_dir, f"{self.dictionary_name}.json")
        
        try:
            with open(dictionary_file, 'w', encoding='utf-8') as f:
                json.dump(self.nested_data, f, ensure_ascii=False, indent=2)
            
            # 更新original_data和current_data
            self.current_data = displayed_data.copy()
            self.original_data = displayed_data.copy()
            
            # 清除搜索并刷新
            if hasattr(self, 'search_input'):
                self.search_input.clear()
            self.refresh_table()
            
            QMessageBox.information(self, "成功", f"已保存 {len(displayed_data)} 个条目的修改")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
    
    def save_normal_dictionary(self):
        """保存普通字典数据"""
        # 从表格读取所有显示的数据
        search_text = self.search_input.text().strip().lower()
        displayed_data = []
        
        for row in range(self.table.rowCount()):
            address_item = self.table.item(row, 0)
            meaning_item = self.table.item(row, 1)
            
            if address_item and meaning_item:
                address = address_item.text().strip()
                meaning = meaning_item.text().strip()
                if address:  # 路径不能为空
                    displayed_data.append([address, meaning])
        
        # 统计修改数量
        change_count = 0
        
        # 更新当前数据
        if search_text:
            # 如果有搜索过滤，只更新匹配搜索条件的数据
            # 构建新的数据列表：保留不匹配的数据，替换匹配的数据
            new_data = []
            filtered_indices = []
            
            # 先找到所有匹配搜索条件的索引（保持顺序）
            for i, item in enumerate(self.current_data):
                if len(item) >= 2:
                    address = str(item[0]).lower()
                    meaning = str(item[1]).lower()
                    if search_text in address or search_text in meaning:
                        filtered_indices.append(i)
            
            # 构建新数据：保留不匹配的数据，替换匹配的数据（按原顺序）
            displayed_idx = 0
            for i, item in enumerate(self.current_data):
                if i in filtered_indices:
                    # 这个位置应该被替换为表格中的数据
                    if displayed_idx < len(displayed_data):
                        new_item = displayed_data[displayed_idx]
                        # 检查是否有修改
                        if len(item) < 2 or item[0] != new_item[0] or item[1] != new_item[1]:
                            change_count += 1
                        new_data.append(new_item)
                        displayed_idx += 1
                    else:
                        # 如果表格中的数据用完了，就跳过（相当于删除）
                        change_count += 1
                else:
                    # 保留不匹配的数据
                    new_data.append(item)
            
            # 如果还有剩余的表格数据，追加到末尾（这不应该发生，但为了安全）
            if displayed_idx < len(displayed_data):
                # 这种情况说明表格中的数据比原始匹配的数据多，可能是用户添加了新数据
                while displayed_idx < len(displayed_data):
                    new_data.append(displayed_data[displayed_idx])
                    change_count += 1
                    displayed_idx += 1
            
            self.current_data = new_data
        else:
            # 没有搜索过滤，直接替换所有数据
            # 比较原始数据和新数据，统计修改数量
            original_dict = {tuple(item) if len(item) >= 2 else tuple(): True for item in self.original_data}
            new_dict = {tuple(item) if len(item) >= 2 else tuple(): True for item in displayed_data}
            
            # 统计新增和修改的项
            for item in displayed_data:
                if len(item) >= 2 and tuple(item) not in original_dict:
                    change_count += 1
            
            # 统计删除的项
            for item in self.original_data:
                if len(item) >= 2 and tuple(item) not in new_dict:
                    change_count += 1
            
            self.current_data = displayed_data
        
        # 保存到文件
        project_root = _get_project_root()
        dictionary_dir = os.path.join(project_root, "dictionary")
        os.makedirs(dictionary_dir, exist_ok=True)
        dictionary_file = os.path.join(dictionary_dir, f"{self.dictionary_name}.json")
        
        try:
            with open(dictionary_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, ensure_ascii=False, indent=2)
            
            print(f"对{self.dictionary_name}字典的{change_count}个修改已保存")
            QMessageBox.information(self, "成功", f"对{self.dictionary_name}字典的{change_count}个修改已保存")
            self.original_data = self.current_data.copy()
            # 保存后清除搜索，显示所有数据
            self.search_input.clear()
            self.refresh_table()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存字典失败: {str(e)}")
    
    def eventFilter(self, obj, event):
        """事件过滤器，处理Ctrl+Tab键自动填充"""
        from PySide6.QtGui import QKeyEvent
        if obj == self.table and isinstance(event, QKeyEvent) and event.type() == event.Type.KeyPress:
            # 使用Ctrl+Tab组合键
            if event.key() == Qt.Key_Tab and event.modifiers() == Qt.ControlModifier:
                current_item = self.table.currentItem()
                if current_item and current_item.column() == 0:  # 在第一列（路径列）
                    current_row = current_item.row()
                    if current_row > 0:  # 有上一行
                        prev_item = self.table.item(current_row - 1, 0)
                        if prev_item:
                            prev_path = prev_item.text().strip()
                            if prev_path:
                                # 获取路径的最后一层目录之前的部分
                                if '/' in prev_path:
                                    # 找到最后一个/的位置
                                    last_slash = prev_path.rfind('/')
                                    if last_slash > 0:
                                        prefix = prev_path[:last_slash + 1]  # 包含最后的/
                                        # 如果当前单元格为空，自动填充
                                        if not current_item.text().strip():
                                            current_item.setText(prefix)
                                            return True  # 阻止默认Tab行为
        return super().eventFilter(obj, event)
    
    def add_value(self):
        """添加值：编辑页新建一行，过渡页新建一个子页"""
        if self.is_nested_dict:
            current_data = self.get_current_level_data()
            is_leaf = self.is_leaf_level(current_data)
        else:
            is_leaf = True
        
        if is_leaf:
            # 编辑页：新建一行
            row_count = self.table.rowCount()
            self.table.insertRow(row_count)
            
            # 创建新行，第一列（路径）可编辑
            path_item = QTableWidgetItem("")
            path_item.setFlags(path_item.flags() | Qt.ItemIsEditable)
            self.table.setItem(row_count, 0, path_item)
            
            # 第二列（含义）可编辑
            meaning_item = QTableWidgetItem("")
            meaning_item.setFlags(meaning_item.flags() | Qt.ItemIsEditable)
            self.table.setItem(row_count, 1, meaning_item)
            
            # 选中新行并开始编辑
            self.table.setCurrentItem(path_item)
            self.table.editItem(path_item)
        else:
            # 过渡页：新建一个子页
            category_name, ok = QInputDialog.getText(self, "添加分类", "请输入分类名称:")
            if ok and category_name.strip():
                category_name = category_name.strip()
                # 检查是否已存在
                current_data = self.get_current_level_data()
                if category_name in current_data:
                    QMessageBox.warning(self, "错误", f"分类 '{category_name}' 已存在")
                    return
                
                # 添加到当前层级数据
                def add_to_nested_dict(data, path, new_key):
                    """递归添加到嵌套字典"""
                    if len(path) == 0:
                        # 到达目标层级，添加新键
                        data[new_key] = {}
                        return data
                    else:
                        # 继续递归
                        key = path[0]
                        if key not in data:
                            data[key] = {}
                        data[key] = add_to_nested_dict(data[key], path[1:], new_key)
                        return data
                
                self.nested_data = add_to_nested_dict(self.nested_data.copy(), self.navigation_path, category_name)
                
                # 刷新显示
                self.refresh_categories()
    
    def delete_value(self):
        """删除值：编辑页删除选中行，过渡页删除选中分类"""
        if self.is_nested_dict:
            current_data = self.get_current_level_data()
            is_leaf = self.is_leaf_level(current_data)
        else:
            is_leaf = True
        
        selected_rows = [index.row() for index in self.table.selectionModel().selectedRows()]
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择要删除的行或分类")
            return
        
        if is_leaf:
            # 编辑页：删除选中行
            reply = QMessageBox.question(
                self, "确认删除", 
                f"确定要删除选中的 {len(selected_rows)} 行吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                # 从后往前删除，避免索引变化
                for row in sorted(selected_rows, reverse=True):
                    self.table.removeRow(row)
        else:
            # 过渡页：删除选中分类
            if len(selected_rows) > 1:
                QMessageBox.warning(self, "提示", "一次只能删除一个分类")
                return
            
            row = selected_rows[0]
            category_item = self.table.item(row, 0)
            if not category_item:
                return
            
            category_name = category_item.text()
            reply = QMessageBox.question(
                self, "确认删除", 
                f"确定要删除分类 '{category_name}' 及其所有内容吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                # 从嵌套字典中删除
                def delete_from_nested_dict(data, path, key_to_delete):
                    """递归从嵌套字典中删除"""
                    if len(path) == 0:
                        # 到达目标层级，删除键
                        if key_to_delete in data:
                            del data[key_to_delete]
                        return data
                    else:
                        # 继续递归
                        key = path[0]
                        if key in data:
                            data[key] = delete_from_nested_dict(data[key], path[1:], key_to_delete)
                        return data
                
                self.nested_data = delete_from_nested_dict(self.nested_data.copy(), self.navigation_path, category_name)
                
                # 刷新显示
                self.refresh_categories()


class ScriptSelectionPanel(QDialog):
    """脚本选择面板"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_script = None
        self.setup_ui()
        self.load_scripts()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("脚本管理")
        self.setMinimumSize(400, 500)
        self.resize(400, 500)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # 标题和导入按钮
        title_layout = QHBoxLayout()
        title_label = QLabel("选择脚本")
        title_label.setStyleSheet("""
            QLabel {
                color: #8B4513;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 0;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        self.btn_import = QPushButton("导入脚本")
        self.btn_import.setStyleSheet("""
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
        self.btn_import.clicked.connect(self.import_script)
        title_layout.addWidget(self.btn_import)
        layout.addLayout(title_layout)
        
        # 脚本列表表格
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["脚本名"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: rgba(255, 182, 193, 200);
            }
            QTableWidget::item:focus {
                outline: none;
                border: none;
            }
            QTableWidget::item:selected:focus {
                outline: none;
                border: none;
            }
        """)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.table)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        self.btn_open = QPushButton("打开")
        self.btn_open.setStyleSheet("""
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
        self.btn_open.setEnabled(False)
        self.btn_open.clicked.connect(self.open_script)
        bottom_layout.addWidget(self.btn_open)
        
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
        
        # 连接选择变化事件
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
    
    def load_scripts(self):
        """加载脚本列表"""
        project_root = _get_project_root()
        script_dir = os.path.join(project_root, "script")
        
        scripts = []
        if os.path.exists(script_dir):
            for filename in os.listdir(script_dir):
                if filename.endswith('.py') and filename != '__init__.py':
                    script_name = filename[:-3]  # 去掉.py后缀
                    scripts.append(script_name)
        
        scripts.sort()
        
        self.table.setRowCount(len(scripts))
        for i, script_name in enumerate(scripts):
            item = QTableWidgetItem(script_name)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, item)
    
    def on_selection_changed(self):
        """选择变化时更新按钮状态"""
        selected = self.table.selectionModel().hasSelection()
        self.btn_open.setEnabled(selected)
    
    def on_item_double_clicked(self, item):
        """双击打开脚本"""
        self.open_script()
    
    def open_script(self):
        """打开选中的脚本"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        script_name = self.table.item(row, 0).text()
        self.selected_script = script_name
        self.accept()
    
    def import_script(self):
        """导入脚本文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择要导入的Python脚本",
            "",
            "Python文件 (*.py);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            # 获取文件名
            filename = os.path.basename(file_path)
            
            # 检查脚本是否已存在
            project_root = _get_project_root()
            script_dir = os.path.join(project_root, "script")
            os.makedirs(script_dir, exist_ok=True)
            script_file = os.path.join(script_dir, filename)
            
            if os.path.exists(script_file):
                reply = QMessageBox.question(
                    self,
                    "脚本已存在",
                    f"脚本 '{filename}' 已存在，是否覆盖？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            
            # 复制脚本文件
            shutil.copy2(file_path, script_file)
            
            # 刷新脚本列表
            self.load_scripts()
            
            QMessageBox.information(self, "成功", f"脚本 '{filename}' 导入成功！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入脚本失败: {str(e)}")


class ScriptEditPanel(QDialog):
    """脚本编辑面板"""
    def __init__(self, script_name, parent=None, selection_panel=None):
        super().__init__(parent)
        self.script_name = script_name
        self.selection_panel = selection_panel
        self.running_process = None  # 保存正在运行的进程
        self.process_timer = None  # 用于监控进程状态的定时器
        self.setup_ui()
        self.load_script()
    
    def setup_ui(self):
        """设置UI"""
        from config import WINDOW_WIDTH, WINDOW_HEIGHT
        self.setWindowTitle(f"查看脚本：{self.script_name}")
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """
        
        # 使用水平分割器：左侧文本框，右侧按钮
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧文本编辑区
        self.text_edit = QPlainTextEdit()
        self.text_edit.setStyleSheet("""
            QPlainTextEdit {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
        splitter.addWidget(self.text_edit)
        
        # 右侧按钮面板
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)  # 增大间距
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_panel.setLayout(right_layout)
        
        # 添加stretch，让按钮靠近底部
        right_layout.addStretch()
        
        self.btn_uninstall = QPushButton("卸载脚本")
        self.btn_uninstall.setStyleSheet(button_style)
        self.btn_uninstall.clicked.connect(self.uninstall_script)
        right_layout.addWidget(self.btn_uninstall)
        
        self.btn_save = QPushButton("保存脚本")
        self.btn_save.setStyleSheet(button_style)
        self.btn_save.clicked.connect(self.save_script)
        right_layout.addWidget(self.btn_save)
        
        self.btn_run = QPushButton("运行脚本")
        self.btn_run.setStyleSheet(button_style)
        self.btn_run.clicked.connect(self.run_script)
        right_layout.addWidget(self.btn_run)
        
        self.btn_terminal = QPushButton("打开终端")
        self.btn_terminal.setStyleSheet(button_style)
        self.btn_terminal.clicked.connect(self.open_terminal)
        right_layout.addWidget(self.btn_terminal)
        
        splitter.addWidget(right_panel)
        
        # 设置分割器比例：左侧文本框占大部分，右侧按钮面板占小部分
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setSizes([700, 300])
        
        layout.addWidget(splitter)
    
    def load_script(self):
        """加载脚本内容"""
        project_root = _get_project_root()
        script_dir = os.path.join(project_root, "script")
        script_file = os.path.join(script_dir, f"{self.script_name}.py")
        
        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                content = f.read()
            self.text_edit.setPlainText(content)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载脚本失败: {str(e)}")
    
    def save_script(self):
        """保存脚本内容"""
        project_root = _get_project_root()
        script_dir = os.path.join(project_root, "script")
        script_file = os.path.join(script_dir, f"{self.script_name}.py")
        
        try:
            content = self.text_edit.toPlainText()
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(content)
            QMessageBox.information(self, "成功", f"脚本 '{self.script_name}' 已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存脚本失败: {str(e)}")
    
    def uninstall_script(self):
        """卸载脚本"""
        reply = QMessageBox.question(
            self,
            "确认卸载",
            f"确定要卸载脚本 '{self.script_name}' 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            project_root = _get_project_root()
            script_dir = os.path.join(project_root, "script")
            script_file = os.path.join(script_dir, f"{self.script_name}.py")
            
            try:
                if os.path.exists(script_file):
                    os.remove(script_file)
                    QMessageBox.information(self, "成功", f"脚本 '{self.script_name}' 已卸载")
                    self.back_to_selection()
                else:
                    QMessageBox.warning(self, "错误", f"脚本文件不存在: {script_file}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"卸载脚本失败: {str(e)}")
    
    def run_script(self):
        """运行/停止脚本"""
        import subprocess
        import sys
        
        # 如果已有进程在运行，则停止
        if self.running_process is not None:
            try:
                if self.running_process.poll() is None:  # 进程仍在运行
                    self.running_process.terminate()
                    try:
                        self.running_process.wait(timeout=3)  # 等待3秒
                    except subprocess.TimeoutExpired:
                        self.running_process.kill()  # 强制终止
                    QMessageBox.information(self, "成功", f"脚本 '{self.script_name}' 已停止")
                self.running_process = None
                self.btn_run.setText("运行脚本")
                # 停止定时器
                if self.process_timer:
                    self.process_timer.stop()
                    self.process_timer = None
            except Exception as e:
                QMessageBox.warning(self, "错误", f"停止脚本失败: {str(e)}")
            return
        
        project_root = _get_project_root()
        script_dir = os.path.join(project_root, "script")
        script_file = os.path.join(script_dir, f"{self.script_name}.py")
        
        if not os.path.exists(script_file):
            QMessageBox.warning(self, "错误", f"脚本文件不存在: {script_file}")
            return
        
        # 读取沙盒模式设置
        settings_file = os.path.join(project_root, "settings.json")
        sandbox_mode = False
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    sandbox_mode = settings.get('sandbox_mode', False)
        except Exception as e:
            print(f"读取设置失败: {e}")
        
        try:
            if sandbox_mode:
                # 沙盒模式运行：使用受限环境
                env = os.environ.copy()
                
                # 使用 subprocess 在子进程中运行
                self.running_process = subprocess.Popen(
                    [sys.executable, script_file],
                    cwd=script_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                
                # 更新按钮文本
                self.btn_run.setText("停止运行")
                
                # 使用线程异步等待进程完成
                class ProcessWatcher(QThread):
                    finished = Signal(int, str, str)  # returncode, stdout, stderr
                    
                    def __init__(self, process):
                        super().__init__()
                        self.process = process
                    
                    def run(self):
                        try:
                            stdout, stderr = self.process.communicate(timeout=300)  # 5分钟超时
                            self.finished.emit(self.process.returncode, stdout, stderr)
                        except subprocess.TimeoutExpired:
                            self.process.kill()
                            self.finished.emit(-1, "", "脚本运行超时（已终止）")
                
                def on_process_finished(returncode, stdout, stderr):
                    self.running_process = None
                    self.btn_run.setText("运行脚本")
                    # 移除弹窗提示
                
                watcher = ProcessWatcher(self.running_process)
                watcher.finished.connect(on_process_finished)
                watcher.start()
            else:
                # 直接运行脚本
                self.running_process = subprocess.Popen(
                    [sys.executable, script_file],
                    cwd=script_dir,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                
                # 更新按钮文本
                self.btn_run.setText("停止运行")
                
                # 检查进程是否立即退出
                if self.running_process.poll() is not None:
                    # 进程已结束
                    self.running_process = None
                    self.btn_run.setText("运行脚本")
                    # 移除弹窗提示
                    # 创建定时器监控进程状态
                    if self.process_timer:
                        self.process_timer.stop()
                    self.process_timer = QTimer()
                    self.process_timer.timeout.connect(self.check_process_status)
                    self.process_timer.start(1000)  # 每秒检查一次
        except Exception as e:
            self.running_process = None
            self.btn_run.setText("运行脚本")
            if self.process_timer:
                self.process_timer.stop()
                self.process_timer = None
            QMessageBox.critical(self, "错误", f"运行脚本失败: {str(e)}")
    
    def check_process_status(self):
        """检查进程状态（用于非沙盒模式）"""
        if self.running_process is None:
            if self.process_timer:
                self.process_timer.stop()
                self.process_timer = None
            return
        
        if self.running_process.poll() is not None:
            # 进程已结束
            self.running_process = None
            self.btn_run.setText("运行脚本")
            if self.process_timer:
                self.process_timer.stop()
                self.process_timer = None
    
    def open_terminal(self):
        """打开终端（占位功能）"""
        QMessageBox.information(self, "提示", "打开终端功能待实现")
    
    def back_to_selection(self):
        """返回到脚本选择页面"""
        self.accept()  # 使用accept而不是reject，这样主窗口可以检测到需要返回选择页面
