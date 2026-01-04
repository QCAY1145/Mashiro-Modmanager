"""
Mod管理器主程序入口
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap
from ui.main_window import MainWindow


def get_exe_directory():
    """获取exe文件所在目录，兼容开发环境和打包环境"""
    if getattr(sys, 'frozen', False):
        # 打包后的exe环境
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.abspath(__file__))


def main():
    """主函数，启动应用程序"""
    # 获取exe所在目录并切换到该目录
    exe_dir = get_exe_directory()
    os.chdir(exe_dir)
    
    app = QApplication(sys.argv)
    
    # 设置应用程序图标（兼容打包环境）
    try:
        if getattr(sys, 'frozen', False):
            # 打包后的exe环境，使用PyInstaller的临时路径
            icon_path = os.path.join(sys._MEIPASS, "background", "title.png")
        else:
            # 开发环境
            icon_path = os.path.join(exe_dir, "background", "title.png")
        
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                icon = QIcon(pixmap)
                app.setWindowIcon(icon)
    except Exception:
        # 图标设置失败不影响程序运行
        pass
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


