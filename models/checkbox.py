"""
Mod复选框组件模块
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QCheckBox
from PySide6.QtCore import Qt, Signal


class ModCheckBox(QWidget):
    """自定义Mod复选框控件"""
    state_changed = Signal(int, bool)  # 行号, 是否启用
    
    def __init__(self, row, parent=None):
        super().__init__(parent)
        self.row = row
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        self.checkbox = QCheckBox()
        # 默认状态由外部设置，不在这里硬编码
        self.checkbox.stateChanged.connect(self.on_state_changed)
        
        # 设置复选框样式
        self.checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #8B4513;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #FF8C00;
                background-color: #FFF8DC;
            }
            QCheckBox::indicator:checked {
                background-color: #2E8B57;
                border: 2px solid #2E8B57;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgNEw0LjUgN0wxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
            }
            QCheckBox::indicator:checked:hover {
                background-color: #3CB371;
                border: 2px solid #3CB371;
            }
        """)
        
        layout.addWidget(self.checkbox)
        self.setLayout(layout)
    
    def on_state_changed(self, state):
        """复选框状态改变"""
        # 使用isChecked()方法获取实际状态，更可靠
        is_checked = self.checkbox.isChecked()
        self.state_changed.emit(self.row, is_checked)
    
    def set_checked(self, checked):
        """设置复选框状态"""
        # 临时阻塞信号，避免在程序设置状态时触发事件处理
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(checked)
        self.checkbox.blockSignals(False)
    
    def is_checked(self):
        """获取复选框状态"""
        return self.checkbox.isChecked()



