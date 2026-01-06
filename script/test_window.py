"""
测试窗口脚本
用于测试基本窗口功能
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtCore import Qt


class TestWindow(QMainWindow):
    """测试窗口类"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("测试窗口")
        self.setGeometry(100, 100, 400, 300)
        
        # 创建中央标签
        label = QLabel("这是一个测试窗口", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #8B4513;
                padding: 20px;
            }
        """)
        
        self.setCentralWidget(label)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

