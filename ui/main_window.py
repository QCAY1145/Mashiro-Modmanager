import sys
import os
# 添加项目根目录到Python路径，以便导入config模块
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# 在打包环境中，确保models目录在路径中
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # 打包环境：添加临时目录到路径
    if sys._MEIPASS not in sys.path:
        sys.path.insert(0, sys._MEIPASS)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QLabel, QPushButton, QLineEdit, QCheckBox, QComboBox,
    QFormLayout, QTreeWidget, QTreeWidgetItem, QFileDialog, QInputDialog,
    QMessageBox, QScrollArea, QStyle, QGraphicsDropShadowEffect, QSlider, QGroupBox, QColorDialog, QDialog
)
from PySide6.QtCore import Qt, QDate, QSize, QTimer
from PySide6.QtCore import QItemSelectionModel
from PySide6.QtGui import QColor, QPixmap, QFont, QIcon

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    COLOR_PRIMARY, COLOR_PRIMARY_ALT, COLOR_ACCENT, COLOR_BG_LIGHT,
    COLOR_BG_GRAY, COLOR_TEXT_DARK, COLOR_TEXT_LIGHT,
    BORDER_RADIUS, SHADOW_BLUR, SHADOW_OFFSET_Y, SHADOW_OPACITY,
    SPACING_BASE, ROW_HEIGHT
)
from models.table import CustomModTable

# 延迟导入panels模块，兼容打包环境
def _import_panels():
    """导入panels模块中的所有类，兼容开发环境和打包环境"""
    try:
        from models.panels import (
            BinaryDisablePanel, BinarySelectionPanel, AdminPermissionPanel,
            BatchImportPanel, UnknownCategoryAuthorPanel, ConflictResolutionPanel,
            PriorityAdjustmentPanel, CategoryManagementPanel, ExportSelectionPanel
        )
        return (
            BinaryDisablePanel, BinarySelectionPanel, AdminPermissionPanel,
            BatchImportPanel, UnknownCategoryAuthorPanel, ConflictResolutionPanel,
            PriorityAdjustmentPanel, CategoryManagementPanel, ExportSelectionPanel
        )
    except ImportError:
        # 打包环境下的回退方案：尝试多种路径
        import importlib.util
        
        # 尝试多个可能的路径
        possible_paths = []
        
        # 1. 项目根目录下的models
        possible_paths.append(os.path.join(_project_root, 'models', 'panels.py'))
        
        # 2. 打包环境的临时目录（sys._MEIPASS）
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            possible_paths.append(os.path.join(sys._MEIPASS, 'models', 'panels.py'))
        
        # 3. 当前文件所在目录的models
        current_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths.append(os.path.join(current_dir, '..', 'models', 'panels.py'))
        possible_paths.append(os.path.join(os.path.dirname(current_dir), 'models', 'panels.py'))
        
        # 4. 尝试通过importlib查找
        try:
            import importlib
            panels_module = importlib.import_module('models.panels')
            return (
                panels_module.BinaryDisablePanel,
                panels_module.BinarySelectionPanel,
                panels_module.AdminPermissionPanel,
                panels_module.BatchImportPanel,
                panels_module.UnknownCategoryAuthorPanel,
                panels_module.ConflictResolutionPanel,
                panels_module.PriorityAdjustmentPanel,
                panels_module.CategoryManagementPanel,
                panels_module.ExportSelectionPanel
            )
        except:
            pass
        
        # 5. 尝试从文件加载
        for panels_path in possible_paths:
            panels_path = os.path.abspath(panels_path)
            if os.path.exists(panels_path):
                try:
                    spec = importlib.util.spec_from_file_location("models.panels", panels_path)
                    if spec and spec.loader:
                        panels_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(panels_module)
                        return (
                            panels_module.BinaryDisablePanel,
                            panels_module.BinarySelectionPanel,
                            panels_module.AdminPermissionPanel,
                            panels_module.BatchImportPanel,
                            panels_module.UnknownCategoryAuthorPanel,
                            panels_module.ConflictResolutionPanel,
                            panels_module.PriorityAdjustmentPanel,
                            panels_module.CategoryManagementPanel,
                            panels_module.ExportSelectionPanel
                        )
                except Exception as e:
                    continue
        
        # 如果所有方法都失败，抛出详细错误
        raise ImportError(
            f"无法找到 models.panels 模块。\n"
            f"已尝试的路径: {possible_paths}\n"
            f"项目根目录: {_project_root}\n"
            f"是否打包环境: {getattr(sys, 'frozen', False)}\n"
            f"临时目录: {getattr(sys, '_MEIPASS', 'N/A')}"
        )

# 立即导入所有panels类
(
    BinaryDisablePanel, BinarySelectionPanel, AdminPermissionPanel,
    BatchImportPanel, UnknownCategoryAuthorPanel, ConflictResolutionPanel,
    PriorityAdjustmentPanel, CategoryManagementPanel, ExportSelectionPanel
) = _import_panels()

from utils.animation_utils import AnimatedTransition

class MainWindow(QMainWindow):
    """Mod管理器主窗口"""
    
    def __init__(self):
        super().__init__()
        # 标记是否已显示过权限提示
        self._admin_permission_shown = False
        # 延迟初始化动画管理器，避免在窗口显示前出现问题
        self.animation_manager = None
        self.init_ui()
        # 在UI初始化后再初始化动画管理器
        try:
            self.animation_manager = AnimatedTransition(self)
        except Exception as e:
            print(f"[警告] 动画管理器初始化失败: {e}")
            # 创建一个简单的占位对象
            class DummyAnimationManager:
                def __init__(self):
                    self.parent = None
                    self.current_animation = None
                def transition_to(self, *args, **kwargs):
                    pass
            self.animation_manager = DummyAnimationManager()
    
    def get_background_path(self, filename):
        """获取背景图片路径，兼容开发环境和打包环境"""
        if getattr(sys, 'frozen', False):
            # 打包后的exe环境，使用PyInstaller的临时路径
            return os.path.join(sys._MEIPASS, "background", filename)
        else:
            # 开发环境
            project_root = self.get_project_root()
            return os.path.join(project_root, "background", filename)
    
    def get_project_root(self):
        """获取项目根目录，兼容开发环境和打包环境"""
        if getattr(sys, 'frozen', False):
            # 打包后的exe环境
            return os.path.dirname(sys.executable)
        else:
            # 开发环境
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # ui/main_window.py -> ui -> 项目根目录
            project_root = os.path.dirname(script_dir)
            return project_root
    
    def set_window_icon(self):
        """设置窗口图标，兼容开发环境和打包环境"""
        try:
            if getattr(sys, 'frozen', False):
                # 打包后的exe环境，使用PyInstaller的临时路径
                icon_path = os.path.join(sys._MEIPASS, "background", "title.png")
            else:
                # 开发环境
                icon_path = self.get_background_path("title.png")
            
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    icon = QIcon(pixmap)
                    self.setWindowIcon(icon)
        except Exception as e:
            # 图标设置失败不影响程序运行
            pass
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        # 设置窗口大小固定，不允许调整
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        # 设置窗口标志
        flags = Qt.WindowType.Window
        flags |= Qt.WindowType.WindowCloseButtonHint  
        flags |= Qt.WindowType.WindowMinimizeButtonHint
        self.setWindowFlags(flags)
        
        # 设置窗口图标
        self.set_window_icon()
        
        try:
            self.setup_ui()
        except Exception as e:
            # 如果setup_ui失败，至少让窗口能显示
            print(f"[错误] UI初始化失败: {e}")
            import traceback
            traceback.print_exc()
            # 创建一个简单的中央部件作为后备
            from PySide6.QtWidgets import QLabel
            error_label = QLabel(f"UI初始化失败: {e}\n请检查控制台输出")
            self.setCentralWidget(error_label)
    
    def setup_ui(self):
        """设置UI布局"""
        # 创建中央部件
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")  # 设置对象名称，用于样式选择器
        self.setCentralWidget(central_widget)
        
        # 应用窗口背景
        self.apply_window_background()
        
        # 创建主布局（垂直布局，包含顶栏、中间区域）
        main_layout = QVBoxLayout()
        main_layout.setSpacing(SPACING_BASE)  # 间距8px
        main_layout.setContentsMargins(SPACING_BASE, SPACING_BASE, SPACING_BASE, SPACING_BASE)  # 边距8px
        central_widget.setLayout(main_layout)
        
        # 1. 创建顶栏（左侧按钮组 + 右侧搜索设置区）
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        # 2. 创建中间区域（左侧Mod表格 + 右侧操作按钮栏）
        content_area = self.create_content_area()
        main_layout.addWidget(content_area, stretch=1)  # stretch=1让中间区域占据剩余空间
        
        # 3. 延迟加载已存在的模组（使用QTimer在窗口显示后再加载，避免阻塞窗口显示）
        QTimer.singleShot(100, self.load_existing_mods)
    
    def create_top_bar(self):
        """创建顶栏：左侧按钮组 + 右侧搜索设置区"""
        top_bar_widget = QWidget()
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setSpacing(SPACING_BASE)  # 组件之间的间距（8px）
        top_bar_layout.setContentsMargins(SPACING_BASE, SPACING_BASE, SPACING_BASE, SPACING_BASE)  # 内边距8px
        top_bar_widget.setLayout(top_bar_layout)
        
        # 设置顶栏最小高度为48px，允许拉伸
        top_bar_widget.setMinimumHeight(48)
        
        # 设置顶栏CSS样式：半透明毛玻璃效果，圆角，阴影
        top_bar_widget.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 180), stop:1 rgba(240, 240, 240, 160));
                border-radius: {BORDER_RADIUS}px;
            }}
        """)
        # 添加阴影效果
        top_bar_shadow = QGraphicsDropShadowEffect()
        top_bar_shadow.setBlurRadius(SHADOW_BLUR)
        top_bar_shadow.setXOffset(0)
        top_bar_shadow.setYOffset(SHADOW_OFFSET_Y)
        top_bar_shadow.setColor(QColor(0, 0, 0, SHADOW_OPACITY))
        top_bar_widget.setGraphicsEffect(top_bar_shadow)
        
        # 左侧按钮组
        left_button_group = self.create_left_button_group()
        top_bar_layout.addWidget(left_button_group)
        
        # 添加弹性空间（弹簧），将搜索设置区推到右侧
        top_bar_layout.addStretch()
        
        # 右侧搜索设置区
        right_search_area = self.create_right_search_area()
        top_bar_layout.addWidget(right_search_area)
        
        return top_bar_widget
    
    def create_left_button_group(self):
        """创建左侧按钮组：全部启用、全部禁用、批量导入"""
        button_group_widget = QWidget()
        button_group_layout = QHBoxLayout()
        button_group_layout.setSpacing(SPACING_BASE)  # 按钮之间的间距（8px）
        button_group_layout.setContentsMargins(0, 0, 0, 0)
        button_group_widget.setLayout(button_group_layout)
        
        # 添加三个按钮
        self.btn_enable_all = QPushButton("全部启用")
        self.btn_batch_disable = QPushButton("批量禁用")
        self.btn_organize = QPushButton("批量导入")
        
        # 设置按钮最小宽度为115px（96px的1.2倍）
        button_width = 115
        self.btn_enable_all.setMinimumWidth(button_width)
        self.btn_batch_disable.setMinimumWidth(button_width)
        self.btn_organize.setMinimumWidth(button_width)
        
        # 设置按钮CSS样式：卡片设计，圆角，悬停效果，70%半透明，文字居中
        button_style = f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 180);  /* 70%半透明 */
                border: 1px solid rgba(0, 0, 0, 10);
                border-radius: {BORDER_RADIUS - 2}px;
                color: {COLOR_TEXT_DARK};
                padding: 6px 12px;
                font-weight: 500;
                text-align: center;  /* 文字居中 */
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY};
                color: {COLOR_TEXT_LIGHT};
                border: 1px solid {COLOR_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_PRIMARY_ALT};
                border: 1px solid {COLOR_PRIMARY_ALT};
            }}
        """
        self.btn_enable_all.setStyleSheet(button_style)
        self.btn_batch_disable.setStyleSheet(button_style)
        self.btn_organize.setStyleSheet(button_style)
        
        # 将按钮添加到布局
        button_group_layout.addWidget(self.btn_enable_all)
        button_group_layout.addWidget(self.btn_batch_disable)
        button_group_layout.addWidget(self.btn_organize)
        
        # 连接按钮事件
        self.btn_enable_all.clicked.connect(self.enable_all_mods)
        self.btn_batch_disable.clicked.connect(self.batch_disable_mods)
        self.btn_organize.clicked.connect(self.batch_import_mods)
        
        return button_group_widget
    
    def enable_all_mods(self):
        """全部启用Mod（只启用当前未启用的mod）"""
        if hasattr(self, 'mod_table'):
            # 只启用当前未启用的mod
            for row, checkbox in self.mod_table.checkbox_widgets.items():
                if not checkbox.is_checked():  # 只处理未启用的mod
                    name_item = self.mod_table.item(row, 1)
                    if name_item:
                        mod_name = name_item.text()
                        checkbox.set_checked(True)
                        # 手动调用文件操作（因为set_checked使用了blockSignals）
                        self.log_mod_usage(mod_name, True)
                        self.apply_mod_to_game(mod_name, True)
            
            # 更新统计信息
            self.mod_table.statistics_changed.emit()
    
    def batch_disable_mods(self):
        """批量禁用Mod（支持二分禁用）"""
        if hasattr(self, 'mod_table'):
            result = self.mod_table.binary_disable_dialog()
            # 批量禁用结果，不打印详细信息
    
    def show_binary_disable_panel(self, panel):
        """显示批量禁用面板 - 悬浮方式"""
        # 不隐藏表格，保持原有界面
        # self.mod_table_widget.hide()  # 注释掉这行
        
        # 计算居中位置
        main_window_size = self.size()
        panel_size = panel.size()
        x = (main_window_size.width() - panel_size.width()) // 2
        y = (main_window_size.height() - panel_size.height()) // 2
        
        # 将面板悬浮显示在主窗口上
        panel.setParent(self)
        panel.move(x, y)
        panel.raise_()  # 提升到最顶层
        panel.show()
        
        # 保存面板引用
        self.binary_disable_panel = panel
        
        # 连接按钮事件
        panel.btn_all_disable.clicked.connect(lambda: self.handle_binary_disable_result(1))
        panel.btn_binary_disable.clicked.connect(lambda: self.handle_binary_disable_result(2))
        panel.btn_cancel.clicked.connect(lambda: self.hide_binary_disable_panel())
    
    def handle_binary_disable_result(self, result):
        """处理批量禁用结果"""
        if result == 1:  # 全部禁用
            self.mod_table.set_all_mods_enabled(False)
            self.hide_binary_disable_panel()
        elif result == 2:  # 二分禁用
            # 简化：直接隐藏当前面板，然后开始二分选择
            self.hide_binary_disable_panel()
            self.start_binary_selection()
        else:  # 其他情况
            self.hide_binary_disable_panel()
    
    def hide_binary_disable_panel(self):
        """隐藏批量禁用面板"""
        if hasattr(self, 'binary_disable_panel'):
            # 简化：直接隐藏，确保功能正常
            self.binary_disable_panel.hide()
            self.binary_disable_panel.deleteLater()
            delattr(self, 'binary_disable_panel')
    
    def batch_import_mods(self):
        """批量导入Mod"""
        # 显示批量导入面板
        panel = BatchImportPanel(self)
        self.show_batch_import_panel(panel)
    
    def show_batch_import_panel(self, panel):
        """显示批量导入面板 - 悬浮方式"""
        # 获取批量导入面板的主题设置并应用
        theme_settings = self.get_window_theme_settings('batch_import')
        panel.apply_background(theme_settings)
        
        # 计算居中位置
        main_window_size = self.size()
        panel_size = panel.size()
        x = (main_window_size.width() - panel_size.width()) // 2
        y = (main_window_size.height() - panel_size.height()) // 2
        
        # 将面板悬浮显示在主窗口上
        panel.setParent(self)
        panel.move(x, y)
        panel.raise_()  # 提升到最顶层
        panel.show()
        
        # 保存面板引用
        self.batch_import_panel = panel
        
        # 连接按钮事件
        panel.btn_hunt_box.clicked.connect(lambda: self.handle_batch_import_result(1))
        panel.btn_export_mods.clicked.connect(lambda: self.handle_batch_import_result(2))
        panel.btn_cancel.clicked.connect(lambda: self.handle_batch_import_result(0))
    
    def handle_batch_import_result(self, result):
        """处理批量导入结果"""
        # 先隐藏面板
        self.hide_batch_import_panel()
        
        if result == 1:  # 从狩技盒子导入
            self.import_from_hunt_box()
        elif result == 2:  # 从导出mods导入
            self.import_from_export_mods()
        # result == 0 表示取消，不需要处理
    
    def hide_batch_import_panel(self):
        """隐藏批量导入面板"""
        if hasattr(self, 'batch_import_panel'):
            self.batch_import_panel.hide()
            self.batch_import_panel.deleteLater()
            delattr(self, 'batch_import_panel')
    
    def import_from_export_mods(self):
        """从导出mods批量导入"""
        import shutil
        import xml.etree.ElementTree as ET
        
        # 打开文件夹选择对话框，选择导出目录
        export_dir = QFileDialog.getExistingDirectory(
            self,
            "选择导出目录（包含mods文件夹的目录）",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not export_dir:
            return
        
        # 查找mods文件夹
        mods_export_dir = os.path.join(export_dir, "mods")
        if not os.path.exists(mods_export_dir):
            QMessageBox.warning(self, "警告", f"在选择的目录中未找到mods文件夹：\n{mods_export_dir}")
            return
        
        # 获取项目根目录和mods目录
        project_root = self.get_project_root()
        mods_dir = os.path.join(project_root, "mods")
        os.makedirs(mods_dir, exist_ok=True)
        
        # 遍历导出目录中的所有mod文件夹
        imported_count = 0
        skipped_count = 0
        failed_mods = []
        
        for item in os.listdir(mods_export_dir):
            item_path = os.path.join(mods_export_dir, item)
            
            # 只处理文件夹
            if not os.path.isdir(item_path):
                continue
            
            # 跳过modinfo文件夹
            if item == "modinfo":
                continue
            
            try:
                # 检查目标文件夹是否已存在
                target_path = os.path.join(mods_dir, item)
                if os.path.exists(target_path):
                    # 如果已存在，询问是否覆盖
                    from PySide6.QtWidgets import QMessageBox
                    reply = QMessageBox.question(
                        self,
                        "确认覆盖",
                        f"Mod '{item}' 已存在，是否覆盖？",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        skipped_count += 1
                        continue
                    # 删除旧文件夹
                    shutil.rmtree(target_path)
                
                # 复制mod文件夹
                shutil.copytree(item_path, target_path)
                
                # 检查是否有modinfo.xml，如果没有则创建
                modinfo_dir = os.path.join(target_path, "modinfo")
                xml_file_path = os.path.join(modinfo_dir, "modinfo.xml")
                
                if not os.path.exists(xml_file_path):
                    # 读取mod文件夹名作为mod名称
                    mod_name = item.replace("_", " ")
                    
                    # 创建modinfo文件夹
                    os.makedirs(modinfo_dir, exist_ok=True)
                    
                    # 生成XML文件
                    xml_root = ET.Element("mod")
                    
                    name_elem = ET.SubElement(xml_root, "name")
                    name_elem.text = mod_name
                    
                    # 记录完整的文件结构
                    file_structure_elem = ET.SubElement(xml_root, "file_structure")
                    file_list = self.get_folder_files(target_path)
                    for file_path in file_list:
                        file_elem = ET.SubElement(file_structure_elem, "file")
                        file_elem.text = file_path
                        # 如果是文件（不是目录），记录文件大小和修改时间
                        if not file_path.endswith('/'):
                            # 将统一的分隔符转换为当前系统的分隔符，确保跨平台兼容
                            normalized_path = file_path.replace('/', os.sep).replace('\\', os.sep)
                            full_path = os.path.join(target_path, normalized_path)
                            if os.path.exists(full_path):
                                file_elem.set("size", str(os.path.getsize(full_path)))
                                file_elem.set("mtime", str(os.path.getmtime(full_path)))
                    
                    # 保存XML文件
                    tree = ET.ElementTree(xml_root)
                    tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
                else:
                    # 如果已有XML，读取mod名称等信息
                    try:
                        tree = ET.parse(xml_file_path)
                        root = tree.getroot()
                        name_elem = root.find('.//name')
                        if name_elem is not None and name_elem.text:
                            mod_name = name_elem.text
                        else:
                            mod_name = item.replace("_", " ")
                    except:
                        mod_name = item.replace("_", " ")
                
                # 读取分类和作者信息
                category = ""
                author = ""
                try:
                    tree = ET.parse(xml_file_path)
                    root = tree.getroot()
                    category_elem = root.find('.//category')
                    if category_elem is not None and category_elem.text:
                        category = category_elem.text
                    author_elem = root.find('.//author')
                    if author_elem is not None and author_elem.text:
                        author = author_elem.text
                except:
                    pass
                
                # 检查并处理未知的分类和作者
                original_category = category
                original_author = author
                category, author = self.check_and_handle_unknown_category_author(category, author)
                
                # 如果分类或作者被忽略（置空），需要更新XML文件
                if category != original_category or author != original_author:
                    try:
                        tree = ET.parse(xml_file_path)
                        root = tree.getroot()
                        
                        # 更新或删除category
                        category_elem = root.find('.//category')
                        if category:
                            if category_elem is not None:
                                category_elem.text = category
                            else:
                                category_elem = ET.SubElement(root, "category")
                                category_elem.text = category
                        else:
                            if category_elem is not None:
                                root.remove(category_elem)
                        
                        # 更新或删除author
                        author_elem = root.find('.//author')
                        if author:
                            if author_elem is not None:
                                author_elem.text = author
                            else:
                                author_elem = ET.SubElement(root, "author")
                                author_elem.text = author
                        else:
                            if author_elem is not None:
                                root.remove(author_elem)
                        
                        # 保存更新后的XML
                        tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
                    except Exception as e:
                        print(f"[警告] 更新XML文件失败: {e}")
                
                # 添加到表格（不再检查未知项，因为已经在上面检查过了）
                self.add_mod_to_table(mod_name, category, author, check_unknown=False)
                # 批量导入时也记录导入时间
                import time
                try:
                    mod_states = self.load_mod_states()
                    mod_state = mod_states.get(mod_name, {})
                    if isinstance(mod_state, bool):
                        mod_state = {"enabled": mod_state, "favorite": False, "ignored": False}
                    if "import_time" not in mod_state:
                        mod_state["import_time"] = time.time()
                        mod_states[mod_name] = mod_state
                        self._save_mod_states_direct(mod_states)
                except:
                    pass
                imported_count += 1
                
            except Exception as e:
                failed_mods.append(f"{item}: {str(e)}")
                print(f"[失败] 导入mod失败 {item}: {str(e)}")
        
        # 显示结果
        result_message = f"批量导入完成！\n\n成功导入: {imported_count} 个\n跳过: {skipped_count} 个"
        if failed_mods:
            result_message += f"\n失败: {len(failed_mods)} 个"
            result_message += "\n\n失败的mod:\n" + "\n".join(failed_mods[:10])  # 最多显示10个
            if len(failed_mods) > 10:
                result_message += f"\n... 还有 {len(failed_mods) - 10} 个失败"
        
        QMessageBox.information(self, "批量导入结果", result_message)
        
        # 刷新mod列表
        self.refresh_mod_list()
    
    def import_from_hunt_box(self):
        """从狩技盒子批量导入"""
        import shutil
        import xml.etree.ElementTree as ET
        
        # 打开文件夹选择对话框，选择狩技盒子的模组文件夹
        hunt_box_dir = QFileDialog.getExistingDirectory(
            self,
            "选择狩技盒子的模组文件夹（包含序号文件夹的目录）",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not hunt_box_dir:
            return
        
        # 获取项目根目录和mods目录
        project_root = self.get_project_root()
        mods_dir = os.path.join(project_root, "mods")
        os.makedirs(mods_dir, exist_ok=True)
        
        # 遍历目录中的所有序号文件夹
        imported_count = 0
        skipped_count = 0
        failed_mods = []
        skipped_details = []  # 记录跳过的详细信息
        
        # 先列出所有找到的文件夹
        found_folders = []
        for item in os.listdir(hunt_box_dir):
            item_path = os.path.join(hunt_box_dir, item)
            if os.path.isdir(item_path):
                found_folders.append(item)
        
        print(f"[调试] 在目录中找到 {len(found_folders)} 个文件夹: {found_folders}")
        
        for item in os.listdir(hunt_box_dir):
            item_path = os.path.join(hunt_box_dir, item)
            
            # 只处理文件夹
            if not os.path.isdir(item_path):
                continue
            
            # 只处理数字文件夹（序号文件夹）
            if not item.isdigit():
                skipped_details.append(f"{item} (不是数字文件夹)")
                continue
            
            try:
                # 检查是否有 files 文件夹和 info.xml
                file_folder = os.path.join(item_path, "files")
                info_xml_path = os.path.join(item_path, "info.xml")
                
                print(f"[调试] 检查文件夹 {item}:")
                print(f"  - files文件夹存在: {os.path.exists(file_folder)}")
                print(f"  - files是目录: {os.path.isdir(file_folder) if os.path.exists(file_folder) else False}")
                print(f"  - info.xml存在: {os.path.exists(info_xml_path)}")
                
                if not os.path.exists(file_folder) or not os.path.isdir(file_folder):
                    # 跳过没有files文件夹的
                    skipped_details.append(f"{item} (缺少files文件夹)")
                    print(f"[跳过] {item}: 缺少files文件夹")
                    continue
                
                if not os.path.exists(info_xml_path):
                    # 跳过没有info.xml的
                    skipped_details.append(f"{item} (缺少info.xml)")
                    print(f"[跳过] {item}: 缺少info.xml")
                    continue
                
                # 读取info.xml获取mod信息
                mod_name = item  # 默认使用序号作为名称
                category = ""
                author = ""
                version = ""
                
                try:
                    tree = ET.parse(info_xml_path)
                    root = tree.getroot()
                    
                    # 查找mod名称（优先使用moduleName，其次使用name）
                    name_elem = root.find('.//moduleName')
                    if name_elem is not None and name_elem.text:
                        mod_name = name_elem.text.strip()
                    else:
                        name_elem = root.find('.//name')
                        if name_elem is not None and name_elem.text:
                            mod_name = name_elem.text.strip()
                    
                    # 查找作者
                    author_elem = root.find('.//author')
                    if author_elem is not None and author_elem.text:
                        author = author_elem.text.strip()
                    
                    # 查找mod类型（作为分类）
                    mod_type_elem = root.find('.//modType')
                    if mod_type_elem is not None and mod_type_elem.text:
                        category = mod_type_elem.text.strip()
                    
                    # 查找版本
                    version_elem = root.find('.//version')
                    if version_elem is not None and version_elem.text:
                        version = version_elem.text.strip()
                except Exception as e:
                    print(f"[警告] 读取info.xml失败 {item}: {str(e)}")
                    # 继续使用默认值
                
                # 使用mod名称创建目标文件夹名
                mod_folder_name = mod_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
                target_path = os.path.join(mods_dir, mod_folder_name)
                
                # 检查目标文件夹是否已存在
                if os.path.exists(target_path):
                    # 如果已存在，询问是否覆盖
                    reply = QMessageBox.question(
                        self,
                        "确认覆盖",
                        f"Mod '{mod_name}' 已存在，是否覆盖？",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        skipped_count += 1
                        continue
                    # 删除旧文件夹
                    shutil.rmtree(target_path)
                
                # 复制files文件夹的内容到目标路径
                # 先创建目标文件夹
                os.makedirs(target_path, exist_ok=True)
                
                # 复制files文件夹中的所有内容
                for file_item in os.listdir(file_folder):
                    source_item_path = os.path.join(file_folder, file_item)
                    target_item_path = os.path.join(target_path, file_item)
                    
                    if os.path.isdir(source_item_path):
                        shutil.copytree(source_item_path, target_item_path)
                    else:
                        shutil.copy2(source_item_path, target_item_path)
                
                # 检查并处理未知的分类和作者
                original_category = category
                original_author = author
                category, author = self.check_and_handle_unknown_category_author(category, author)
                
                # 创建modinfo文件夹
                modinfo_dir = os.path.join(target_path, "modinfo")
                os.makedirs(modinfo_dir, exist_ok=True)
                
                # 生成modinfo.xml文件
                xml_root = ET.Element("mod")
                
                name_elem = ET.SubElement(xml_root, "name")
                name_elem.text = mod_name
                
                if category:
                    category_elem = ET.SubElement(xml_root, "category")
                    category_elem.text = category
                
                if author:
                    author_elem = ET.SubElement(xml_root, "author")
                    author_elem.text = author
                
                if version:
                    version_elem = ET.SubElement(xml_root, "version")
                    version_elem.text = version
                
                # 记录完整的文件结构
                file_structure_elem = ET.SubElement(xml_root, "file_structure")
                file_list = self.get_folder_files(target_path)
                for file_path in file_list:
                    file_elem = ET.SubElement(file_structure_elem, "file")
                    file_elem.text = file_path
                    # 如果是文件（不是目录），记录文件大小和修改时间
                    if not file_path.endswith('/'):
                        # 将统一的分隔符转换为当前系统的分隔符，确保跨平台兼容
                        normalized_path = file_path.replace('/', os.sep).replace('\\', os.sep)
                        full_path = os.path.join(target_path, normalized_path)
                        if os.path.exists(full_path):
                            file_elem.set("size", str(os.path.getsize(full_path)))
                            file_elem.set("mtime", str(os.path.getmtime(full_path)))
                
                # 保存XML文件
                xml_file_path = os.path.join(modinfo_dir, "modinfo.xml")
                tree = ET.ElementTree(xml_root)
                tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
                
                # 添加到表格（不再检查未知项，因为已经在上面检查过了）
                self.add_mod_to_table(mod_name, category, author, check_unknown=False)
                # 批量导入时也记录导入时间
                import time
                try:
                    mod_states = self.load_mod_states()
                    mod_state = mod_states.get(mod_name, {})
                    if isinstance(mod_state, bool):
                        mod_state = {"enabled": mod_state, "favorite": False, "ignored": False}
                    if "import_time" not in mod_state:
                        mod_state["import_time"] = time.time()
                        mod_states[mod_name] = mod_state
                        self._save_mod_states_direct(mod_states)
                except:
                    pass
                imported_count += 1
                
            except Exception as e:
                failed_mods.append(f"{item}: {str(e)}")
                print(f"[失败] 导入mod失败 {item}: {str(e)}")
        
        # 显示结果
        result_message = f"批量导入完成！\n\n成功导入: {imported_count} 个\n跳过: {skipped_count} 个"
        
        if skipped_details:
            result_message += f"\n\n跳过的文件夹 ({len(skipped_details)} 个):\n" + "\n".join(skipped_details[:10])
            if len(skipped_details) > 10:
                result_message += f"\n... 还有 {len(skipped_details) - 10} 个被跳过"
        
        if failed_mods:
            result_message += f"\n\n失败: {len(failed_mods)} 个"
            result_message += "\n失败的mod:\n" + "\n".join(failed_mods[:10])  # 最多显示10个
            if len(failed_mods) > 10:
                result_message += f"\n... 还有 {len(failed_mods) - 10} 个失败"
        
        if imported_count == 0 and skipped_count == 0 and not failed_mods:
            result_message = f"未找到任何可导入的mod！\n\n选择的目录: {hunt_box_dir}\n\n请确认：\n1. 目录中包含序号文件夹（如1001、1002等）\n2. 每个序号文件夹中包含files文件夹和info.xml文件"
        
        QMessageBox.information(self, "批量导入结果", result_message)
        
        # 刷新mod列表
        self.refresh_mod_list()
    
    def start_binary_selection(self):
        """开始二分选择"""
        current_enabled = self.mod_table.get_enabled_mods()
        
        if not current_enabled:
            return
        
        # 创建新的二分选择面板
        selection_panel = BinarySelectionPanel(current_enabled, self)
        
        # 如果已有面板，先隐藏并删除
        if hasattr(self, 'binary_selection_panel'):
            self.binary_selection_panel.hide()
            self.binary_selection_panel.deleteLater()
        
        # 计算居中位置
        main_window_size = self.size()
        panel_size = selection_panel.size()
        x = (main_window_size.width() - panel_size.width()) // 2
        y = (main_window_size.height() - panel_size.height()) // 2
        
        # 将新面板悬浮显示在主窗口上
        selection_panel.setParent(self)
        selection_panel.move(x, y)
        selection_panel.raise_()  # 提升到最顶层
        selection_panel.show()
        
        # 保存面板引用
        self.binary_selection_panel = selection_panel
        
        # 连接按钮事件
        selection_panel.btn_front_half.clicked.connect(lambda: self.handle_binary_selection_result(1))
        selection_panel.btn_back_half.clicked.connect(lambda: self.handle_binary_selection_result(2))
        selection_panel.btn_cancel_binary.clicked.connect(lambda: self.handle_binary_selection_result(0))
        
        # 如果没有启用的Mod了，禁用前半和后半按钮
        if len(current_enabled) <= 1:
            selection_panel.btn_front_half.setEnabled(False)
            selection_panel.btn_back_half.setEnabled(False)
            selection_panel.btn_front_half.setStyleSheet("""
                QPushButton {
                    background-color: rgba(200, 200, 200, 200);
                    border: 1px solid #CCCCCC;
                    border-radius: 4px;
                    color: #999999;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 15px;
                    text-align: center;
                }
            """)
            selection_panel.btn_back_half.setStyleSheet("""
                QPushButton {
                    background-color: rgba(200, 200, 200, 200);
                    border: 1px solid #CCCCCC;
                    border-radius: 4px;
                    color: #999999;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 15px;
                    text-align: center;
                }
            """)
    
    def handle_binary_selection_result(self, result):
        """处理二分选择结果"""
        # 先隐藏当前面板
        self.hide_binary_selection_panel()
        
        current_enabled = self.mod_table.get_enabled_mods()
        
        if result == 1:  # 前半部分
            half_count = len(current_enabled) // 2
            mods_to_disable = current_enabled[:half_count]
        elif result == 2:  # 后半部分
            half_count = len(current_enabled) // 2
            mods_to_disable = current_enabled[half_count:]
        else:  # 取消二分
            # 恢复保存的配置
            self.mod_table.restore_saved_config()
            return
        
        # 禁用选中的Mod
        for mod_name in mods_to_disable:
            self.mod_table.set_mod_enabled(mod_name, False)
        
        # 检查是否还有启用的Mod
        remaining_enabled = self.mod_table.get_enabled_mods()
        
        # 如果还有启用的Mod，继续二分选择
        if remaining_enabled:
            self.start_binary_selection()
    
    def hide_binary_selection_panel(self):
        """隐藏二分选择面板"""
        if hasattr(self, 'binary_selection_panel'):
            # 简化：直接隐藏，确保功能正常
            self.binary_selection_panel.hide()
            self.binary_selection_panel.deleteLater()
            delattr(self, 'binary_selection_panel')
    
    def show_advanced_settings_panel(self):
        """显示高级设置面板"""
        if hasattr(self, 'advanced_settings_panel') and self.advanced_settings_panel:
            # 使用动画显示已存在的面板
            self._show_advanced_settings_panel_with_animation()
            return
        
        # 创建高级设置面板 - 完全复制导入模组的创建方式
        self.advanced_settings_panel = self.create_advanced_settings_panel()
        
        # 加载当前设置
        current_settings = self.load_advanced_settings()
        self.path_input.setText(current_settings.get('game_path', ''))
        self.sandbox_checkbox.setChecked(current_settings.get('sandbox_mode', False))
        if hasattr(self, 'virtual_mapping_checkbox'):
            self.virtual_mapping_checkbox.setChecked(current_settings.get('virtual_mapping', False))
        
        # 使用动画显示面板
        self._show_advanced_settings_panel_with_animation()
    
    def _show_advanced_settings_panel_with_animation(self):
        """使用动画显示高级设置面板"""
        # 使用统一的动画接口显示面板 - 覆盖主窗口
        self.show_panel_with_animation(self.advanced_settings_panel, "scale_in", 500, position_center=False)
    
    def create_advanced_settings_panel(self):
        """创建高级设置面板 - 完全复制导入模组的create_import_panel方法"""
        advanced_panel = QWidget()
        advanced_panel.setObjectName("advancedSettingsPanel")
        
        # 设置窗口大小：和主窗口一样大
        main_window_size = self.size()
        window_width = main_window_size.width()
        window_height = main_window_size.height()
        advanced_panel.setFixedSize(window_width, window_height)
        
        # 设置窗口样式：可拖动，类似传统信息系统窗口，提高不透明度
        advanced_panel.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)
        advanced_panel.setStyleSheet("""
            QWidget#advancedSettingsPanel {
                background-color: rgba(255, 192, 203, 240);  /* 提高不透明度 */
                border: 2px solid #8B4513;
                border-radius: 8px;
            }
        """)
        
        # 设置背景图
        self.apply_advanced_settings_background(advanced_panel)
        
        # 垂直布局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        advanced_panel.setLayout(layout)
        
        # 标题栏（可拖动）- 完全复制导入模组的标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(35)
        title_bar.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 182, 193, 180);
                border-radius: 6px;
                border-bottom: 1px solid #8B4513;
            }
        """)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(15, 8, 15, 8)
        title_bar.setLayout(title_layout)
        
        # 标题
        title = QLabel("高级设置")
        title.setStyleSheet("""
            QLabel {
                color: #9D00FF;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        
        # 关闭按钮
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(25, 25)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 180);
                border: 1px solid #8B4513;
                border-radius: 3px;
                color: #8B4513;
                font-size: 16px;
                font-weight: bold;
                margin-top: -4px;
            }
            QPushButton:hover {
                background-color: #8B4513;
                color: white;
            }
        """)
        close_btn.clicked.connect(self.hide_advanced_settings_panel)
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(close_btn)
        layout.addWidget(title_bar)
        
        # 高级设置表单
        form_widget = QWidget()
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_widget.setLayout(form_layout)
        
        # 统一样式标签 - 完全复制导入模组的样式
        label_style = """
            QLabel {
                color: #9D00FF;
                font-size: 15px;
                font-weight: bold;
                min-width: 50px;
                text-align: right;
            }
        """
        
        # 游戏根目录路径
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("请选择游戏根目录...")
        self.path_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                padding: 7px;
                color: #9D00FF;
                font-size: 14px;
            }
        """)
        
        path_label = QLabel("游戏根目录:")
        path_label.setStyleSheet(label_style)
        
        # 使用水平布局来对齐标签和输入框
        path_layout = QHBoxLayout()
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(15)
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input, stretch=1)
        
        # 浏览按钮
        browse_btn = QPushButton("浏览")
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #9D00FF;
                font-size: 14px;
                font-weight: bold;
                padding: 7px 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """)
        browse_btn.clicked.connect(self.browse_advanced_path)
        path_layout.addWidget(browse_btn)
        
        form_layout.addRow(path_layout)
        
        # 沙盒模式开关
        sandbox_widget = QWidget()
        sandbox_layout = QHBoxLayout()
        sandbox_layout.setContentsMargins(0, 0, 0, 0)
        sandbox_layout.setSpacing(15)
        sandbox_widget.setLayout(sandbox_layout)
        
        sandbox_label = QLabel("沙盒模式:")
        sandbox_label.setStyleSheet(label_style)
        
        self.sandbox_checkbox = QCheckBox()
        self.sandbox_checkbox.setStyleSheet("""
            QCheckBox {
                color: #9D00FF;
                font-size: 14px;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #8B4513;
                border-radius: 2px;
                background-color: rgba(255, 255, 255, 200);
            }
            QCheckBox::indicator:checked {
                background-color: rgba(255, 182, 193, 200);
                border-color: #8B4513;
            }
        """)
        
        sandbox_desc = QLabel("启用沙盒模式运行游戏")
        sandbox_desc.setStyleSheet("""
            QLabel {
                color: #9D00FF;
                font-size: 13px;
            }
        """)
        
        sandbox_layout.addWidget(sandbox_label)
        sandbox_layout.addWidget(self.sandbox_checkbox)
        sandbox_layout.addWidget(sandbox_desc)
        sandbox_layout.addStretch()
        
        form_layout.addRow(sandbox_widget)
        
        # 虚拟映射开关
        virtual_mapping_widget = QWidget()
        virtual_mapping_layout = QHBoxLayout()
        virtual_mapping_layout.setContentsMargins(0, 0, 0, 0)
        virtual_mapping_layout.setSpacing(15)
        virtual_mapping_widget.setLayout(virtual_mapping_layout)
        
        virtual_mapping_label = QLabel("使用虚拟映射:")
        virtual_mapping_label.setStyleSheet(label_style)
        
        self.virtual_mapping_checkbox = QCheckBox()
        self.virtual_mapping_checkbox.setStyleSheet("""
            QCheckBox {
                color: #9D00FF;
                font-size: 14px;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #8B4513;
                border-radius: 2px;
                background-color: rgba(255, 255, 255, 200);
            }
            QCheckBox::indicator:checked {
                background-color: rgba(255, 182, 193, 200);
                border-color: #8B4513;
            }
        """)
        
        virtual_mapping_desc = QLabel("使用符号链接代替物理复制（节省磁盘空间）")
        virtual_mapping_desc.setStyleSheet("""
            QLabel {
                color: #9D00FF;
                font-size: 13px;
            }
        """)
        
        virtual_mapping_layout.addWidget(virtual_mapping_label)
        virtual_mapping_layout.addWidget(self.virtual_mapping_checkbox)
        virtual_mapping_layout.addWidget(virtual_mapping_desc)
        virtual_mapping_layout.addStretch()
        
        form_layout.addRow(virtual_mapping_widget)
        
        layout.addWidget(form_widget)
        
        # 按钮区域 - 完全复制导入模组的按钮样式
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch()
        
        self.btn_save = QPushButton("保存")
        self.btn_cancel = QPushButton("取消")
        
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #9D00FF;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """
        
        self.btn_save.setStyleSheet(button_style)
        self.btn_cancel.setStyleSheet(button_style)
        
        self.btn_save.clicked.connect(self.handle_advanced_settings_save)
        self.btn_cancel.clicked.connect(self.hide_advanced_settings_panel)
        
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)
        layout.addLayout(button_layout)
        
        return advanced_panel

    def apply_advanced_settings_background(self, panel):
        """应用高级设置背景图 - 应用主题设置中的颜色和透明度"""
        # 获取高级设置面板的主题设置
        theme_settings = self.get_window_theme_settings('advanced_settings')
        primary_color = theme_settings['primary_color']
        background_opacity = theme_settings['background_opacity']
        
        # 将颜色转换为RGB，并应用透明度
        try:
            color = QColor(primary_color)
            r, g, b = color.red(), color.green(), color.blue()
        except:
            r, g, b = 255, 192, 203  # 默认粉色
        
        import os
        # 背景图片路径：项目根目录/background/AdvancedSettingsPanel.png
        background_image = self.get_background_path("AdvancedSettingsPanel.png")
        
        # 检查文件是否存在，如果存在则使用背景图片
        if os.path.exists(background_image):
            # 将Windows路径中的反斜杠转换为正斜杠，直接使用本地路径
            background_url = background_image.replace("\\", "/")
            
            # 构建高级设置面板背景样式（应用主题颜色和透明度）
            panel_style = f"""
                QWidget#advancedSettingsPanel {{
                    background-color: rgba({r}, {g}, {b}, {background_opacity});
                    background-image: url('{background_url}');
                    background-position: center;
                    background-repeat: no-repeat;
                    border: 2px solid #8B4513;
                    border-radius: 8px;
                }}
            """
            panel.setStyleSheet(panel_style)
        else:
            # 如果没有背景图，只应用颜色和透明度
            panel_style = f"""
                QWidget#advancedSettingsPanel {{
                    background-color: rgba({r}, {g}, {b}, {background_opacity});
                    border: 2px solid #8B4513;
                    border-radius: 8px;
                }}
            """
            panel.setStyleSheet(panel_style)
    
    def browse_advanced_path(self):
        """浏览路径"""
        from PySide6.QtWidgets import QFileDialog
        folder_path = QFileDialog.getExistingDirectory(self, "选择游戏根目录")
        if folder_path:
            self.path_input.setText(folder_path)
    
    def handle_advanced_settings_save(self):
        """处理高级设置保存"""
        if hasattr(self, 'advanced_settings_panel'):
            # 获取当前设置
            current_settings = self.load_advanced_settings()
            old_virtual_mapping = current_settings.get('virtual_mapping', False)
            new_virtual_mapping = self.virtual_mapping_checkbox.isChecked()
            
            settings = {
                'game_path': self.path_input.text(),
                'sandbox_mode': self.sandbox_checkbox.isChecked(),
                'virtual_mapping': new_virtual_mapping
            }
            
            # 检测虚拟映射状态变化
            if not old_virtual_mapping and new_virtual_mapping:
                # 从关闭变为开启：总是显示提示窗口
                enabled_mods = self.mod_table.get_enabled_mods()
                if enabled_mods:
                    # 有启用的mod，询问是否先禁用
                    reply = QMessageBox.warning(
                        self,
                        "启用虚拟映射",
                        "虚拟映射功能需要管理员权限才能创建符号链接。\n\n"
                        "为了防止难以预料的错误产生，请确保开启时所有mod已禁用，以后以符号链接方式重新启用！\n\n"
                        "检测到当前有启用的mod，是否先禁用所有mod？",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    if reply == QMessageBox.Yes:
                        # 禁用所有mod
                        self.mod_table.set_all_mods_enabled(False)
                    else:
                        # 用户选择不禁用，取消保存
                        return
                else:
                    # 没有启用的mod，只显示提示信息
                    QMessageBox.information(
                        self,
                        "启用虚拟映射",
                        "虚拟映射功能需要管理员权限才能创建符号链接。\n\n"
                        "为了防止难以预料的错误产生，请确保开启时所有mod已禁用，以后以符号链接方式重新启用！"
                    )
            elif old_virtual_mapping and not new_virtual_mapping:
                # 从开启变为关闭：删除所有符号链接，复制文件到游戏根目录
                self.convert_symlinks_to_files()
            
            self.save_advanced_settings(settings)
            self.hide_advanced_settings_panel()
    
    def hide_advanced_settings_panel(self):
        """隐藏高级设置面板"""
        if hasattr(self, 'advanced_settings_panel'):
            # 直接隐藏，不使用动画
            self.advanced_settings_panel.hide()
            self.advanced_settings_panel.deleteLater()
            delattr(self, 'advanced_settings_panel')
    
    def show_theme_settings_panel(self):
        """显示主题设置面板"""
        if hasattr(self, 'theme_settings_panel') and self.theme_settings_panel:
            self._show_theme_settings_panel_with_animation()
            return
        
        # 创建主题设置面板
        self.theme_settings_panel = self.create_theme_settings_panel()
        
        # 加载当前主题设置（在面板创建后，属性已经存在）
        current_theme = self.load_theme_settings()
        
        # 为每个窗口加载设置（确保theme_window_groups已创建）
        if hasattr(self, 'theme_window_groups') and self.theme_window_groups:
            for key, widgets in self.theme_window_groups.items():
                window_settings = current_theme.get(key, {})
                if "primary_color" in widgets:
                    widgets["primary_color"].setText(window_settings.get('primary_color', '#FFC0CB'))
                if "text_color" in widgets:
                    widgets["text_color"].setText(window_settings.get('text_color', '#8B4513'))
                if "opacity" in widgets:
                    default_opacity = 240
                    if key == "import_panel":
                        default_opacity = 255
                    elif key == "batch_import":
                        default_opacity = 120
                    opacity_value = window_settings.get('background_opacity', default_opacity)
                    widgets["opacity"].setValue(opacity_value)
                    if "opacity_label" in widgets:
                        widgets["opacity_label"].setText(str(opacity_value))
        
        # 使用动画显示面板
        self._show_theme_settings_panel_with_animation()
    
    def _show_theme_settings_panel_with_animation(self):
        """使用动画显示主题设置面板"""
        self.show_panel_with_animation(self.theme_settings_panel, "slide_in_from_bottom", 500, position_center=False)
    
    def hide_theme_settings_panel(self):
        """隐藏主题设置面板（直接关闭，无动画）"""
        if hasattr(self, 'theme_settings_panel') and self.theme_settings_panel:
            panel = self.theme_settings_panel
            panel.hide()
            panel.deleteLater()
            if hasattr(self, 'theme_settings_panel'):
                delattr(self, 'theme_settings_panel')
    
    def create_theme_settings_panel(self):
        """创建主题设置面板 - 参考高级设置面板"""
        theme_panel = QWidget()
        theme_panel.setObjectName("themeSettingsPanel")
        
        # 设置窗口大小：和主窗口一样大
        main_window_size = self.size()
        window_width = main_window_size.width()
        window_height = main_window_size.height()
        theme_panel.setFixedSize(window_width, window_height)
        
        # 设置窗口样式
        theme_panel.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)
        
        # 设置背景图（会应用主题设置中的颜色和透明度）
        self.apply_theme_settings_background(theme_panel)
        
        # 垂直布局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        theme_panel.setLayout(layout)
        
        # 标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(35)
        title_bar.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 182, 193, 180);
                border-radius: 6px;
                border-bottom: 1px solid #8B4513;
            }
        """)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(15, 8, 15, 8)
        title_bar.setLayout(title_layout)
        
        # 标题
        title = QLabel("主题设置")
        title.setStyleSheet("""
            QLabel {
                color: #9D00FF;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        
        # 关闭按钮
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(25, 25)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 180);
                border: 1px solid #8B4513;
                border-radius: 3px;
                color: #8B4513;
                font-size: 16px;
                font-weight: bold;
                margin-top: -4px;
            }
            QPushButton:hover {
                background-color: #8B4513;
                color: white;
            }
        """)
        close_btn.clicked.connect(self.hide_theme_settings_panel)
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(close_btn)
        layout.addWidget(title_bar)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 100);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #9D00FF;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #7A00CC;
            }
        """)
        
        # 可折叠窗口列表容器
        windows_container = QWidget()
        windows_container.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)
        windows_layout = QVBoxLayout()
        windows_layout.setSpacing(15)
        windows_layout.setContentsMargins(15, 15, 15, 15)
        windows_container.setLayout(windows_layout)
        
        # 定义可配置的窗口列表（根据实际窗口属性定制）
        self.theme_window_groups = {}
        window_configs = [
            {
                "name": "主窗口", 
                "key": "main_window",
                "properties": ["background_color", "text_color"]  # 只有背景色和文字颜色
            },
            {
                "name": "导入/编辑模组面板", 
                "key": "import_panel",
                "properties": ["background_color", "background_opacity", "text_color"]  # 有背景色、透明度、文字颜色，没有毛玻璃
            },
            {
                "name": "高级设置面板", 
                "key": "advanced_settings",
                "properties": ["background_color", "background_opacity", "text_color"]  # 有背景色、透明度、文字颜色，没有毛玻璃
            },
            {
                "name": "主题设置面板", 
                "key": "theme_settings",
                "properties": ["background_color", "background_opacity", "text_color"]  # 有背景色、透明度、文字颜色，没有毛玻璃
            },
            {
                "name": "批量导入面板", 
                "key": "batch_import",
                "properties": ["background_color", "background_opacity", "text_color"]  # 有背景色、透明度、文字颜色，没有毛玻璃
            },
        ]
        
        # 统一样式标签（粉色）
        label_style = """
            QLabel {
                color: #FFC0CB;
                font-size: 15px;
                font-weight: bold;
                min-width: 50px;
            }
        """
        
        # 为每个窗口创建可折叠组
        for config in window_configs:
            group = QGroupBox(config["name"])
            group.setCheckable(True)
            group.setChecked(False)  # 默认折叠
            group.setFlat(False)
            group.setStyleSheet("""
                QGroupBox {
                    color: #FFC0CB;
                    font-size: 16px;
                    font-weight: bold;
                    border: 2px solid #8B4513;
                    border-radius: 6px;
                    margin-top: 10px;
                    padding-top: 10px;
                    background-color: transparent;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                    color: #FFC0CB;
                }
                QGroupBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 1px solid #8B4513;
                    border-radius: 2px;
                    background-color: rgba(255, 255, 255, 200);
                }
                QGroupBox::indicator:checked {
                    background-color: rgba(255, 192, 203, 200);
                    border-color: #8B4513;
                }
            """)
            
            # 窗口样式表单
            form_layout = QFormLayout()
            form_layout.setSpacing(12)
            form_layout.setContentsMargins(15, 20, 15, 15)
            
            # 根据窗口属性动态创建配置项
            properties = config.get("properties", [])
            widgets_dict = {}
            
            # 背景颜色（如果窗口有此属性）
            if "background_color" in properties:
                primary_color_widget = QWidget()
                primary_color_layout = QHBoxLayout()
                primary_color_layout.setContentsMargins(0, 0, 0, 0)
                primary_color_layout.setSpacing(5)
                primary_color_widget.setLayout(primary_color_layout)
                
                primary_color_input = QLineEdit()
                primary_color_input.setPlaceholderText("#FFC0CB")
                primary_color_input.setReadOnly(True)  # 只读，只能通过颜色选择器修改
                primary_color_input.setStyleSheet("""
                    QLineEdit {
                        background-color: rgba(255, 255, 255, 200);
                        border: 1px solid #8B4513;
                        border-radius: 4px;
                        padding: 7px;
                        color: #000000;
                        font-size: 14px;
                    }
                """)
                
                def open_primary_color_dialog():
                    current_color = primary_color_input.text().strip() or "#FFC0CB"
                    try:
                        color = QColor(current_color)
                    except:
                        color = QColor(255, 192, 203)  # #FFC0CB
                    
                    dialog = QColorDialog(color, self)
                    dialog.setWindowTitle("选择背景颜色")
                    if dialog.exec():
                        selected_color = dialog.selectedColor()
                        color_hex = selected_color.name()
                        primary_color_input.setText(color_hex)
                        # 更新输入框背景色预览
                        primary_color_input.setStyleSheet(f"""
                            QLineEdit {{
                                background-color: {color_hex};
                                border: 1px solid #8B4513;
                                border-radius: 4px;
                                padding: 7px;
                                color: #000000;
                                font-size: 14px;
                            }}
                        """)
                
                primary_color_btn = QPushButton("选择颜色")
                primary_color_btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255, 255, 255, 200);
                        border: 1px solid #8B4513;
                        border-radius: 4px;
                        color: #FFC0CB;
                        font-size: 14px;
                        font-weight: bold;
                        padding: 7px 15px;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 192, 203, 200);
                        color: white;
                    }
                """)
                primary_color_btn.clicked.connect(open_primary_color_dialog)
                
                primary_color_layout.addWidget(primary_color_input, stretch=1)
                primary_color_layout.addWidget(primary_color_btn)
                
                primary_color_label = QLabel("背景颜色:")
                primary_color_label.setStyleSheet(label_style)
                form_layout.addRow(primary_color_label, primary_color_widget)
                widgets_dict["primary_color"] = primary_color_input
            
            # 文字颜色（如果窗口有此属性）
            if "text_color" in properties:
                text_color_widget = QWidget()
                text_color_layout = QHBoxLayout()
                text_color_layout.setContentsMargins(0, 0, 0, 0)
                text_color_layout.setSpacing(5)
                text_color_widget.setLayout(text_color_layout)
                
                text_color_input = QLineEdit()
                text_color_input.setPlaceholderText("#8B4513")
                text_color_input.setReadOnly(True)  # 只读，只能通过颜色选择器修改
                text_color_input.setStyleSheet("""
                    QLineEdit {
                        background-color: rgba(255, 255, 255, 200);
                        border: 1px solid #8B4513;
                        border-radius: 4px;
                        padding: 7px;
                        color: #000000;
                        font-size: 14px;
                    }
                """)
                
                def open_text_color_dialog():
                    current_color = text_color_input.text().strip() or "#8B4513"
                    try:
                        color = QColor(current_color)
                    except:
                        color = QColor(139, 69, 19)  # #8B4513
                    
                    dialog = QColorDialog(color, self)
                    dialog.setWindowTitle("选择文字颜色")
                    if dialog.exec():
                        selected_color = dialog.selectedColor()
                        color_hex = selected_color.name()
                        text_color_input.setText(color_hex)
                        # 更新输入框背景色预览
                        text_color_input.setStyleSheet(f"""
                            QLineEdit {{
                                background-color: {color_hex};
                                border: 1px solid #8B4513;
                                border-radius: 4px;
                                padding: 7px;
                                color: #000000;
                                font-size: 14px;
                            }}
                        """)
                
                text_color_btn = QPushButton("选择颜色")
                text_color_btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255, 255, 255, 200);
                        border: 1px solid #8B4513;
                        border-radius: 4px;
                        color: #FFC0CB;
                        font-size: 14px;
                        font-weight: bold;
                        padding: 7px 15px;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 192, 203, 200);
                        color: white;
                    }
                """)
                text_color_btn.clicked.connect(open_text_color_dialog)
                
                text_color_layout.addWidget(text_color_input, stretch=1)
                text_color_layout.addWidget(text_color_btn)
                
                text_color_label = QLabel("文字颜色:")
                text_color_label.setStyleSheet(label_style)
                form_layout.addRow(text_color_label, text_color_widget)
                widgets_dict["text_color"] = text_color_input
            
            # 背景透明度（如果窗口有此属性）
            if "background_opacity" in properties:
                opacity_widget = QWidget()
                opacity_layout = QHBoxLayout()
                opacity_layout.setContentsMargins(0, 0, 0, 0)
                opacity_layout.setSpacing(10)
                opacity_widget.setLayout(opacity_layout)
                
                opacity_label = QLabel("背景透明度:")
                opacity_label.setStyleSheet(label_style)
                
                opacity_slider = QSlider(Qt.Horizontal)
                opacity_slider.setMinimum(100)
                opacity_slider.setMaximum(255)
                # 根据窗口类型设置默认值
                if config["key"] == "import_panel":
                    opacity_slider.setValue(255)  # 完全不透明
                elif config["key"] == "batch_import":
                    opacity_slider.setValue(120)  # 120透明度
                else:
                    opacity_slider.setValue(240)  # 默认240
                
                opacity_slider.setStyleSheet("""
                    QSlider::groove:horizontal {
                        border: 1px solid #8B4513;
                        height: 8px;
                        background: rgba(255, 255, 255, 200);
                        border-radius: 4px;
                    }
                    QSlider::handle:horizontal {
                        background: #FFC0CB;
                        border: 1px solid #8B4513;
                        width: 18px;
                        height: 18px;
                        border-radius: 9px;
                        margin: -5px 0;
                    }
                """)
                
                opacity_value_label = QLabel(str(opacity_slider.value()))
                opacity_value_label.setStyleSheet("""
                    QLabel {
                        color: #FFC0CB;
                        font-size: 14px;
                        min-width: 40px;
                    }
                """)
                
                def make_opacity_updater(label):
                    def update(value):
                        label.setText(str(value))
                    return update
                
                opacity_slider.valueChanged.connect(make_opacity_updater(opacity_value_label))
                
                opacity_layout.addWidget(opacity_slider, stretch=1)
                opacity_layout.addWidget(opacity_value_label)
                form_layout.addRow(opacity_label, opacity_widget)
                widgets_dict["opacity"] = opacity_slider
                widgets_dict["opacity_label"] = opacity_value_label
            
            # 创建一个容器widget来包含表单内容，这样可以控制显示/隐藏
            form_container = QWidget()
            form_container.setStyleSheet("""
                QWidget {
                    background: transparent;
                }
            """)
            form_container.setLayout(form_layout)
            
            # 将表单容器添加到group中
            group_layout = QVBoxLayout()
            group_layout.setContentsMargins(0, 0, 0, 0)
            group_layout.addWidget(form_container)
            group.setLayout(group_layout)
            
            # 连接checked信号来控制内容显示/隐藏（使用lambda捕获正确的form_container）
            group.toggled.connect(lambda checked, container=form_container: container.setVisible(checked))
            form_container.setVisible(False)  # 默认隐藏（折叠状态）
            
            windows_layout.addWidget(group)
            
            # 保存控件引用（只保存实际创建的控件）
            widgets_dict["group"] = group
            if "background_color" in properties:
                widgets_dict["primary_color"] = primary_color_input
            if "text_color" in properties:
                widgets_dict["text_color"] = text_color_input
            
            self.theme_window_groups[config["key"]] = widgets_dict
        
        windows_layout.addStretch()
        scroll_area.setWidget(windows_container)
        layout.addWidget(scroll_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch()
        
        self.btn_theme_save = QPushButton("保存")
        self.btn_theme_cancel = QPushButton("取消")
        
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #9D00FF;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """
        
        self.btn_theme_save.setStyleSheet(button_style)
        self.btn_theme_cancel.setStyleSheet(button_style)
        
        self.btn_theme_save.clicked.connect(self.handle_theme_settings_save)
        self.btn_theme_cancel.clicked.connect(self.hide_theme_settings_panel)
        
        button_layout.addWidget(self.btn_theme_save)
        button_layout.addWidget(self.btn_theme_cancel)
        layout.addLayout(button_layout)
        
        return theme_panel
    
    def apply_theme_settings_background(self, panel):
        """应用主题设置背景图 - 应用主题设置中的颜色和透明度"""
        # 获取主题设置面板的主题设置
        theme_settings = self.get_window_theme_settings('theme_settings')
        primary_color = theme_settings['primary_color']
        background_opacity = theme_settings['background_opacity']
        
        # 将颜色转换为RGB，并应用透明度
        try:
            color = QColor(primary_color)
            r, g, b = color.red(), color.green(), color.blue()
        except:
            r, g, b = 255, 192, 203  # 默认粉色
        
        project_root = self.get_project_root()
        background_image = self.get_background_path("themesettings.png")
        
        if os.path.exists(background_image):
            background_url = background_image.replace("\\", "/")
            # 当背景图存在时，使用60%透明度（153），确保背景图可见
            overlay_opacity = int(255 * 0.6)  # 60%透明度
            panel_style = f"""
                QWidget#themeSettingsPanel {{
                    background-color: rgba({r}, {g}, {b}, {overlay_opacity});
                    background-image: url('{background_url}');
                    background-position: center;
                    background-repeat: no-repeat;
                    border: 2px solid #8B4513;
                    border-radius: 8px;
                }}
            """
            panel.setStyleSheet(panel_style)
        else:
            # 如果没有背景图，使用用户设置的透明度
            panel_style = f"""
                QWidget#themeSettingsPanel {{
                    background-color: rgba({r}, {g}, {b}, {background_opacity});
                    border: 2px solid #8B4513;
                    border-radius: 8px;
                }}
            """
            panel.setStyleSheet(panel_style)
    
    def load_theme_settings(self):
        """加载主题设置（从JSON加载）"""
        import json
        
        project_root = self.get_project_root()
        json_dir = os.path.join(project_root, "json")
        theme_file = os.path.join(json_dir, "theme_settings.json")
        
        if os.path.exists(theme_file):
            try:
                with open(theme_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 兼容旧格式（单个全局设置）
                    if 'primary_color' in data and not any(key in ['main_window', 'import_panel', 'advanced_settings', 'theme_settings', 'conflict_resolution', 'priority_adjustment', 'batch_import', 'unknown_category_author'] for key in data.keys()):
                        # 旧格式，转换为新格式
                        old_settings = data
                        return {
                            'main_window': {
                                'primary_color': old_settings.get('primary_color', '#9D00FF'),
                                'text_color': old_settings.get('text_color', '#FFFFFF'),
                                'background_opacity': old_settings.get('background_opacity', 240),
                                'glass_effect': old_settings.get('glass_effect', False)
                            }
                        }
                    return data
            except:
                pass
        
        # 默认设置（新格式）
        return {}
    
    def save_theme_settings(self, settings):
        """保存主题设置到JSON"""
        import json
        
        project_root = self.get_project_root()
        json_dir = os.path.join(project_root, "json")
        os.makedirs(json_dir, exist_ok=True)
        
        # 保存到JSON
        theme_file_json = os.path.join(json_dir, "theme_settings.json")
        try:
            with open(theme_file_json, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存主题设置到JSON失败: {e}")
    
    def show_unimplemented_feature_message(self):
        """显示未实现功能提示"""
        QMessageBox.information(
            self,
            "功能提示",
            "该功能未完善，发行版暂不提供，愿意参与开发测试请联系作者"
        )
    
    def get_window_theme_settings(self, window_key):
        """获取指定窗口的主题设置"""
        settings = self.load_theme_settings()
        window_settings = settings.get(window_key, {})
        
        # 返回窗口设置，如果不存在则返回默认值
        return {
            'primary_color': window_settings.get('primary_color', '#9D00FF'),
            'text_color': window_settings.get('text_color', '#FFFFFF'),
            'background_opacity': window_settings.get('background_opacity', 240),
            'glass_effect': window_settings.get('glass_effect', False)
        }
    
    def apply_theme_settings(self):
        """应用主题设置到主窗口"""
        # 获取主窗口的主题设置
        main_window_settings = self.get_window_theme_settings('main_window')
        primary_color = main_window_settings['primary_color']
        text_color = main_window_settings['text_color']
        background_opacity = main_window_settings['background_opacity']
        glass_effect = main_window_settings['glass_effect']
        
        # 应用主色调和文字颜色到界面元素
        # 这里可以根据需要应用到具体的UI元素
        # 例如：按钮、标签等的颜色
        
        # 应用背景透明度（如果需要）
        # 注意：某些效果可能需要重启应用才能完全生效
        
        # 应用毛玻璃效果（如果需要）
        # 注意：某些效果可能需要重启应用才能完全生效
        
        # 这里可以添加更多应用主题设置的代码
        pass
    
    def handle_theme_settings_save(self):
        """处理主题设置保存"""
        settings = {}
        
        # 保存每个窗口的设置
        if hasattr(self, 'theme_window_groups'):
            for key, widgets in self.theme_window_groups.items():
                window_settings = {}
                
                # 安全地获取每个属性（如果存在）
                if "primary_color" in widgets:
                    window_settings['primary_color'] = widgets["primary_color"].text().strip() or '#9D00FF'
                else:
                    window_settings['primary_color'] = '#9D00FF'
                
                if "text_color" in widgets:
                    window_settings['text_color'] = widgets["text_color"].text().strip() or '#FFFFFF'
                else:
                    window_settings['text_color'] = '#FFFFFF'
                
                if "opacity" in widgets:
                    window_settings['background_opacity'] = widgets["opacity"].value()
                else:
                    window_settings['background_opacity'] = 240  # 默认值
                
                if "glass_effect" in widgets:
                    window_settings['glass_effect'] = widgets["glass_effect"].isChecked()
                else:
                    window_settings['glass_effect'] = False
                
                settings[key] = window_settings
        else:
            # 兼容旧代码（如果还没有创建新的UI）
            settings = {
                'primary_color': '#9D00FF',
                'text_color': '#FFFFFF',
                'background_opacity': 240,
                'glass_effect': False
            }
        
        self.save_theme_settings(settings)
        # 立即应用主题设置
        self.apply_theme_settings()
        self.hide_theme_settings_panel()
        
        # 提示用户需要重启应用才能生效
        QMessageBox.information(self, "主题设置", "主题设置已保存并应用，部分设置需要重启应用才能完全生效。")
    
    def is_admin(self):
        """检查是否以管理员身份运行（Windows）"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def restart_as_admin(self):
        """以管理员身份重新运行程序"""
        try:
            import ctypes
            import sys
            
            # 获取当前脚本路径
            script_path = os.path.abspath(sys.argv[0])
            
            # 如果当前已经是管理员，直接返回
            if self.is_admin():
                return True
            
            # 以管理员身份重新运行
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",  # 以管理员身份运行
                sys.executable,  # Python解释器
                f'"{script_path}"',  # 脚本路径
                None,
                1  # SW_SHOWNORMAL
            )
            # 退出当前程序
            sys.exit(0)
            return True
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法以管理员身份重新运行：{str(e)}")
            return False
    
    def show_admin_permission_panel(self):
        """显示管理员权限提示面板"""
        if hasattr(self, 'admin_permission_panel') and self.admin_permission_panel:
            # 如果面板已存在，直接显示
            self.show_panel_with_animation(
                self.admin_permission_panel, 
                "scale_in", 
                300, 
                position_center=True
            )
            return
        
        # 创建权限提示面板
        self.admin_permission_panel = AdminPermissionPanel(self)
        self.admin_permission_panel.setObjectName("adminPermissionPanel")
        
        # 设置面板样式
        self.admin_permission_panel.setStyleSheet("""
            QWidget#adminPermissionPanel {
                background-color: rgba(255, 182, 193, 120);
                border: 4px solid #8B4513;
                border-radius: 12px;
            }
        """)
        
        # 居中显示
        self.show_panel_with_animation(
            self.admin_permission_panel, 
            "scale_in", 
            300, 
            position_center=True
        )
        
        # 连接按钮事件
        self.admin_permission_panel.btn_restart.clicked.disconnect()
        self.admin_permission_panel.btn_restart.clicked.connect(self.handle_admin_permission_result)
        self.admin_permission_panel.btn_cancel.clicked.disconnect()
        self.admin_permission_panel.btn_cancel.clicked.connect(self.hide_admin_permission_panel)
    
    def handle_admin_permission_result(self):
        """处理管理员权限面板的结果"""
        if self.admin_permission_panel.result == 1:
            # 用户选择重新以管理员身份运行
            self.restart_as_admin()
        else:
            # 用户取消
            self.hide_admin_permission_panel()
    
    def hide_admin_permission_panel(self):
        """隐藏管理员权限提示面板"""
        if hasattr(self, 'admin_permission_panel') and self.admin_permission_panel:
            self.admin_permission_panel.hide()
            self.admin_permission_panel.deleteLater()
            delattr(self, 'admin_permission_panel')
            self._admin_permission_shown = False
    
    def load_advanced_settings(self):
        """加载高级设置"""
        import os
        project_root = self.get_project_root()
        settings_file = os.path.join(project_root, "settings.json")
        
        default_settings = {
            'game_path': '',
            'sandbox_mode': False,
            'virtual_mapping': False
        }
        
        if os.path.exists(settings_file):
            try:
                import json
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return {**default_settings, **settings}
            except Exception as e:
                print(f"[失败] 加载设置失败")
        
        return default_settings
    
    def save_advanced_settings(self, settings):
        """保存高级设置"""
        import os
        import json
        project_root = self.get_project_root()
        settings_file = os.path.join(project_root, "settings.json")
        
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            # 设置已保存，不打印详细信息
        except Exception as e:
            print(f"[失败] 保存设置失败")
    
    def create_right_search_area(self):
        """创建右侧搜索设置区：搜索框 + 设置按钮"""
        search_area_widget = QWidget()
        search_area_layout = QHBoxLayout()
        search_area_layout.setSpacing(SPACING_BASE)  # 组件之间的间距（8px）
        search_area_layout.setContentsMargins(0, 0, 0, 0)
        search_area_widget.setLayout(search_area_layout)
        
        # 搜索输入框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索Mod...")
        self.search_input.setMinimumWidth(200)  # 设置最小宽度，允许拉伸
        self.search_input.setMaximumWidth(350)  # 设置最大宽度，避免过度拉伸
        # 设置搜索框CSS样式：卡片设计，内阴影，聚焦效果
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: white;
                border: 1px solid {COLOR_BG_GRAY};
                border-radius: {BORDER_RADIUS - 2}px;
                color: {COLOR_TEXT_DARK};
                padding: 8px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR_PRIMARY};
                background-color: rgba(255, 255, 255, 240);
            }}
        """)
        # 连接搜索框文本变化事件
        self.search_input.textChanged.connect(self.filter_mods_by_search)
        # 添加焦点离开事件，当搜索框失去焦点且为空时，重新应用忽略规则
        self.search_input.editingFinished.connect(self.on_search_focus_out)
        search_area_layout.addWidget(self.search_input)
        
        # 刷新按钮（带图标）
        self.btn_refresh = QPushButton("🔄")  # 使用Unicode刷新图标
        self.btn_refresh.setFixedWidth(36)  # 设置按钮固定宽度36px
        self.btn_refresh.setFixedHeight(36)  # 设置按钮固定高度36px
        self.btn_refresh.setToolTip("刷新")  # 悬停提示
        # 设置按钮样式：卡片设计，圆角，悬停效果
        self.btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border: 1px solid {COLOR_BG_GRAY};
                border-radius: {BORDER_RADIUS - 2}px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY};
                color: {COLOR_TEXT_LIGHT};
                border: 1px solid {COLOR_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_PRIMARY_ALT};
                border: 1px solid {COLOR_PRIMARY_ALT};
            }}
        """)
        # 连接刷新按钮的点击事件
        self.btn_refresh.clicked.connect(self.refresh_mod_list)
        search_area_layout.addWidget(self.btn_refresh)
        
        return search_area_widget
    
    def create_content_area(self):
        """创建中间内容区域：左侧Mod表格 + 右侧操作按钮栏"""
        content_widget = QWidget()
        content_layout = QHBoxLayout()
        content_layout.setSpacing(SPACING_BASE)  # 间距8px
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_widget.setLayout(content_layout)
        
        # 延迟创建导入面板，避免初始化时的问题
        # 导入面板将在第一次需要时创建
        self.import_panel = None
        
        # 左侧Mod表格
        self.mod_table_widget = self.create_mod_table()
        content_layout.addWidget(self.mod_table_widget, stretch=1)  # stretch=1让表格占据大部分空间
        
        # 右侧操作按钮栏
        right_button_bar = self.create_right_button_bar()
        content_layout.addWidget(right_button_bar, stretch=0)  # stretch=0固定宽度
        
        return content_widget
    
    def create_import_panel(self):
        """创建可拖动的模组信息录入窗口"""
        import_panel = QWidget()
        import_panel.setObjectName("importPanel")
        
        # 设置窗口大小：和主窗口一样大
        # 如果窗口还没显示，使用默认大小
        try:
            main_window_size = self.size()
            window_width = main_window_size.width()
            window_height = main_window_size.height()
            # 如果大小为0，使用默认值
            if window_width <= 0 or window_height <= 0:
                window_width = 1200
                window_height = 800
        except:
            # 如果获取大小失败，使用默认值
            window_width = 1200
            window_height = 800
        import_panel.setFixedSize(window_width, window_height)
        
        # 设置窗口样式：作为子面板悬浮在主窗口上方
        import_panel.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        
        # 设置背景图（会应用主题设置中的颜色和透明度）
        self.apply_import_panel_background(import_panel)
        
        # 垂直布局
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        import_panel.setLayout(layout)
        
        # 标题栏（可拖动）
        title_bar = QWidget()
        title_bar.setFixedHeight(35)
        title_bar.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 182, 193, 180);
                border-radius: 6px;
                border-bottom: 1px solid #8B4513;
            }
        """)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(10, 5, 10, 5)
        title_bar.setLayout(title_layout)
        
        # 标题
        title = QLabel("导入模组")
        title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        # 关闭按钮
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(25, 25)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 180);
                border: 1px solid #8B4513;
                border-radius: 3px;
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8B4513;
                color: white;
            }
        """)
        close_btn.clicked.connect(self.hide_import_panel)
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(close_btn)
        layout.addWidget(title_bar)
        
        # 模组信息表单
        form_widget = QWidget()
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_widget.setLayout(form_layout)
        
        # 模组名称
        self.mod_name_input = QLineEdit()
        self.mod_name_input.setPlaceholderText("请输入模组名称")
        self.mod_name_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                padding: 5px;
                color: #000000;
            }
        """)
        
        # 统一样式标签
        label_style = """
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
                font-weight: bold;
                min-width: 50px;
                text-align: right;
            }
        """
        
        mod_name_label = QLabel("模组名称:")
        mod_name_label.setStyleSheet(label_style)
        
        # 使用水平布局来对齐标签和输入框
        mod_name_layout = QHBoxLayout()
        mod_name_layout.setContentsMargins(0, 0, 0, 0)
        mod_name_layout.setSpacing(10)
        mod_name_layout.addWidget(mod_name_label)
        mod_name_layout.addWidget(self.mod_name_input, stretch=1)
        
        form_layout.addRow(mod_name_layout)
        
        # 分类和作者在同一行
        category_author_widget = QWidget()
        category_author_layout = QHBoxLayout()
        category_author_layout.setContentsMargins(0, 0, 0, 0)
        category_author_layout.setSpacing(10)
        category_author_widget.setLayout(category_author_layout)
        
        # 分类输入框（支持多个分类，用分号分隔）
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("分类（多个用分号分隔）")
        self.category_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                padding: 5px;
                color: #000000;
            }
        """)
        
        # 分类下拉选择框（初始隐藏，点击加号按钮时显示在输入框下方）
        self.category_combo = QComboBox()
        # 从配置文件加载分类
        try:
            categories = self.load_categories()
            if not categories:
                categories = ["邦邦"]
        except Exception as e:
            # 初始化时出错，使用默认值
            categories = ["邦邦"]
        category_items = categories + ["添加新标签..."]
        self.category_combo.addItems(category_items)
        self.category_combo.setCurrentIndex(0)  # 默认选择第一项
        self.category_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                padding: 5px;
                color: #000000;
            }
        """)
        self.category_combo.hide()  # 初始隐藏
        # 连接下拉框选择事件
        self.category_combo.currentTextChanged.connect(self.on_category_selected)
        
        # 添加分类按钮（加号按钮）
        add_category_btn = QPushButton("+")
        add_category_btn.setFixedSize(30, 30)
        add_category_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #000000;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """)
        add_category_btn.clicked.connect(self.show_category_selection_dialog)
        
        # 作者选择（和分类一样写法）
        self.author_combo = QComboBox()
        # 从配置文件加载作者
        try:
            authors = self.load_authors()
            if not authors:
                authors = ["QCanon"]
        except Exception as e:
            # 初始化时出错，使用默认值
            authors = ["QCanon"]
        author_items = [""] + authors + ["添加新作者..."]
        self.author_combo.addItems(author_items)
        self.author_combo.setCurrentIndex(0)  # 默认选择空项
        self.author_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                padding: 5px;
                color: #000000;
            }
        """)
        self.author_combo.currentTextChanged.connect(self.on_author_changed)
        
        # 标签和下拉框对齐布局
        category_label = QLabel("分类:")
        category_label.setStyleSheet(label_style)
        author_label = QLabel("作者:")
        author_label.setStyleSheet(label_style)
        
        # 分类布局：输入框 + 加号按钮（同一行）
        category_input_layout = QHBoxLayout()
        category_input_layout.setContentsMargins(0, 0, 0, 0)
        category_input_layout.setSpacing(5)
        category_input_layout.addWidget(self.category_input, stretch=1)
        category_input_layout.addWidget(add_category_btn)
        
        # 分类容器（包含输入框行和下拉框的垂直布局）
        category_container = QWidget()
        category_container_layout = QVBoxLayout()
        category_container_layout.setContentsMargins(0, 0, 0, 0)
        category_container_layout.setSpacing(2)
        category_container_layout.addLayout(category_input_layout)
        category_container_layout.addWidget(self.category_combo)
        category_container.setLayout(category_container_layout)
        
        category_author_layout.addWidget(category_label)
        category_author_layout.addWidget(category_container, stretch=1)
        category_author_layout.addWidget(author_label)
        category_author_layout.addWidget(self.author_combo, stretch=1)
        
        form_layout.addRow(category_author_widget)
        
        # 描述
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("请输入模组描述")
        self.description_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                padding: 5px;
                color: #000000;
            }
        """)
        
        description_label = QLabel("描述:")
        description_label.setStyleSheet(label_style)
        
        # 使用水平布局来对齐标签和输入框
        description_layout = QHBoxLayout()
        description_layout.setContentsMargins(0, 0, 0, 0)
        description_layout.setSpacing(10)
        description_layout.addWidget(description_label)
        description_layout.addWidget(self.description_input, stretch=1)
        
        form_layout.addRow(description_layout)
        
        layout.addWidget(form_widget)
        
        # 缩略图和文件树区域（上下对齐）
        content_widget = QWidget()
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(10, 5, 10, 5)
        content_layout.setSpacing(10)
        content_widget.setLayout(content_layout)
        
        # 缩略图区域（支持拖拽）
        thumbnail_widget = QWidget()
        thumbnail_layout = QVBoxLayout()
        thumbnail_layout.setContentsMargins(0, 0, 0, 0)
        thumbnail_layout.setSpacing(0)  # 无间距
        thumbnail_widget.setLayout(thumbnail_layout)
        
        thumbnail_label = QLabel("缩略图:")
        thumbnail_label.setStyleSheet(label_style)
        thumbnail_layout.addWidget(thumbnail_label)
        
        self.thumbnail_preview = QLabel()
        self.thumbnail_preview.setFixedSize(288, 288)  # 再放大1.2倍 (240 * 1.2 = 288)
        self.thumbnail_preview.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 150);
                border: 1px dashed #8B4513;
                border-radius: 4px;
            }
        """)
        self.thumbnail_preview.setAlignment(Qt.AlignCenter)
        self.thumbnail_preview.setText("无图片\n\n拖拽图片到此处")
        # 设置鼠标悬停为手型，表示可点击
        self.thumbnail_preview.setCursor(Qt.PointingHandCursor)
        # 连接点击事件
        self.thumbnail_preview.mousePressEvent = self.on_thumbnail_click
        # 支持拖拽
        self.thumbnail_preview.setAcceptDrops(True)
        self.thumbnail_preview.dragEnterEvent = self.on_thumbnail_drag_enter
        self.thumbnail_preview.dropEvent = self.on_thumbnail_drop
        
        thumbnail_layout.addWidget(self.thumbnail_preview)
        # 不添加弹性空间，让缩略图保持在底部
        
        # 右侧文件树和操作区域（水平布局）
        right_widget = QWidget()
        right_layout = QHBoxLayout()
        right_layout.setContentsMargins(5, 0, 0, 0)
        right_layout.setSpacing(10)
        right_widget.setLayout(right_layout)
        
        # 文件树区域（与缩略图底部对齐）
        file_tree_widget = QWidget()
        file_tree_layout = QVBoxLayout()
        file_tree_layout.setContentsMargins(0, 0, 0, 0)
        file_tree_layout.setSpacing(0)  # 无间距
        file_tree_widget.setLayout(file_tree_layout)
        
        file_tree_label = QLabel("文件列表:")
        file_tree_label.setStyleSheet(label_style)
        file_tree_layout.addWidget(file_tree_label)
        
        # 文件树滚动区域（支持拖拽）
        from PySide6.QtWidgets import QScrollArea
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderHidden(True)
        self.file_tree.setFixedHeight(288)  # 与缩略图高度保持一致
        self.file_tree.setAcceptDrops(True)  # 接受拖拽
        # 正确设置拖拽事件
        self.file_tree.dragEnterEvent = lambda event: self.handle_drag_enter_event(event, self.file_tree)
        self.file_tree.dropEvent = lambda event: self.handle_drop_event(event, self.file_tree)
        self.file_tree.setStyleSheet("""
            QTreeWidget {
                background-color: rgba(255, 255, 255, 150);
                border: 1px solid #8B4513;
                border-radius: 4px;
            }
            QTreeWidget::item {
                color: #000000;
                font-size: 11px;
                padding: 2px;
            }
            QTreeWidget::item:hover {
                background-color: #87CEEB;  /* 天蓝色 */
                color: white;
            }
            QTreeWidget::item:selected {
                background-color: #4682B4;
                color: white;
            }
        """)
        file_tree_layout.addWidget(self.file_tree)
        
        # 操作按钮区域（按钮靠上）
        action_widget = QWidget()
        action_layout = QVBoxLayout()
        action_layout.setContentsMargins(5, 0, 0, 0)
        action_layout.setSpacing(15)  # 按钮之间的上下距离
        action_widget.setLayout(action_layout)
        
        # 操作标签和按钮在同一行，标签与其他区域齐平
        action_header_layout = QHBoxLayout()
        action_header_layout.setContentsMargins(0, 0, 0, 0)
        
        action_label = QLabel("操作:")
        action_label.setStyleSheet(label_style)
        
        # 使用字典按钮
        dict_btn = QPushButton("使用字典")
        dict_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #000000;
                font-size: 12px;
                font-weight: bold;
                padding: 8px 12px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """)
        
        # 运行脚本按钮
        script_btn = QPushButton("运行脚本")
        script_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #000000;
                font-size: 12px;
                font-weight: bold;
                padding: 8px 12px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """)
        
        # 标签和按钮布局
        action_header_layout.addWidget(action_label)
        action_header_layout.addStretch()  # 标签左对齐
        
        # 按钮垂直布局，靠上显示
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addWidget(dict_btn)
        button_layout.addWidget(script_btn)
        
        # 连接未实现功能的按钮
        dict_btn.clicked.connect(self.show_unimplemented_feature_message)
        script_btn.clicked.connect(self.show_unimplemented_feature_message)
        
        # 组装操作区域
        action_layout.addLayout(action_header_layout)
        action_layout.addLayout(button_layout)
        action_layout.addStretch()  # 添加弹性空间在底部
        
        # 添加弹性空间（但不添加，让按钮区域保持紧凑）
        # action_layout.addStretch()
        
        # 组装右侧区域（水平布局）
        right_layout.addWidget(file_tree_widget, stretch=3)
        right_layout.addWidget(action_widget, stretch=1)
        
        # 组装内容区域
        content_layout.addWidget(thumbnail_widget)
        content_layout.addWidget(right_widget, stretch=1)
        
        layout.addWidget(content_widget)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(139, 69, 19, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 12px;
                text-align: center;  /* 文字居中 */
            }
            QPushButton:hover {
                background-color: #8B4513;
            }
        """)
        save_btn.clicked.connect(self.save_mod_info)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #000000;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 12px;
                text-align: center;  /* 文字居中 */
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """)
        cancel_btn.clicked.connect(self.hide_import_panel)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # 设置拖动功能
        self.drag_position = None
        # 由于窗口现在占满整个主窗口，禁用拖动功能
        # title_bar.mousePressEvent = self.mouse_press_event
        # title_bar.mouseMoveEvent = self.mouse_move_event
        
        return import_panel
    
    def mousePressEvent(self, event):
        """鼠标按下事件，用于拖动窗口"""
        if event.button() == Qt.LeftButton:
            # 只有在导入面板存在时才设置拖动位置
            if hasattr(self, 'import_panel') and self.import_panel:
                self.drag_position = event.globalPosition().toPoint() - self.import_panel.pos()
            else:
                self.drag_position = None
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件，用于拖动窗口"""
        if hasattr(self, 'drag_position') and self.drag_position is not None:
            if event.buttons() == Qt.LeftButton:
                # 只有在导入面板存在时才移动
                if hasattr(self, 'import_panel') and self.import_panel:
                    self.import_panel.move(event.globalPosition().toPoint() - self.drag_position)
    
    def open_file_dialog(self):
        """打开文件选择对话框"""
        from PySide6.QtWidgets import QFileDialog
        
        # 设置文件过滤器，只允许选择zip和7z文件
        file_filter = "压缩文件 (*.zip *.7z);;Zip文件 (*.zip);;7z文件 (*.7z)"
        
        # 打开文件对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择Mod文件",
            "",  # 默认路径
            file_filter,
            "Zip文件 (*.zip)"  # 默认选择的过滤器
        )
        
        # 如果用户选择了文件，显示导入面板
        if file_path:
            self.selected_file_path = file_path  # 保存选择的文件路径
            self.show_import_panel_with_file(file_path)
    
    def show_import_panel_with_file(self, file_path):
        """显示导入面板并检查modinfo文件夹"""
        import zipfile
        import xml.etree.ElementTree as ET
        
        # 确保导入面板已创建
        if not hasattr(self, 'import_panel') or not self.import_panel:
            self.import_panel = self.create_import_panel()
        
        # 重置表单
        self.mod_name_input.clear()
        self.description_input.clear()
        self.category_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.author_combo.setCurrentIndex(0)
        self.thumbnail_preview.setText("无图片")
        
        # 设置模组名称为zip文件名（不含扩展名）
        import os
        file_basename = os.path.basename(file_path)
        mod_name = os.path.splitext(file_basename)[0]
        self.mod_name_input.setText(mod_name)
        
        # 清空文件树
        self.file_tree.clear()
        
        try:
            # 检查zip文件中是否有modinfo文件夹
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                
                # 显示文件树
                self.display_file_tree(file_list)
                
                # 查找modinfo文件夹
                modinfo_files = [f for f in file_list if f.startswith('modinfo/') and len(f) > len('modinfo/')]
                
                if modinfo_files:
                    # 有modinfo文件夹，尝试读取XML和PNG
                    xml_files = [f for f in modinfo_files if f.endswith('.xml')]
                    png_files = [f for f in modinfo_files if f.endswith('.png')]
                    
                    # 读取XML文件获取模组信息
                    if xml_files:
                        try:
                            xml_content = zip_file.read(xml_files[0])
                            root = ET.fromstring(xml_content)
                            
                            # 解析XML信息
                            name_elem = root.find('.//name')
                            author_elem = root.find('.//author')
                            description_elem = root.find('.//description')
                            category_elem = root.find('.//category')
                            
                            if name_elem is not None:
                                self.mod_name_input.setText(name_elem.text or mod_name)
                            if author_elem is not None:
                                # 如果XML中有作者信息，设置到下拉框
                                author_text = author_elem.text or ""
                                if author_text:
                                    index = self.author_combo.findText(author_text)
                                    if index >= 0:
                                        self.author_combo.setCurrentIndex(index)
                            if description_elem is not None:
                                self.description_input.setText(description_elem.text or "")
                            if category_elem is not None:
                                category_text = category_elem.text or ""
                                if category_text:
                                    # 支持多分类（分号分隔），直接设置到输入框
                                    self.category_input.setText(category_text.strip())
                        except Exception as e:
                            pass  # 解析XML失败，不打印详细信息
                    
                    # 读取PNG缩略图
                    if png_files:
                        try:
                            from PySide6.QtGui import QPixmap
                            png_data = zip_file.read(png_files[0])
                            pixmap = QPixmap()
                            pixmap.loadFromData(png_data)
                            if not pixmap.isNull():
                                scaled_pixmap = pixmap.scaled(240, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                self.thumbnail_preview.setPixmap(scaled_pixmap)
                        except Exception as e:
                            pass  # 加载缩略图失败，不打印详细信息
                else:
                    # 没有modinfo文件夹，用户需要手动填写
                    pass
        except Exception as e:
            pass  # 读取zip文件失败，不打印详细信息
        
        # 使用动画显示导入面板
        self._show_import_panel_with_animation()
    
    def _show_import_panel_with_animation(self):
        """使用动画显示导入面板"""
        # 使用快速的动画接口显示面板 - 覆盖主窗口
        self.show_panel_with_animation(self.import_panel, "fade_in", 250, position_center=False)  # 加快到250ms
    
    def display_file_tree(self, file_list):
        """显示树形文件结构"""
        self.file_tree.clear()
        
        # 创建文件夹结构
        folder_dict = {}
        
        # 首先构建文件夹结构
        for file_path in file_list:
            if file_path.endswith('/'):
                # 这是一个文件夹
                parts = file_path.strip('/').split('/')
                current_dict = folder_dict
                for part in parts:
                    if part not in current_dict:
                        current_dict[part] = {}
                    current_dict = current_dict[part]
        
        # 然后添加文件到对应文件夹
        for file_path in file_list:
            if not file_path.endswith('/'):
                # 这是一个文件
                parts = file_path.split('/')
                current_dict = folder_dict
                for part in parts[:-1]:  # 除了文件名外的所有部分
                    if part:
                        if part not in current_dict:
                            current_dict[part] = {}
                        current_dict = current_dict[part]
                # 添加文件名
                current_dict[parts[-1]] = None  # None表示这是文件
        
        # 递归构建树形结构
        def build_tree(parent_item, folder_data):
            for name, content in sorted(folder_data.items()):
                if content is None:
                    # 这是文件
                    item = QTreeWidgetItem(parent_item)
                    item.setText(0, name)
                    # 设置文件图标（可选）
                    item.setIcon(0, self.style().standardIcon(QStyle.SP_FileIcon))
                else:
                    # 这是文件夹
                    folder_item = QTreeWidgetItem(parent_item)
                    folder_item.setText(0, name)
                    # 设置文件夹图标
                    folder_item.setIcon(0, self.style().standardIcon(QStyle.SP_DirIcon))
                    # 递归添加子项
                    build_tree(folder_item, content)
                    # 默认展开文件夹
                    folder_item.setExpanded(True)
        
        # 从根开始构建树
        build_tree(self.file_tree.invisibleRootItem(), folder_dict)
    
    def on_thumbnail_click(self, event):
        """点击缩略图选择图片"""
        if event.button() == Qt.LeftButton:
            # 打开文件选择对话框
            file_filter = "图片文件 (*.png *.jpg *.jpeg);;PNG文件 (*.png);;JPG文件 (*.jpg *.jpeg)"
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择缩略图",
                "",
                file_filter,
                "PNG文件 (*.png)"
            )
            
            if file_path:
                self.load_custom_thumbnail(file_path)
    
    def load_custom_thumbnail(self, file_path):
        """加载自定义缩略图"""
        try:
            from PySide6.QtGui import QPixmap
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # 以图片高度为基准，在中心截取正方形
                height = pixmap.height()
                width = pixmap.width()
                
                if width > height:
                    # 宽度大于高度，从中心截取正方形
                    x = (width - height) // 2
                    y = 0
                    size = height
                else:
                    # 高度大于等于宽度，从中心截取正方形
                    x = 0
                    y = (height - width) // 2
                    size = width
                
                # 截取正方形区域
                cropped_pixmap = pixmap.copy(x, y, size, size)
                
                # 缩放到288x288
                scaled_pixmap = cropped_pixmap.scaled(288, 288, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # 显示缩略图
                self.thumbnail_preview.setPixmap(scaled_pixmap)
                # 保存pixmap供保存时使用
                self.thumbnail_pixmap = scaled_pixmap
                
        except Exception as e:
            print(f"加载缩略图失败: {e}")
    
    def apply_import_panel_background(self, import_panel):
        # 获取导入面板的主题设置
        theme_settings = self.get_window_theme_settings('import_panel')
        primary_color = theme_settings['primary_color']
        background_opacity = theme_settings['background_opacity']
        
        # 将颜色转换为RGB，并应用透明度
        try:
            color = QColor(primary_color)
            r, g, b = color.red(), color.green(), color.blue()
        except:
            r, g, b = 255, 192, 203  # 默认粉色
        
        # 获取项目根目录
        # 背景图片路径：项目根目录/background/importer.png
        background_image = self.get_background_path("importer.png")
        
        # 检查文件是否存在，如果存在则使用背景图片
        if os.path.exists(background_image):
            # 将Windows路径中的反斜杠转换为正斜杠，直接使用本地路径
            background_url = background_image.replace("\\", "/")
            
            # 构建导入面板背景样式（应用主题颜色和透明度）
            panel_style = f"""
                QWidget#importPanel {{
                    background-color: rgba({r}, {g}, {b}, {background_opacity});
                    background-image: url('{background_url}');
                    background-position: center;
                    background-repeat: no-repeat;
                    border: 2px solid #8B4513;
                    border-radius: 8px;
                }}
            """
            import_panel.setStyleSheet(panel_style)
        else:
            # 如果没有背景图，只应用颜色和透明度
            panel_style = f"""
                QWidget#importPanel {{
                    background-color: rgba({r}, {g}, {b}, {background_opacity});
                    border: 2px solid #8B4513;
                    border-radius: 8px;
                }}
            """
            import_panel.setStyleSheet(panel_style)
    
    def on_author_changed(self, text):
        """作者选择变化事件"""
        if text == "添加新作者...":
            # 找到导入面板作为父窗口
            import_panel = None
            if hasattr(self, 'import_panel') and self.import_panel:
                import_panel = self.import_panel
            else:
                # 尝试从当前窗口找到导入面板
                for widget in self.findChildren(QWidget):
                    if hasattr(widget, 'objectName') and widget.objectName() == "importPanel":
                        import_panel = widget
                        break
            
            # 创建输入对话框，使用导入面板作为父窗口
            from PySide6.QtWidgets import QInputDialog
            parent_widget = import_panel if import_panel else self
            new_author, ok = QInputDialog.getText(parent_widget, "添加新作者", "请输入新的作者名称:")
            
            if ok and new_author.strip():
                # 保存新作者到配置文件
                parent = self.parent()
                while parent and not hasattr(parent, 'save_author'):
                    parent = parent.parent()
                if parent:
                    parent.save_author(new_author.strip())
                
                # 移除"添加新作者..."选项
                self.author_combo.removeItem(self.author_combo.count() - 1)
                # 添加新作者
                self.author_combo.addItem(new_author.strip())
                # 重新添加"添加新作者..."选项
                self.author_combo.addItem("添加新作者...")
                # 选择新添加的作者
                self.author_combo.setCurrentText(new_author.strip())
            else:
                # 用户取消，恢复到第一个选项
                self.author_combo.setCurrentIndex(0)
        elif text != "":
            # 选择了预设作者
            pass  # 下拉框已经显示了选择
    
    def handle_drag_enter_event(self, event, widget):
        """处理拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否是压缩包文件
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.zip', '.7z')):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def handle_drop_event(self, event, widget):
        """处理拖拽放下事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.zip', '.7z')):
                    # 处理压缩包文件
                    self.selected_file_path = file_path
                    self.show_import_panel_with_file(file_path)
                    break
    
    def on_thumbnail_drag_enter(self, event):
        """缩略图拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否是图片文件
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def on_thumbnail_drop(self, event):
        """缩略图拖拽放下事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    # 加载图片
                    self.load_custom_thumbnail(file_path)
                    break
    
    def save_mod_info(self):
        """保存模组信息并解压压缩包"""
        import zipfile
        import xml.etree.ElementTree as ET
        import shutil
        
        if not hasattr(self, 'selected_file_path'):
            return
        
        try:
            # 获取表单数据
            mod_name = self.mod_name_input.text().strip() or "未命名模组"
            category = self.category_input.text().strip()  # 从输入框获取，支持多分类（分号分隔）
            author = self.author_combo.currentText().strip()
            description = self.description_input.text().strip()
            
            # 在保存XML之前，先检查并处理未知的分类和作者
            # 对于多分类，需要分别检查每个分类
            if category:
                categories_list = [cat.strip() for cat in category.split(';') if cat.strip()]
                processed_categories = []
                for cat in categories_list:
                    processed_cat, _ = self.check_and_handle_unknown_category_author(cat, "")
                    if processed_cat:
                        processed_categories.append(processed_cat)
                category = '; '.join(processed_categories) if processed_categories else ""
            
            category, author = self.check_and_handle_unknown_category_author(category, author)
            
            # 创建mods目录（如果不存在）
            project_root = self.get_project_root()
            mods_dir = os.path.join(project_root, "mods")
            os.makedirs(mods_dir, exist_ok=True)
            
            # 使用模组名称作为文件夹名
            mod_folder_name = mod_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
            mod_folder_path = os.path.join(mods_dir, mod_folder_name)
            
            # 解压压缩包到mods目录
            with zipfile.ZipFile(self.selected_file_path, 'r') as zip_file:
                zip_file.extractall(mod_folder_path)
            
            # 创建modinfo文件夹
            modinfo_dir = os.path.join(mod_folder_path, "modinfo")
            os.makedirs(modinfo_dir, exist_ok=True)
            
            # 生成XML文件
            xml_root = ET.Element("mod")
            
            name_elem = ET.SubElement(xml_root, "name")
            name_elem.text = mod_name
            
            if category:
                category_elem = ET.SubElement(xml_root, "category")
                category_elem.text = category
            
            if author:
                author_elem = ET.SubElement(xml_root, "author")
                author_elem.text = author
            
            if description:
                description_elem = ET.SubElement(xml_root, "description")
                description_elem.text = description
            
            # 记录完整的文件结构
            file_structure_elem = ET.SubElement(xml_root, "file_structure")
            file_list = self.get_folder_files(mod_folder_path)
            for file_path in file_list:
                file_elem = ET.SubElement(file_structure_elem, "file")
                file_elem.text = file_path
                # 如果是文件（不是目录），记录文件大小和修改时间
                if not file_path.endswith('/'):
                    # 将统一的分隔符转换为当前系统的分隔符，确保跨平台兼容
                    normalized_path = file_path.replace('/', os.sep).replace('\\', os.sep)
                    full_path = os.path.join(mod_folder_path, normalized_path)
                    if os.path.exists(full_path):
                        file_elem.set("size", str(os.path.getsize(full_path)))
                        file_elem.set("mtime", str(os.path.getmtime(full_path)))
            
            # 保存XML文件
            xml_file_path = os.path.join(modinfo_dir, "modinfo.xml")
            tree = ET.ElementTree(xml_root)
            tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
            
            # 生成PNG文件（如果有缩略图）
            if hasattr(self, 'thumbnail_pixmap') and not self.thumbnail_pixmap.isNull():
                png_file_path = os.path.join(modinfo_dir, "thumbnail.png")
                self.thumbnail_pixmap.save(png_file_path)
            
            # 添加到主表格（不再检查未知项，因为已经在上面检查过了）
            self.add_mod_to_table(mod_name, category, author, check_unknown=False)
            
            # 关闭导入面板
            self.hide_import_panel()
            
            print(f"[成功] 模组导入成功: {mod_name}")
            
        except Exception as e:
            print(f"[失败] 模组导入失败: {mod_name}")
    
    def check_and_handle_unknown_category_author(self, category, author):
        """检查并处理未知的标签和作者
        返回: (final_category, final_author)
        """
        # 如果窗口还没显示，直接返回，不检查未知项（避免初始化时死循环）
        if not self.isVisible():
            return (category, author)
        
        categories = self.load_categories()
        authors = self.load_authors()
        
        final_category = category
        final_author = author
        
        # 检查未知标签（每个都单独询问）
        if category and category.strip() and category not in categories:
            panel = UnknownCategoryAuthorPanel(category, "标签", self)
            result = self.show_unknown_item_panel(panel)
            if result == 1:  # 保存
                self.save_category(category)
            elif result == 2:  # 忽略
                final_category = ""
        
        # 检查未知作者（每个都单独询问）
        if author and author.strip() and author not in authors:
            panel = UnknownCategoryAuthorPanel(author, "作者", self)
            result = self.show_unknown_item_panel(panel)
            if result == 1:  # 保存
                self.save_author(author)
            elif result == 2:  # 忽略
                final_author = ""
        
        return (final_category, final_author)
    
    def show_unknown_item_panel(self, panel):
        """显示未知标签/作者面板 - 使用系统对话框"""
        # 确保窗口已显示
        if not self.isVisible():
            return 2  # 如果窗口还没显示，默认忽略
        
        # 执行对话框（QDialog会自动居中显示）
        result = panel.exec()
        return result
    
    def add_mod_to_table(self, mod_name, category, author, check_unknown=True):
        """添加模组到主表格
        Args:
            mod_name: mod名称
            category: 分类
            author: 作者
            check_unknown: 是否检查未知的标签和作者（默认True，加载已有mod时设为False）
        """
        # 检查并处理未知的标签和作者（仅在导入新mod时检查）
        if check_unknown:
            category, author = self.check_and_handle_unknown_category_author(category, author)
        
        # 获取表格
        if hasattr(self, 'mod_table'):
            # 从配置文件加载状态（添加异常处理）
            try:
                mod_states = self.load_mod_states()
            except:
                mod_states = {}
            mod_state = mod_states.get(mod_name, {})
            
            # 如果是新导入的mod，记录导入时间
            if check_unknown:
                import time
                if isinstance(mod_state, bool):
                    mod_state = {"enabled": mod_state, "favorite": False, "ignored": False}
                if "import_time" not in mod_state:
                    mod_state["import_time"] = time.time()
                    mod_states[mod_name] = mod_state
                    # 保存更新后的状态
                    try:
                        self._save_mod_states_direct(mod_states)
                    except:
                        pass
            
            # 如果是旧格式，兼容处理
            if isinstance(mod_state, bool):
                enabled = mod_state
                favorite = False
                ignored = False
            else:
                enabled = mod_state.get("enabled", False)
                favorite = mod_state.get("favorite", False)
                ignored = mod_state.get("ignored", False)
            
            # 如果被忽略，不添加到表格
            if ignored:
                return
            
            # 使用CustomModTable的add_mod_row方法
            row = self.mod_table.add_mod_row(mod_name, category or "未分类", author or "未知", enabled=enabled)
            
            # 如果被收藏，设置背景色为浅黄色
            if favorite and row >= 0:
                self.set_mod_favorite_background(row)
    
    def edit_mod(self, mod_name, category, author):
        """编辑模组信息"""
        # 复用导入面板的界面，只修改标题
        self.show_import_panel()
        # 修改标题为编辑模组
        if hasattr(self, 'import_panel') and self.import_panel:
            # 找到标题标签并修改
            title_label = self.import_panel.findChild(QLabel)
            if title_label:
                title_label.setText("编辑模组")
            
            # 填充现有模组信息
            self.mod_name_input.setText(mod_name)
            if category and category != "未分类":
                # 支持多分类（分号分隔）
                self.category_input.setText(category)
            if author and author != "未知":
                index = self.author_combo.findText(author)
                if index >= 0:
                    self.author_combo.setCurrentIndex(index)
            
            # 加载模组文件树
            self.load_mod_file_tree(mod_name)
            # 加载模组XML信息
            self.load_mod_xml_info(mod_name)
            
            # 修改保存按钮的行为
            save_btn = None
            for widget in self.import_panel.findChildren(QPushButton):
                if widget.text() == "保存":
                    save_btn = widget
                    break
            
            if save_btn:
                save_btn.clicked.disconnect()
                save_btn.clicked.connect(self.save_mod_changes)
    
    def save_mod_changes(self):
        """保存模组修改"""
        # 获取当前选中的行
        selected_rows = self.mod_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        
        # 获取表单数据
        mod_name = self.mod_name_input.text().strip() or "未命名模组"
        category = self.category_input.text().strip()  # 从输入框获取，支持多分类（分号分隔）
        author = self.author_combo.currentText().strip() or "未知"
        description = self.description_input.text().strip()
        
        # 更新表格
        self.mod_table.item(row, 1).setText(mod_name)
        self.mod_table.item(row, 2).setText(category if category else "未分类")
        self.mod_table.item(row, 3).setText(author)
        # 更新日期
        from PySide6.QtCore import QDate
        add_date = QDate.currentDate().toString("yyyy-MM-dd")
        self.mod_table.item(row, 4).setText(add_date)
        
        # 更新XML文件（如果存在）- 保存多分类（分号分隔）到XML
        self.update_mod_xml(mod_name, category, author, description)
        
        # 关闭导入面板
        self.hide_import_panel()
        
        # 模组信息已更新，不打印详细信息
    
    def load_mod_file_tree(self, mod_name):
        """加载模组的文件树形结构"""
        # 清空文件树
        self.file_tree.clear()
        
        # 获取模组文件路径
        mod_file_path = self.get_mod_file_path(mod_name)
        
        if mod_file_path and os.path.exists(mod_file_path):
            try:
                if mod_file_path.endswith('.zip'):
                    # 如果是zip文件，读取内部结构
                    import zipfile
                    with zipfile.ZipFile(mod_file_path, 'r') as zip_file:
                        file_list = zip_file.namelist()
                        self.display_file_tree(file_list)
                elif os.path.isdir(mod_file_path):
                    # 如果是文件夹，读取文件夹结构
                    file_list = self.get_folder_files(mod_file_path)
                    self.display_file_tree(file_list)
            except Exception as e:
                pass  # 加载文件树失败，不打印详细信息
                # 显示错误信息
                from PySide6.QtWidgets import QTreeWidgetItem
                error_item = QTreeWidgetItem(self.file_tree)
                error_item.setText(0, f"无法读取文件结构: {str(e)}")
    
    def get_mod_file_path(self, mod_name):
        """获取模组文件路径"""
        project_root = self.get_project_root()
        mods_dir = os.path.join(project_root, "mods")
        
        # 查找模组文件夹
        mod_folder_name = mod_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        mod_folder_path = os.path.join(mods_dir, mod_folder_name)
        
        if os.path.exists(mod_folder_path):
            # 查找zip文件或文件夹
            for item in os.listdir(mod_folder_path):
                item_path = os.path.join(mod_folder_path, item)
                if item.endswith('.zip') and os.path.isfile(item_path):
                    return item_path
                elif os.path.isdir(item_path) and item != 'modinfo':
                    return item_path
        
        return None
    
    def get_folder_files(self, folder_path):
        """获取文件夹中的所有文件路径"""
        file_list = []
        for root, dirs, files in os.walk(folder_path):
            # 跳过modinfo文件夹
            if 'modinfo' in dirs:
                dirs.remove('modinfo')
            rel_path = os.path.relpath(root, folder_path)
            if rel_path.startswith('modinfo') or os.path.basename(root) == 'modinfo':
                continue
            
            for file in files:
                # 获取相对路径
                rel_path = os.path.relpath(os.path.join(root, file), folder_path)
                file_list.append(rel_path.replace('\\', '/'))
            for dir in dirs:
                # 添加文件夹路径
                rel_path = os.path.relpath(os.path.join(root, dir), folder_path)
                file_list.append(rel_path.replace('\\', '/') + '/')
        
        return sorted(file_list)
    
    def load_mod_xml_info(self, mod_name):
        """加载模组XML信息到表单"""
        project_root = self.get_project_root()
        mods_dir = os.path.join(project_root, "mods")
        
        # 查找模组文件夹
        mod_folder_name = mod_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        mod_folder_path = os.path.join(mods_dir, mod_folder_name)
        
        if os.path.exists(mod_folder_path):
            modinfo_dir = os.path.join(mod_folder_path, "modinfo")
            xml_file_path = os.path.join(modinfo_dir, "modinfo.xml")
            
            if os.path.exists(xml_file_path):
                try:
                    import xml.etree.ElementTree as ET
                    tree = ET.parse(xml_file_path)
                    root = tree.getroot()
                    
                    # 读取XML中的信息
                    xml_name = self.get_xml_text(root, 'name')
                    xml_category = self.get_xml_text(root, 'category')
                    xml_author = self.get_xml_text(root, 'author')
                    xml_description = self.get_xml_text(root, 'description')
                    
                    # 使用XML中的信息更新表单（XML信息优先级更高）
                    if xml_name and xml_name.strip():
                        self.mod_name_input.setText(xml_name.strip())
                    
                    if xml_category and xml_category.strip():
                        # 支持多分类（分号分隔），直接设置到输入框
                        self.category_input.setText(xml_category.strip())
                    
                    if xml_author and xml_author.strip():
                        index = self.author_combo.findText(xml_author.strip())
                        if index >= 0:
                            self.author_combo.setCurrentIndex(index)
                        else:
                            # 如果作者不在下拉框中，添加到"添加新作者..."之前
                            add_new_index = self.author_combo.findText("添加新作者...")
                            if add_new_index >= 0:
                                self.author_combo.insertItem(add_new_index, xml_author.strip())
                            else:
                                self.author_combo.addItem(xml_author.strip())
                            self.author_combo.setCurrentText(xml_author.strip())
                            # 已添加新作者，不打印详细信息
                    
                    if xml_description and xml_description.strip():
                        self.description_input.setText(xml_description.strip())
                    
                    # 已加载XML信息，不打印详细信息
                    
                except Exception as e:
                    pass  # 读取XML文件失败，不打印详细信息
    
    def get_xml_text(self, root, tag):
        """安全获取XML元素文本"""
        element = root.find(tag)
        return element.text if element is not None and element.text else ""
    
    def update_mod_xml(self, mod_name, category, author, description):
        """更新模组XML文件"""
        import xml.etree.ElementTree as ET
        
        project_root = self.get_project_root()
        mods_dir = os.path.join(project_root, "mods")
        
        # 查找模组文件夹
        mod_folder_name = mod_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        mod_folder_path = os.path.join(mods_dir, mod_folder_name)
        
        if os.path.exists(mod_folder_path):
            modinfo_dir = os.path.join(mod_folder_path, "modinfo")
            xml_file_path = os.path.join(modinfo_dir, "modinfo.xml")
            
            if os.path.exists(xml_file_path):
                # 读取并更新XML
                tree = ET.parse(xml_file_path)
                root = tree.getroot()
                
                # 更新或创建元素
                name_elem = root.find('name')
                if name_elem is None:
                    name_elem = ET.SubElement(root, 'name')
                name_elem.text = mod_name
                
                if category and category != "未分类":
                    category_elem = root.find('category')
                    if category_elem is None:
                        category_elem = ET.SubElement(root, 'category')
                    category_elem.text = category
                
                if author and author != "未知":
                    author_elem = root.find('author')
                    if author_elem is None:
                        author_elem = ET.SubElement(root, 'author')
                    author_elem.text = author
                
                if description:
                    description_elem = root.find('description')
                    if description_elem is None:
                        description_elem = ET.SubElement(root, 'description')
                    description_elem.text = description
                
                # 保存XML
                tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
    
    def show_import_panel(self):
        """显示导入面板"""
        if hasattr(self, 'import_panel') and self.import_panel:
            # 使用动画显示已存在的面板
            self._show_import_panel_with_animation()
            return
        
        # 创建导入面板 - 使用create_import_panel方法
        self.import_panel = self.create_import_panel()
        
        # 使用动画显示面板
        self._show_import_panel_with_animation()
    
    def show_panel_with_animation(self, panel, animation_type="fade_in", duration=400, position_center=True):
        """
        通用的面板动画显示方法
        
        Args:
            panel: 要显示的面板
            animation_type: 动画类型 ("fade_in", "slide_in_from_right", "slide_in_from_bottom", "scale_in")
            duration: 动画持续时间（毫秒）
            position_center: 是否居中显示
        """
        if position_center:
            # 计算居中位置
            main_window_size = self.size()
            panel_size = panel.size()
            x = (main_window_size.width() - panel_size.width()) // 2
            y = (main_window_size.height() - panel_size.height()) // 2
        else:
            # 覆盖整个主窗口
            x = 0
            y = 0
        
        # 设置父窗口和位置
        panel.setParent(self)
        panel.move(x, y)
        panel.raise_()
        
        # 使用动画显示
        self.animation_manager.transition_to(
            panel, 
            animation_type=animation_type, 
            duration=duration
        )
    
    def hide_panel_with_animation(self, panel, animation_type="fade_out", duration=300, callback=None):
        """
        通用的面板动画隐藏方法
        
        Args:
            panel: 要隐藏的面板
            animation_type: 动画类型 ("fade_out", "slide_out_to_right", "slide_out_to_bottom", "scale_out")
            duration: 动画持续时间（毫秒）
            callback: 动画完成后的回调函数
        """
        def on_hide_complete():
            """默认的隐藏完成回调"""
            panel.hide()
            if callback:
                callback()
        
        self.animation_manager.hide_current(
            panel, 
            animation_type=animation_type, 
            duration=duration, 
            callback=on_hide_complete
        )
    
    def load_existing_mods(self):
        """加载已存在的模组，按导入顺序排列"""
        import xml.etree.ElementTree as ET
        import time
        
        project_root = self.get_project_root()
        mods_dir = os.path.join(project_root, "mods")
        
        if not os.path.exists(mods_dir):
            return
        
        # 加载mod状态以获取导入时间
        try:
            mod_states = self.load_mod_states()
        except:
            mod_states = {}
        
        # 收集所有mod信息
        mods_list = []
        
        # 遍历mods目录下的所有文件夹
        for mod_folder_name in os.listdir(mods_dir):
            mod_folder_path = os.path.join(mods_dir, mod_folder_name)
            if os.path.isdir(mod_folder_path):
                # 检查是否有modinfo.xml文件
                modinfo_dir = os.path.join(mod_folder_path, "modinfo")
                xml_file_path = os.path.join(modinfo_dir, "modinfo.xml")
                
                mod_name = mod_folder_name.replace("_", " ")
                category = "未分类"
                author = "未知"
                
                if os.path.exists(xml_file_path):
                    try:
                        # 解析XML文件
                        tree = ET.parse(xml_file_path)
                        root = tree.getroot()
                        
                        name_elem = root.find('name')
                        if name_elem is not None and name_elem.text:
                            mod_name = name_elem.text
                        
                        category_elem = root.find('category')
                        if category_elem is not None and category_elem.text:
                            category = category_elem.text
                        
                        author_elem = root.find('author')
                        if author_elem is not None and author_elem.text:
                            author = author_elem.text
                    except Exception as e:
                        pass  # 解析模组XML失败，不打印详细信息
                
                # 获取导入时间（如果没有则使用文件夹修改时间作为默认值）
                mod_state = mod_states.get(mod_name, {})
                if isinstance(mod_state, bool):
                    import_time = os.path.getmtime(mod_folder_path)  # 使用文件夹修改时间
                else:
                    import_time = mod_state.get("import_time", os.path.getmtime(mod_folder_path))
                
                mods_list.append({
                    "name": mod_name,
                    "category": category,
                    "author": author,
                    "import_time": import_time
                })
        
        # 按导入时间排序（早导入的在前）
        mods_list.sort(key=lambda x: x["import_time"])
        
        # 按顺序添加到表格
        for mod_info in mods_list:
            self.add_mod_to_table(mod_info["name"], mod_info["category"], mod_info["author"], check_unknown=False)
        
        # 加载完成后，应用忽略规则（隐藏被忽略的mod）
        self.apply_ignore_rules()
    
    def refresh_mod_list(self):
        """刷新mod列表，重新加载所有mod"""
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve
        
        # 清空当前表格
        self.mod_table.setRowCount(0)
        self.mod_table.checkbox_widgets.clear()
        # 清空收藏行集合
        if hasattr(self.mod_table, 'favorite_rows'):
            self.mod_table.favorite_rows.clear()
        
        # 创建闪烁动画
        animation = QPropertyAnimation(self.btn_refresh, b"styleSheet")
        animation.setDuration(1500)  # 1.5秒，足够慢
        animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        
        # 定义闪烁样式
        normal_style = f"""
            QPushButton {{
                background-color: white;
                border: 1px solid {COLOR_BG_GRAY};
                border-radius: {BORDER_RADIUS - 2}px;
                font-size: 16px;
            }}
        """
        
        highlight_style = f"""
            QPushButton {{
                background-color: rgba(255, 182, 193, 255);
                border: 2px solid #8B4513;
                border-radius: {BORDER_RADIUS - 2}px;
                font-size: 16px;
            }}
        """
        
        # 设置动画关键帧
        animation.setStartValue(normal_style)
        animation.setKeyValueAt(0.3, highlight_style)
        animation.setKeyValueAt(0.6, normal_style)
        animation.setKeyValueAt(0.9, highlight_style)
        animation.setEndValue(normal_style)
        
        # 启动动画
        animation.start()
        
        # 重新加载所有mod
        self.load_existing_mods()
        
        # 应用忽略规则（隐藏被忽略的mod）
        self.apply_ignore_rules()
        
        # 更新统计信息
        self.update_statistics()
        
        print(f"[成功] mod列表已刷新")
    
    def show_category_selection_dialog(self):
        """显示分类选择弹窗"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QScrollArea, QWidget, QGridLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("选择分类")
        dialog.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # 获取所有分类（从配置文件）
        try:
            categories = self.load_categories()
            if not categories:
                categories = ["邦邦"]
        except:
            categories = ["邦邦"]
        
        # 获取当前已选择的分类
        current_text = self.category_input.text().strip()
        selected_categories = [cat.strip() for cat in current_text.split(';') if cat.strip()]
        
        # 合并所有标签：配置文件中的标签 + 当前已选择但不在配置文件中的标签
        all_categories = list(categories)
        for cat in selected_categories:
            if cat not in all_categories:
                all_categories.append(cat)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QGridLayout()
        scroll_layout.setSpacing(10)
        scroll_widget.setLayout(scroll_layout)
        
        # 创建复选框
        checkboxes = {}
        row = 0
        col = 0
        max_cols = 3  # 默认每行3个，会根据文本长度调整
        
        for category in all_categories:
            checkbox = QCheckBox(category)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #000000;
                    font-size: 12px;
                    padding: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
            """)
            
            # 如果已选择，设置为选中
            if category in selected_categories:
                checkbox.setChecked(True)
            
            # 根据文本长度调整列数
            text_width = len(category) * 8  # 估算文本宽度
            if text_width > 80:
                max_cols = max(1, max_cols - 1)
            
            scroll_layout.addWidget(checkbox, row, col)
            checkboxes[category] = checkbox
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # 添加新标签选项
        add_new_checkbox = QCheckBox("添加新标签...")
        add_new_checkbox.setStyleSheet("""
            QCheckBox {
                color: #000000;
                font-size: 12px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
        """)
        scroll_layout.addWidget(add_new_checkbox, row, col)
        checkboxes["添加新标签..."] = add_new_checkbox
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        confirm_btn = QPushButton("确定")
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #000000;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #000000;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """)
        
        def on_confirm():
            selected = []
            for category, checkbox in checkboxes.items():
                if checkbox.isChecked() and category != "添加新标签...":
                    selected.append(category)
            
            # 处理添加新标签
            if checkboxes["添加新标签..."].isChecked():
                from PySide6.QtWidgets import QInputDialog
                new_tag, ok = QInputDialog.getText(dialog, "添加新标签", "请输入新的分类标签:")
                if ok and new_tag.strip():
                    self.save_category(new_tag.strip())
                    selected.append(new_tag.strip())
            
            # 更新输入框（即使为空也要更新，以清除之前的标签）
            self.category_input.setText('; '.join(selected))
            
            dialog.accept()
        
        # 实时更新输入框（当复选框状态改变时）
        def on_checkbox_changed():
            selected = []
            for category, checkbox in checkboxes.items():
                if checkbox.isChecked() and category != "添加新标签...":
                    selected.append(category)
            # 实时更新输入框
            self.category_input.setText('; '.join(selected))
        
        # 为所有复选框连接状态改变事件
        for checkbox in checkboxes.values():
            checkbox.stateChanged.connect(on_checkbox_changed)
        
        confirm_btn.clicked.connect(on_confirm)
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(confirm_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 根据内容自适应大小
        dialog.adjustSize()
        dialog.setMinimumWidth(300)
        dialog.setMaximumWidth(500)
        
        dialog.exec()
    
    def on_category_selected(self, text):
        """分类选择事件，选择后自动添加到输入框并隐藏下拉框"""
        if not text or text == "添加新标签...":
            # 如果是"添加新标签..."，弹出输入对话框
            if text == "添加新标签...":
                from PySide6.QtWidgets import QInputDialog
                new_tag, ok = QInputDialog.getText(self, "添加新标签", "请输入新的分类标签:")
                
                if ok and new_tag.strip():
                    # 保存新标签到配置文件
                    self.save_category(new_tag.strip())
                    
                    # 移除"添加新标签..."选项
                    self.category_combo.removeItem(self.category_combo.count() - 1)
                    # 添加新标签
                    self.category_combo.addItem(new_tag.strip())
                    # 重新添加"添加新标签..."选项
                    self.category_combo.addItem("添加新标签...")
                    # 选择新添加的标签
                    self.category_combo.setCurrentText(new_tag.strip())
                    # 添加到输入框
                    text = new_tag.strip()
                else:
                    # 用户取消，隐藏下拉框
                    self.category_combo.hide()
                    return
            else:
                # 空选择，隐藏下拉框
                self.category_combo.hide()
                return
        
        # 获取当前输入框的内容
        current_text = self.category_input.text().strip()
        
        # 解析现有分类（用分号分隔）
        existing_categories = [cat.strip() for cat in current_text.split(';') if cat.strip()]
        
        # 检查是否已存在
        if text not in existing_categories:
            # 添加到列表
            existing_categories.append(text)
            # 用分号连接并更新输入框
            new_text = '; '.join(existing_categories)
            self.category_input.setText(new_text)
        
        # 隐藏下拉框
        self.category_combo.hide()
        # 重置下拉框选择到第一项
        self.category_combo.setCurrentIndex(0)
    
    def on_category_changed(self, text):
        """分类选择变化事件（保留用于兼容性，但不再使用）"""
        pass
    
    def hide_import_panel(self):
        """隐藏导入面板"""
        if not hasattr(self, 'import_panel') or not self.import_panel:
            return
        
        # 简化：直接隐藏，确保功能正常
        self.import_panel.hide()
        # 确保表格显示（如果存在）
        if hasattr(self, 'mod_table_widget'):
            self.mod_table_widget.show()
        
        # 清理面板引用
        self.import_panel.deleteLater()
        delattr(self, 'import_panel')
    
    def create_mod_table(self):
        """创建左侧Mod表格"""
        # 使用自定义表格类
        try:
            self.mod_table = CustomModTable()
        except Exception as e:
            # 如果创建表格失败，创建一个空的表格作为后备
            print(f"[警告] 创建表格失败: {e}")
            import traceback
            traceback.print_exc()
            from PySide6.QtWidgets import QTableWidget
            self.mod_table = QTableWidget()
        
        # 初始为空表
        self.mod_table.setRowCount(0)
        
        # 连接统计变化信号到更新方法
        self.mod_table.statistics_changed.connect(self.update_statistics)
        
        return self.mod_table
    
    def create_right_button_bar(self):
        """创建右侧垂直按钮面板"""
        button_bar_widget = QWidget()
        button_bar_layout = QVBoxLayout()
        button_bar_layout.setSpacing(SPACING_BASE)  # 垂直间距（8px）
        button_bar_layout.setContentsMargins(SPACING_BASE, SPACING_BASE, SPACING_BASE, SPACING_BASE)  # 边距（8px）
        button_bar_widget.setLayout(button_bar_layout)
        
        # 设置面板最小宽度200px，允许拉伸时适当调整
        button_bar_widget.setMinimumWidth(200)
        # 设置面板最大宽度，防止过度拉伸
        button_bar_widget.setMaximumWidth(250)
        
        # 设置按钮栏背景为透明（使用卡片按钮设计）
        button_bar_widget.setStyleSheet("background-color: transparent;")
        
        # 创建8个按钮，每个按钮带Qt标准图标和文字
        # 获取QApplication的style对象用于获取标准图标
        app = QApplication.instance()
        style = app.style() if app else None
        
        # 1. [导入Mod] - SP_DialogOpenButton图标
        self.btn_import_mod = QPushButton("导入Mod")
        if style:
            self.btn_import_mod.setIcon(style.standardIcon(QStyle.SP_DialogOpenButton))
        # 连接点击事件到文件选择功能
        self.btn_import_mod.clicked.connect(self.open_file_dialog)
        
        # 2. [导出选中] - SP_DialogSaveButton图标
        self.btn_export_selected = QPushButton("导出选中")
        if style:
            self.btn_export_selected.setIcon(style.standardIcon(QStyle.SP_DialogSaveButton))
        
        # 3. [标签管理] - SP_FileDialogDetailedView图标
        self.btn_tag_manage = QPushButton("标签管理")
        if style:
            self.btn_tag_manage.setIcon(style.standardIcon(QStyle.SP_FileDialogDetailedView))
        
        # 4. [字典管理] - SP_FileDialogContentsView图标
        self.btn_dict_manage = QPushButton("字典管理")
        if style:
            self.btn_dict_manage.setIcon(style.standardIcon(QStyle.SP_FileDialogContentsView))
        
        # 5. [脚本管理] - SP_ComputerIcon图标
        self.btn_script_manage = QPushButton("脚本管理")
        if style:
            self.btn_script_manage.setIcon(style.standardIcon(QStyle.SP_ComputerIcon))
        
        # 6. [主题管理] - SP_DriveCDIcon图标
        self.btn_theme_manage = QPushButton("主题管理")
        if style:
            self.btn_theme_manage.setIcon(style.standardIcon(QStyle.SP_DriveCDIcon))
        
        # 7. [高级设置] - SP_FileDialogInfoView图标
        self.btn_advanced_settings = QPushButton("高级设置")
        if style:
            self.btn_advanced_settings.setIcon(style.standardIcon(QStyle.SP_FileDialogInfoView))
        
        # 8. [启动游戏] - SP_MediaPlay图标
        self.btn_launch_game = QPushButton("启动游戏")
        if style:
            self.btn_launch_game.setIcon(style.standardIcon(QStyle.SP_MediaPlay))
        
        # 连接高级设置按钮
        self.btn_advanced_settings.clicked.connect(self.show_advanced_settings_panel)
        
        # 连接主题管理按钮
        self.btn_theme_manage.clicked.connect(self.show_theme_settings_panel)
        
        # 连接标签管理按钮
        self.btn_tag_manage.clicked.connect(self.show_tag_management_panel)
        
        # 连接未实现功能的按钮
        self.btn_dict_manage.clicked.connect(self.show_unimplemented_feature_message)
        self.btn_script_manage.clicked.connect(self.show_unimplemented_feature_message)
        
        # 连接导出选中按钮
        self.btn_export_selected.clicked.connect(self.export_selected_mods)
        
        # 按钮列表（不包括启动游戏按钮）
        buttons = [
            self.btn_import_mod,
            self.btn_export_selected,
            self.btn_tag_manage,
            self.btn_dict_manage,
            self.btn_script_manage,
            self.btn_theme_manage,
            self.btn_advanced_settings
        ]
        
        # 设置普通按钮最小尺寸，允许拉伸时适当调整
        button_min_width = 180
        button_min_height = 44
        
        # 获取样式表
        button_style = self.get_sidebar_button_style()
        
        for btn in buttons:
            btn.setFixedSize(button_min_width, button_min_height)  # 改回固定尺寸，确保对齐
            btn.setStyleSheet(button_style)
            # 设置图标大小（18x18像素）
            btn.setIconSize(QSize(18, 18))
            # 添加阴影效果
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(SHADOW_BLUR)
            shadow.setXOffset(0)
            shadow.setYOffset(SHADOW_OFFSET_Y)
            shadow.setColor(QColor(0, 0, 0, SHADOW_OPACITY))
            btn.setGraphicsEffect(shadow)
        
        # 添加普通按钮到布局（居左对齐）
        for btn in buttons:
            button_bar_layout.addWidget(btn, alignment=Qt.AlignLeft)
        
        # 添加弹性空间，将按钮推到顶部，统计面板和启动游戏按钮推到底部
        button_bar_layout.addStretch()
        
        # 创建并添加统计信息面板
        statistics_panel = self.create_statistics_panel()
        button_bar_layout.addWidget(statistics_panel)
        
        # 紧接着添加启动游戏按钮，无额外间距
        launch_button_width = 180
        launch_button_height = 52  # 比其他按钮高8px
        self.btn_launch_game.setFixedSize(launch_button_width, launch_button_height)
        # 启动游戏按钮使用强调色
        launch_style = self.get_launch_button_style()
        self.btn_launch_game.setStyleSheet(launch_style)
        self.btn_launch_game.setIconSize(QSize(20, 20))  # 图标也稍大一些
        # 添加阴影效果
        shadow_launch = QGraphicsDropShadowEffect()
        shadow_launch.setBlurRadius(SHADOW_BLUR + 2)
        shadow_launch.setXOffset(0)
        shadow_launch.setYOffset(SHADOW_OFFSET_Y)
        shadow_launch.setColor(QColor(255, 140, 0, SHADOW_OPACITY + 20))  # 橙色阴影
        self.btn_launch_game.setGraphicsEffect(shadow_launch)
        self.btn_launch_game.clicked.connect(self.launch_game)
        button_bar_layout.addWidget(self.btn_launch_game, alignment=Qt.AlignLeft)
        
        return button_bar_widget
    
    def create_statistics_panel(self):
        """创建Mod统计信息面板 - 简洁文本框布局"""
        # 创建面板容器
        panel_widget = QWidget()
        
        # 设置面板最小宽度，确保统计信息始终可见
        panel_widget.setMinimumWidth(160)
        
        # 使用垂直布局，取消间距
        layout = QVBoxLayout()
        layout.setSpacing(0)  # 取消组件之间的间距
        layout.setContentsMargins(5, 0, 5, 0)  # 只保留左右边距，取消上下边距
        panel_widget.setLayout(layout)
        
        # 创建一个文本框显示所有统计信息
        stats_text = QLabel()
        # 移除固定高度，让内容自适应高度（在原有基础上增加10px）
        stats_text.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid black;
                color: black;
                font-weight: bold;
                font-size: 9.6px;  /* 从12px减小20%，即 12 * 0.8 = 9.6px */
                padding: 7px;  /* 增加内边距，使文本框变高 */
            }
        """)
        stats_text.setWordWrap(True)
        
        # 保存引用以便更新
        self.stats_text = stats_text
        
        # 添加到布局
        layout.addWidget(stats_text)
        
        # 初始化统计值
        self.update_statistics()
        
        return panel_widget
    
    def update_statistics(self):
        """更新Mod统计信息"""
        if not hasattr(self, 'mod_table'):
            return
        
        # 获取表格数据
        total_mods = self.mod_table.rowCount()
        enabled_count = self.mod_table.get_enabled_count()
        
        # 检查是否启用虚拟映射
        settings = self.load_advanced_settings()
        use_virtual_mapping = settings.get('virtual_mapping', False)
        
        # 如果是虚拟映射模式，占用空间显示"--"
        if use_virtual_mapping:
            size_str = "--"
        else:
            # 计算启用的mod占用空间
            enabled_mods = self.mod_table.get_enabled_mods()
            if not enabled_mods:
                size_str = "--"
            else:
                total_size = 0
                project_root = self.get_project_root()
                mods_dir = os.path.join(project_root, "mods")
                
                for mod_name in enabled_mods:
                    mod_folder_name = mod_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
                    mod_folder_path = os.path.join(mods_dir, mod_folder_name)
                    
                    if os.path.exists(mod_folder_path):
                        # 计算文件夹大小（排除modinfo文件夹）
                        for root, dirs, files in os.walk(mod_folder_path):
                            # 跳过modinfo文件夹
                            if 'modinfo' in dirs:
                                dirs.remove('modinfo')
                            for file in files:
                                file_path = os.path.join(root, file)
                                if os.path.exists(file_path):
                                    total_size += os.path.getsize(file_path)
                
                # 转换为MB
                size_mb = total_size / (1024 * 1024)
                size_str = f"{size_mb:.2f} MB"
        
        # 更新统计信息到文本框
        if hasattr(self, 'stats_text'):
            stats_text = f"""Mod统计信息
总Mod数: {total_mods}
已启用: {enabled_count}
占用空间: {size_str}"""
            self.stats_text.setText(stats_text)
    
    def apply_window_background(self):
        """应用窗口背景 - 背景图片始终铺满窗口"""
        try:
            # 获取背景图片路径，兼容开发环境和打包环境
            background_image = self.get_background_path("background.png")
            
            # 检查文件是否存在，如果存在则使用背景图片，否则使用渐变背景
            if os.path.exists(background_image):
                # 将Windows路径中的反斜杠转换为正斜杠，直接使用本地路径
                background_url = background_image.replace("\\", "/")
                
                # 构建窗口背景样式
                # Qt样式表不支持background-size，需要使用其他方式
                # 使用 #centralWidget 选择器只影响这个特定widget，不会影响子组件
                window_style = f"""
                    QWidget#centralWidget {{
                        background-image: url('{background_url}');
                        background-position: center;
                        background-repeat: no-repeat;
                    }}
                """
                self.setStyleSheet(window_style)
            else:
                # 使用极浅渐变背景（左上浅白→右下浅灰）
                window_style = f"""
                    QWidget#centralWidget {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 rgba(255, 255, 255, 255), stop:1 {COLOR_BG_LIGHT});
                    }}
                """
                self.setStyleSheet(window_style)
                print(f"[调试] 使用渐变背景，图片不存在: {background_image}")
        except Exception as e:
            # 如果背景设置失败，使用默认渐变背景，确保窗口能正常显示
            print(f"[警告] 应用窗口背景失败: {e}")
            try:
                window_style = f"""
                    QWidget#centralWidget {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 rgba(255, 255, 255, 255), stop:1 {COLOR_BG_LIGHT});
                    }}
                """
                self.setStyleSheet(window_style)
            except:
                pass  # 如果连默认背景都设置失败，就跳过
    
    def get_sidebar_button_style(self):
        """获取侧边栏按钮的QSS样式 - 卡片设计"""
        return f"""
            /* 正常状态：白色卡片，圆角，阴影 */
            QPushButton {{
                background-color: white;
                color: {COLOR_TEXT_DARK};
                border: 1px solid rgba(0, 0, 0, 8);
                border-radius: {BORDER_RADIUS}px;
                padding: 10px 16px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
            }}
            
            /* 悬停状态：主色调背景，背景透明度增加 */
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY};
                color: {COLOR_TEXT_LIGHT};
                border: 1px solid {COLOR_PRIMARY};
            }}
            
            /* 按下状态：稍深的主色调 */
            QPushButton:pressed {{
                background-color: {COLOR_PRIMARY_ALT};
                border: 1px solid {COLOR_PRIMARY_ALT};
                padding-top: 11px;
                padding-bottom: 9px;
            }}
        """
    
    def get_launch_button_style(self):
        """获取启动游戏按钮的QSS样式 - 使用强调色"""
        return f"""
            /* 正常状态：强调色卡片，更大更突出 */
            QPushButton {{
                background-color: {COLOR_ACCENT};
                color: {COLOR_TEXT_LIGHT};
                border: none;
                border-radius: {BORDER_RADIUS}px;
                padding: 12px 16px;
                text-align: left;
                font-size: 15px;
                font-weight: 600;
            }}
            
            /* 悬停状态：更亮的强调色 */
            QPushButton:hover {{
                background-color: #FFA500;
            }}
            
            /* 按下状态 */
            QPushButton:pressed {{
                background-color: #E67E00;
                padding-top: 13px;
                padding-bottom: 11px;
            }}
        """
    
    def check_mod_conflicts(self, enabled_mods):
        """检测mod之间的冲突（检测是否有mod修改了相同的文件）"""
        project_root = self.get_project_root()
        mods_dir = os.path.join(project_root, "mods")
        
        # 存储每个文件被哪些mod修改
        file_mod_map = {}  # {文件路径: [mod列表]}
        conflicts = []  # [(mod1, mod2, 冲突文件)]
        
        for mod_name in enabled_mods:
            mod_folder_name = mod_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
            mod_folder_path = os.path.join(mods_dir, mod_folder_name)
            
            if not os.path.exists(mod_folder_path):
                continue
            
            # 遍历mod文件夹（排除modinfo文件夹）
            for root, dirs, files in os.walk(mod_folder_path):
                # 计算相对路径
                rel_path = os.path.relpath(root, mod_folder_path)
                
                # 跳过modinfo文件夹及其子目录
                if rel_path.startswith('modinfo') or os.path.basename(root) == 'modinfo':
                    if 'modinfo' in dirs:
                        dirs.remove('modinfo')
                    continue
                
                # 记录文件
                for file in files:
                    if rel_path == '.':
                        file_path = file
                    else:
                        file_path = os.path.join(rel_path, file).replace('\\', '/')
                    
                    if file_path not in file_mod_map:
                        file_mod_map[file_path] = []
                    file_mod_map[file_path].append(mod_name)
        
        # 检测冲突（同一个文件被多个mod修改）
        for file_path, mods in file_mod_map.items():
            if len(mods) > 1:
                # 找到所有冲突的mod对
                for i in range(len(mods)):
                    for j in range(i + 1, len(mods)):
                        conflicts.append((mods[i], mods[j], file_path))
        
        return conflicts
    
    def import_mods_to_game(self):
        """导入勾选的mod到游戏根目录"""
        # 获取游戏根目录
        settings = self.load_advanced_settings()
        game_path = settings.get('game_path', '')
        
        if not game_path or not os.path.exists(game_path):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "错误", "请先在高级设置中设置游戏根目录！")
            return
        
        # 获取所有启用的mod
        enabled_mods = self.mod_table.get_enabled_mods()
        
        if not enabled_mods:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "提示", "没有启用的mod！")
            return
        
        # 检测mod之间的冲突
        conflicts = self.check_mod_conflicts(enabled_mods)
        
        # 如果有冲突，显示冲突处理界面（占位）
        if conflicts:
            self.show_conflict_resolution_dialog(conflicts)
            return
        
        # 没有冲突，可以启动游戏（文件已在启用时自动导入）
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "就绪", "所有mod已就绪，可以启动游戏！")
    
    def launch_game(self):
        """启动游戏"""
        import subprocess
        
        # 获取游戏根目录
        settings = self.load_advanced_settings()
        game_path = settings.get('game_path', '')
        
        if not game_path or not os.path.exists(game_path):
            QMessageBox.warning(self, "错误", "请先在高级设置中设置游戏根目录！")
            return
        
        # 尝试找到游戏可执行文件（常见的几种可能）
        possible_exe_names = [
            "MonsterHunterWorld.exe",  # Monster Hunter World
            "game.exe",
            "mhw.exe"
        ]
        
        game_exe = None
        for exe_name in possible_exe_names:
            exe_path = os.path.join(game_path, exe_name)
            if os.path.exists(exe_path):
                game_exe = exe_path
                break
        
        # 如果没找到，让用户选择
        if not game_exe:
            exe_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择游戏可执行文件",
                game_path,
                "可执行文件 (*.exe);;所有文件 (*.*)"
            )
            if exe_path:
                game_exe = exe_path
            else:
                return
        
        # 启动游戏
        try:
            # 切换到游戏目录
            os.chdir(game_path)
            # 启动游戏进程
            subprocess.Popen([game_exe], cwd=game_path)
            print(f"[成功] 游戏启动: {game_exe}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动游戏失败：{str(e)}")
            print(f"[失败] 游戏启动失败: {str(e)}")
    
    def on_search_focus_out(self):
        """搜索框失去焦点时的处理"""
        search_text = self.search_input.text().strip()
        # 如果搜索框为空，重新应用忽略规则
        if not search_text:
            self.apply_ignore_rules()
    
    def apply_ignore_rules(self):
        """应用忽略规则：隐藏被忽略的mod"""
        for row in range(self.mod_table.rowCount()):
            name_item = self.mod_table.item(row, 1)
            if name_item:
                mod_name = name_item.text()
                is_ignored = self.is_mod_ignored(mod_name)
                if is_ignored:
                    self.mod_table.hideRow(row)
                else:
                    self.mod_table.showRow(row)
    
    def filter_mods_by_search(self, search_text):
        """根据搜索文本过滤mod列表，适配忽略规则"""
        search_text = search_text.strip().lower()
        is_searching = bool(search_text)  # 是否正在搜索
        
        # 遍历所有行
        for row in range(self.mod_table.rowCount()):
            # 获取mod名称
            name_item = self.mod_table.item(row, 1)
            if not name_item:
                continue
            
            mod_name = name_item.text()
            
            # 检查mod是否被忽略
            is_ignored = self.is_mod_ignored(mod_name)
            
            # 如果搜索为空，应用忽略规则（隐藏被忽略的mod）
            if not search_text:
                if is_ignored:
                    self.mod_table.setRowHidden(row, True)
                else:
                    self.mod_table.setRowHidden(row, False)
                continue
            
            # 如果正在搜索，显示所有匹配的mod（包括被忽略的）
            category_item = self.mod_table.item(row, 2)
            author_item = self.mod_table.item(row, 3)
            
            # 检查是否匹配（不区分大小写）
            name = mod_name.lower()
            category = category_item.text().lower() if category_item else ""
            author = author_item.text().lower() if author_item else ""
            
            # 如果任何字段包含搜索文本，显示该行（即使被忽略）
            if search_text in name or search_text in category or search_text in author:
                self.mod_table.setRowHidden(row, False)
            else:
                self.mod_table.setRowHidden(row, True)
    
    def apply_mod_to_game(self, mod_name, enabled):
        """应用或移除单个mod到游戏根目录（启用时复制，禁用时删除）
        
        Returns:
            bool: 如果enabled=True，返回是否成功；如果enabled=False，返回True
        """
        # 获取游戏根目录
        settings = self.load_advanced_settings()
        game_path = settings.get('game_path', '')
        
        if not game_path:
            return False
        
        if not os.path.exists(game_path):
            return False
        
        # 获取mods目录
        project_root = self.get_project_root()
        mods_dir = os.path.join(project_root, "mods")
        
        # 获取mod文件夹路径（mod名称转换为文件夹名）
        mod_folder_name = mod_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        mod_folder_path = os.path.join(mods_dir, mod_folder_name)
        
        if not os.path.exists(mod_folder_path):
            return False
        
        import shutil
        
        if enabled:
            # 启用前先检查文件完整性
            integrity_check = self.check_mod_file_integrity(mod_name, mod_folder_path)
            if not integrity_check['is_complete']:
                # 文件不完整，显示弹窗让用户选择
                result = self.show_mod_file_modified_dialog(mod_name)
                if result == 'cancel':
                    # 取消启用
                    return False
                elif result == 'save_and_enable':
                    # 保存当前模组并启用：更新XML中的文件结构
                    self.update_mod_file_structure(mod_name, mod_folder_path)
                elif result == 'uninstall':
                    # 卸载模组
                    row = self.find_mod_row(mod_name)
                    if row >= 0:
                        self.uninstall_mod_permanently(mod_name, row)
                    return False
            
            # 启用前检查文件冲突
            conflict_result = self.check_and_resolve_conflicts(mod_name, mod_folder_path)
            if conflict_result == 'cancel':
                # 取消启用
                return False
            elif conflict_result == 'override':
                # 直接覆盖，继续执行
                pass
            elif conflict_result == 'manual':
                # 手动修改优先级，已经在check_and_resolve_conflicts中处理
                pass
            
            # 启用：复制文件到游戏目录或创建符号链接
            use_virtual_mapping = settings.get('virtual_mapping', False)
            
            copied_count = 0
            symlink_count = 0
            failed_count = 0
            has_permission_error = False
            
            for root, dirs, files in os.walk(mod_folder_path):
                # 计算相对路径
                rel_path = os.path.relpath(root, mod_folder_path)
                
                # 跳过modinfo文件夹及其子目录
                if rel_path.startswith('modinfo') or os.path.basename(root) == 'modinfo':
                    if 'modinfo' in dirs:
                        dirs.remove('modinfo')
                    continue
                
                if rel_path == '.':
                    target_dir = game_path
                else:
                    target_dir = os.path.join(game_path, rel_path)
                
                # 确保目标目录存在
                os.makedirs(target_dir, exist_ok=True)
                
                # 复制文件或创建符号链接
                for file in files:
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(target_dir, file)
                    
                    try:
                        if use_virtual_mapping:
                            # 使用符号链接（虚拟映射）- 不复制文件，只创建符号链接
                            # 确保使用绝对路径（Windows符号链接需要绝对路径）
                            source_file_abs = os.path.abspath(source_file)
                            
                            if os.path.exists(target_file):
                                # 如果已存在，先删除（可能是文件或链接）
                                if os.path.islink(target_file) or os.path.isfile(target_file):
                                    os.remove(target_file)
                            
                            # 创建符号链接
                            os.symlink(source_file_abs, target_file)
                            symlink_count += 1
                            # 验证符号链接是否创建成功（不打印，只在失败时打印）
                            if not os.path.islink(target_file):
                                print(f"[警告] 符号链接可能未生效: {file}")
                        else:
                            # 使用物理复制
                            shutil.copy2(source_file, target_file)
                            copied_count += 1
                    except OSError as e:
                        # Windows上可能需要管理员权限或开发者模式
                        if hasattr(e, 'winerror') and e.winerror == 1314:
                            has_permission_error = True
                            # 需要管理员权限，显示权限提示面板
                            if not hasattr(self, '_admin_permission_shown') or not self._admin_permission_shown:
                                self._admin_permission_shown = True
                                self.show_admin_permission_panel()
                            print(f"[失败] 创建符号链接失败: {file} (需要管理员权限或启用开发者模式)")
                        else:
                            print(f"[失败] 文件操作失败: {file} ({str(e)})")
                        failed_count += 1
                    except Exception as e:
                        print(f"[失败] 文件操作失败: {file} ({str(e)})")
                        failed_count += 1
            
            # 打印总结信息
            if use_virtual_mapping:
                if symlink_count > 0 and failed_count == 0:
                    print(f"[成功] mod应用成功: {mod_name} (虚拟映射: 成功创建 {symlink_count} 个符号链接)")
                    return True
                elif symlink_count > 0 and failed_count > 0:
                    print(f"[警告] mod应用部分成功: {mod_name} (成功: {symlink_count} 个符号链接, 失败: {failed_count} 个)")
                    # 如果有权限错误，返回False以回滚复选框
                    return not has_permission_error
                else:
                    # 全部失败，返回False以回滚复选框
                    print(f"[失败] mod应用失败: {mod_name} (未能创建任何符号链接)")
                    return False
            else:
                if copied_count > 0 and failed_count == 0:
                    print(f"[成功] mod应用成功: {mod_name} (物理复制: {copied_count} 个文件)")
                    return True
                elif copied_count > 0 and failed_count > 0:
                    print(f"[警告] mod应用部分成功: {mod_name} (成功: {copied_count} 个文件, 失败: {failed_count} 个)")
                    return False
                else:
                    # 全部失败，返回False以回滚复选框
                    print(f"[失败] mod应用失败: {mod_name} (未能复制任何文件)")
                    return False
        else:
            # 禁用：删除游戏目录中该mod的文件或符号链接
            use_virtual_mapping = settings.get('virtual_mapping', False)
            deleted_count = 0
            deleted_symlink_count = 0
            updated_symlink_count = 0
            failed_count = 0
            
            # 如果是虚拟映射，检查是否有其他启用的冲突mod
            next_priority_mod = None
            if use_virtual_mapping:
                # 获取该mod的所有冲突mod
                conflict_check = self.check_single_mod_conflicts(mod_name, mod_folder_path)
                if conflict_check['has_conflict']:
                    conflicting_mods = conflict_check['conflicting_mods']
                    
                    # 获取当前启用的mod
                    enabled_mods = self.mod_table.get_enabled_mods()
                    
                    # 找出仍然启用的冲突mod
                    enabled_conflicting_mods = [m for m in conflicting_mods if m in enabled_mods]
                    
                    if enabled_conflicting_mods:
                        # 有启用的冲突mod，需要找到下一个优先级的mod
                        # 获取优先级顺序
                        all_conflicting_mods = [mod_name] + conflicting_mods
                        priority_order = self.load_mod_priority(mod_name, conflicting_mods)
                        
                        if priority_order:
                            # 使用已保存的优先级顺序
                            # 找到当前mod在优先级中的位置
                            try:
                                current_index = priority_order.index(mod_name)
                                # 找到下一个优先级的mod（在当前mod之后，且仍然启用）
                                for i in range(current_index + 1, len(priority_order)):
                                    next_mod = priority_order[i]
                                    if next_mod in enabled_conflicting_mods:
                                        next_priority_mod = next_mod
                                        break
                            except ValueError:
                                pass
                        else:
                            # 没有保存的优先级，使用默认顺序（按列表顺序）
                            for mod in conflicting_mods:
                                if mod in enabled_conflicting_mods:
                                    next_priority_mod = mod
                                    break
            
            # 遍历该mod的所有文件
            mod_files = {}  # 存储文件路径映射 {相对路径: 目标文件路径}
            for root, dirs, files in os.walk(mod_folder_path):
                # 计算相对路径
                rel_path = os.path.relpath(root, mod_folder_path)
                
                # 跳过modinfo文件夹及其子目录
                if rel_path.startswith('modinfo') or os.path.basename(root) == 'modinfo':
                    if 'modinfo' in dirs:
                        dirs.remove('modinfo')
                    continue
                
                if rel_path == '.':
                    target_dir = game_path
                else:
                    target_dir = os.path.join(game_path, rel_path)
                
                # 收集文件信息
                for file in files:
                    target_file = os.path.join(target_dir, file)
                    if rel_path == '.':
                        file_rel_path = file
                    else:
                        file_rel_path = os.path.join(rel_path, file).replace('\\', '/')
                    mod_files[file_rel_path] = target_file
            
            # 处理每个文件
            for file_rel_path, target_file in mod_files.items():
                if not os.path.exists(target_file):
                    continue
                
                try:
                    is_symlink = os.path.islink(target_file)
                    
                    if use_virtual_mapping and next_priority_mod:
                        # 虚拟映射且有下一个优先级的mod，更新符号链接
                        # 获取下一个mod的文件路径
                        project_root = self.get_project_root()
                        mods_dir = os.path.join(project_root, "mods")
                        next_mod_folder_name = next_priority_mod.replace(" ", "_").replace("/", "_").replace("\\", "_")
                        next_mod_folder_path = os.path.join(mods_dir, next_mod_folder_name)
                        
                        # 构建下一个mod的源文件路径
                        if file_rel_path == os.path.basename(file_rel_path):
                            # 根目录文件
                            next_source_file = os.path.join(next_mod_folder_path, file_rel_path)
                        else:
                            # 子目录文件
                            next_source_file = os.path.join(next_mod_folder_path, file_rel_path)
                        
                        if os.path.exists(next_source_file):
                            # 删除旧的符号链接
                            if is_symlink or os.path.isfile(target_file):
                                os.remove(target_file)
                            
                            # 创建新的符号链接指向下一个优先级的mod
                            next_source_file_abs = os.path.abspath(next_source_file)
                            os.symlink(next_source_file_abs, target_file)
                            updated_symlink_count += 1
                        else:
                            # 下一个mod没有这个文件，删除符号链接
                            if is_symlink or os.path.isfile(target_file):
                                os.remove(target_file)
                            deleted_count += 1
                            if is_symlink:
                                deleted_symlink_count += 1
                    else:
                        # 没有下一个优先级的mod，删除文件或符号链接
                        if is_symlink or os.path.isfile(target_file):
                            os.remove(target_file)
                            deleted_count += 1
                            if is_symlink:
                                deleted_symlink_count += 1
                except Exception as e:
                    print(f"[失败] 操作失败: {file_rel_path} ({str(e)})")
                    failed_count += 1
            
            # 删除空目录（从最深开始）
            for root, dirs, files in os.walk(mod_folder_path, topdown=False):
                rel_path = os.path.relpath(root, mod_folder_path)
                
                if rel_path.startswith('modinfo') or os.path.basename(root) == 'modinfo':
                    continue
                
                if rel_path == '.':
                    continue
                
                target_dir = os.path.join(game_path, rel_path)
                if os.path.exists(target_dir):
                    try:
                        # 如果目录为空，删除它
                        if not os.listdir(target_dir):
                            os.rmdir(target_dir)
                    except Exception as e:
                        pass  # 删除目录失败，不打印详细信息
            
            # 打印禁用成功信息
            if use_virtual_mapping:
                if updated_symlink_count > 0:
                    # 有更新符号链接
                    if failed_count == 0:
                        print(f"[成功] mod禁用成功: {mod_name} (虚拟映射: 更新 {updated_symlink_count} 个符号链接 -> {next_priority_mod})")
                    else:
                        print(f"[警告] mod禁用部分成功: {mod_name} (虚拟映射: 更新 {updated_symlink_count} 个符号链接, 失败: {failed_count} 个)")
                elif deleted_symlink_count > 0 and failed_count == 0:
                    print(f"[成功] mod禁用成功: {mod_name} (虚拟映射: 删除 {deleted_symlink_count} 个符号链接)")
                elif deleted_symlink_count > 0 and failed_count > 0:
                    print(f"[警告] mod禁用部分成功: {mod_name} (虚拟映射: 成功删除 {deleted_symlink_count} 个符号链接, 失败: {failed_count} 个)")
                elif deleted_count == 0 and updated_symlink_count == 0:
                    print(f"[提示] mod禁用: {mod_name} (未找到需要处理的符号链接)")
            else:
                if deleted_count > 0 and failed_count == 0:
                    print(f"[成功] mod禁用成功: {mod_name} (物理复制: 删除 {deleted_count} 个文件)")
                elif deleted_count > 0 and failed_count > 0:
                    print(f"[警告] mod禁用部分成功: {mod_name} (物理复制: 成功删除 {deleted_count} 个文件, 失败: {failed_count} 个)")
                elif deleted_count == 0:
                    print(f"[提示] mod禁用: {mod_name} (未找到需要删除的文件)")
    
    def check_mod_file_integrity(self, mod_name, mod_folder_path):
        """检查mod文件完整性，对照XML中的文件结构
        只检查文件是否存在，不检查文件大小和修改时间（支持重新安装）
        
        Returns:
            dict: {
                'is_complete': bool,  # 文件是否完整
                'missing_files': list,  # 缺失的文件列表
                'extra_files': list,  # 额外的文件列表
            }
        """
        result = {
            'is_complete': True,
            'missing_files': [],
            'extra_files': []
        }
        
        # 读取XML中的文件结构
        modinfo_dir = os.path.join(mod_folder_path, "modinfo")
        xml_file_path = os.path.join(modinfo_dir, "modinfo.xml")
        
        if not os.path.exists(xml_file_path):
            # 如果没有XML文件，认为文件完整（可能是旧版本导入的mod，没有文件结构记录）
            return result
        
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            # 获取XML中记录的文件结构
            file_structure_elem = root.find("file_structure")
            if file_structure_elem is None:
                # 如果没有文件结构记录，认为文件完整（可能是旧版本导入的mod）
                return result
            
            # 获取XML中记录的文件路径（只取路径，不关心大小和修改时间）
            xml_file_paths = set()
            for file_elem in file_structure_elem.findall("file"):
                file_path = file_elem.text
                if file_path:
                    xml_file_paths.add(file_path)
            
            # 获取当前实际的文件结构
            current_files = set(self.get_folder_files(mod_folder_path))
            
            # 检查缺失的文件（XML中有但实际不存在）
            result['missing_files'] = []
            for file_path in xml_file_paths:
                if not file_path.endswith('/'):  # 只检查文件，不检查目录
                    # 将统一的分隔符转换为当前系统的分隔符，确保跨平台兼容
                    normalized_path = file_path.replace('/', os.sep).replace('\\', os.sep)
                    full_path = os.path.join(mod_folder_path, normalized_path)
                    if not os.path.exists(full_path):
                        result['missing_files'].append(file_path)
            
            # 检查额外的文件（实际有但XML中没有）
            # 排除modinfo文件夹，因为它是元数据，不在文件结构检查范围内
            result['extra_files'] = []
            for file_path in current_files:
                # 跳过modinfo文件夹及其内容
                if not file_path.startswith('modinfo'):
                    if file_path not in xml_file_paths:
                        result['extra_files'].append(file_path)
            
            # 如果有缺失或额外的文件，认为不完整
            # 注意：不检查文件大小和修改时间，以支持重新安装
            if result['missing_files'] or result['extra_files']:
                result['is_complete'] = False
            
        except Exception as e:
            print(f"[失败] 检查文件完整性失败: {str(e)}")
            # 检查失败时，认为文件完整，允许启用（避免误报）
            result['is_complete'] = True
        
        return result
    
    def find_mod_row(self, mod_name):
        """查找mod在表格中的行号"""
        if not hasattr(self, 'mod_table'):
            return -1
        
        for row in range(self.mod_table.rowCount()):
            name_item = self.mod_table.item(row, 1)
            if name_item and name_item.text() == mod_name:
                return row
        return -1
    
    def update_mod_file_structure(self, mod_name, mod_folder_path):
        """更新XML中的文件结构"""
        modinfo_dir = os.path.join(mod_folder_path, "modinfo")
        xml_file_path = os.path.join(modinfo_dir, "modinfo.xml")
        
        if not os.path.exists(xml_file_path):
            return False
        
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            # 删除旧的file_structure
            old_structure = root.find("file_structure")
            if old_structure is not None:
                root.remove(old_structure)
            
            # 创建新的file_structure
            file_structure_elem = ET.SubElement(root, "file_structure")
            file_list = self.get_folder_files(mod_folder_path)
            for file_path in file_list:
                file_elem = ET.SubElement(file_structure_elem, "file")
                file_elem.text = file_path
                # 如果是文件（不是目录），记录文件大小和修改时间
                if not file_path.endswith('/'):
                    # 将统一的分隔符转换为当前系统的分隔符，确保跨平台兼容
                    normalized_path = file_path.replace('/', os.sep).replace('\\', os.sep)
                    full_path = os.path.join(mod_folder_path, normalized_path)
                    if os.path.exists(full_path):
                        file_elem.set("size", str(os.path.getsize(full_path)))
                        file_elem.set("mtime", str(os.path.getmtime(full_path)))
            
            # 保存XML文件
            tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
            print(f"[成功] 已更新模组文件结构: {mod_name}")
            return True
        except Exception as e:
            print(f"[失败] 更新文件结构失败: {str(e)}")
            return False
    
    def show_mod_file_modified_dialog(self, mod_name):
        """显示mod文件被修改的对话框
        
        Returns:
            str: 'cancel', 'save_and_enable', 或 'uninstall'
        """
        # 延迟导入ModFileModifiedPanel，兼容打包环境
        try:
            from models.panels import ModFileModifiedPanel
        except ImportError:
            import importlib.util
            models_dir = os.path.join(self.get_project_root(), 'models')
            panels_path = os.path.join(models_dir, 'panels.py')
            if os.path.exists(panels_path):
                spec = importlib.util.spec_from_file_location("models.panels", panels_path)
                panels_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(panels_module)
                ModFileModifiedPanel = panels_module.ModFileModifiedPanel
            else:
                raise ImportError(f"无法找到 models.panels 模块: {panels_path}")
        
        # 创建弹窗
        panel = ModFileModifiedPanel(self)
        panel.setObjectName("modFileModifiedPanel")
        
        # 设置面板样式
        panel.setStyleSheet("""
            QWidget#modFileModifiedPanel {
                background-color: rgba(255, 182, 193, 120);
                border: 4px solid #8B4513;
                border-radius: 12px;
            }
        """)
        
        # 居中显示
        self.show_panel_with_animation(
            panel, 
            "scale_in", 
            300, 
            position_center=True
        )
        
        # 等待用户选择
        result = panel.exec()
        
        # 隐藏面板
        panel.hide()
        panel.deleteLater()
        
        if result == 1:
            return 'save_and_enable'
        elif result == 2:
            return 'uninstall'
        else:
            return 'cancel'
    
    def convert_symlinks_to_files(self):
        """关闭虚拟映射时，删除所有符号链接并将文件复制到游戏根目录"""
        import shutil
        
        settings = self.load_advanced_settings()
        game_path = settings.get('game_path', '')
        
        if not game_path or not os.path.exists(game_path):
            print(f"[失败] 转换失败: 游戏根目录不存在")
            return
        
        # 获取所有启用的mod
        enabled_mods = self.mod_table.get_enabled_mods()
        
        if not enabled_mods:
            print(f"[提示] 没有启用的mod，无需转换")
            return
        
        project_root = self.get_project_root()
        mods_dir = os.path.join(project_root, "mods")
        
        converted_count = 0
        failed_count = 0
        
        for mod_name in enabled_mods:
            mod_folder_name = mod_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
            mod_folder_path = os.path.join(mods_dir, mod_folder_name)
            
            if not os.path.exists(mod_folder_path):
                continue
            
            # 按照mod文件夹结构遍历，找到对应的符号链接并转换
            for root, dirs, files in os.walk(mod_folder_path):
                # 计算相对路径
                rel_path = os.path.relpath(root, mod_folder_path)
                
                # 跳过modinfo文件夹及其子目录
                if rel_path.startswith('modinfo') or os.path.basename(root) == 'modinfo':
                    if 'modinfo' in dirs:
                        dirs.remove('modinfo')
                    continue
                
                # 确定目标目录
                if rel_path == '.':
                    target_dir = game_path
                else:
                    target_dir = os.path.join(game_path, rel_path)
                
                # 遍历文件
                for file in files:
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(target_dir, file)
                    
                    # 检查目标文件是否存在且是符号链接
                    if os.path.exists(target_file) and os.path.islink(target_file):
                        try:
                            # 删除符号链接
                            os.remove(target_file)
                            
                            # 复制实际文件
                            if os.path.exists(source_file):
                                # 确保目标目录存在
                                os.makedirs(target_dir, exist_ok=True)
                                shutil.copy2(source_file, target_file)
                                converted_count += 1
                        except Exception as e:
                            print(f"[失败] 转换失败: {file} ({str(e)})")
                            failed_count += 1
        
        if converted_count > 0:
            print(f"[成功] 虚拟映射转换完成: 成功转换 {converted_count} 个符号链接为文件")
        if failed_count > 0:
            print(f"[警告] 虚拟映射转换部分失败: {failed_count} 个文件转换失败")
    
    def show_conflict_resolution_dialog(self, conflicts):
        """显示冲突处理界面（占位）"""
        from PySide6.QtWidgets import QMessageBox
        
        # 构建冲突信息（mod之间的冲突）
        conflict_info = []
        conflict_set = set()  # 用于去重
        
        for mod1, mod2, file_path in conflicts:
            conflict_key = (mod1, mod2, file_path)
            if conflict_key not in conflict_set:
                conflict_set.add(conflict_key)
                conflict_info.append(f"{mod1} 与 {mod2} 冲突: {file_path}")
        
        conflict_text = "\n".join(conflict_info[:10])
        if len(conflict_info) > 10:
            conflict_text += f"\n... 还有 {len(conflict_info) - 10} 个冲突"
        
        QMessageBox.warning(
            self, 
            "Mod冲突", 
            f"检测到 {len(conflict_set)} 个mod冲突：\n\n{conflict_text}\n\n冲突处理界面待实现"
        )
    
    def show_tag_management_panel(self):
        """显示标签管理面板"""
        panel = CategoryManagementPanel(self)
        # 在显示前重新加载标签，确保显示最新的标签列表
        panel.load_categories()
        result = panel.exec()
        if result == QDialog.DialogCode.Accepted:
            # 标签已保存，刷新界面
            self.refresh_category_combo()
            self.refresh_mod_list()
    
    def refresh_category_combo(self):
        """刷新分类下拉框"""
        if hasattr(self, 'category_combo') and self.category_combo:
            # 保存当前选中的文本
            current_text = self.category_combo.currentText()
            
            # 清空下拉框
            self.category_combo.clear()
            
            # 重新加载标签
            try:
                categories = self.load_categories()
                if not categories:
                    categories = ["邦邦"]
            except Exception as e:
                categories = ["邦邦"]
            
            # 添加标签到下拉框
            self.category_combo.addItems(categories)
            self.category_combo.addItem("添加新标签...")
            
            # 恢复之前的选择（如果还存在）
            if current_text and current_text in categories:
                self.category_combo.setCurrentText(current_text)
            else:
                self.category_combo.setCurrentIndex(0)
        
        # 刷新导入面板的分类下拉框
        if hasattr(self, 'import_panel') and self.import_panel:
            if hasattr(self.import_panel, 'refresh_categories'):
                self.import_panel.refresh_categories()
    
    def load_categories(self):
        """加载分类标签列表"""
        import json
        project_root = self.get_project_root()
        json_dir = os.path.join(project_root, "json")
        os.makedirs(json_dir, exist_ok=True)
        categories_file = os.path.join(json_dir, "categories.json")
        
        if os.path.exists(categories_file):
            try:
                with open(categories_file, 'r', encoding='utf-8') as f:
                    categories = json.load(f)
                    if not isinstance(categories, list):
                        categories = []
                    return categories
            except Exception as e:
                print(f"[失败] 加载分类标签失败: {e}")
        
        # 默认分类
        default_categories = ["邦邦"]
        # 保存默认分类
        try:
            with open(categories_file, 'w', encoding='utf-8') as f:
                json.dump(default_categories, f, ensure_ascii=False, indent=2)
        except:
            pass
        return default_categories
    
    def save_category(self, category):
        """保存新分类标签"""
        import json
        project_root = self.get_project_root()
        json_dir = os.path.join(project_root, "json")
        os.makedirs(json_dir, exist_ok=True)
        categories_file = os.path.join(json_dir, "categories.json")
        
        categories = self.load_categories()
        if category not in categories:
            categories.append(category)
            try:
                with open(categories_file, 'w', encoding='utf-8') as f:
                    json.dump(categories, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[失败] 保存分类标签失败: {e}")
    
    def load_authors(self):
        """加载作者列表"""
        import json
        project_root = self.get_project_root()
        json_dir = os.path.join(project_root, "json")
        os.makedirs(json_dir, exist_ok=True)
        authors_file = os.path.join(json_dir, "authors.json")
        
        if os.path.exists(authors_file):
            try:
                with open(authors_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[失败] 加载作者列表失败: {e}")
        
        # 默认作者
        default_authors = ["QCanon"]
        # 保存默认作者
        try:
            with open(authors_file, 'w', encoding='utf-8') as f:
                json.dump(default_authors, f, ensure_ascii=False, indent=2)
        except:
            pass
        return default_authors
    
    def save_author(self, author):
        """保存新作者"""
        import json
        project_root = self.get_project_root()
        json_dir = os.path.join(project_root, "json")
        os.makedirs(json_dir, exist_ok=True)
        authors_file = os.path.join(json_dir, "authors.json")
        
        authors = self.load_authors()
        if author not in authors:
            authors.append(author)
            try:
                with open(authors_file, 'w', encoding='utf-8') as f:
                    json.dump(authors, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[失败] 保存作者失败: {e}")
    
    def load_mod_states(self):
        """加载mod状态（启用、收藏、忽略）"""
        import json
        try:
            project_root = self.get_project_root()
            json_dir = os.path.join(project_root, "json")
            os.makedirs(json_dir, exist_ok=True)
            states_file = os.path.join(json_dir, "mod_states.json")
            
            if os.path.exists(states_file):
                try:
                    with open(states_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # 兼容旧格式：如果是简单的 {mod_name: bool}，转换为新格式
                        if data and len(data) > 0:
                            first_value = list(data.values())[0]
                            if isinstance(first_value, bool):
                                new_data = {}
                                for mod_name, enabled in data.items():
                                    new_data[mod_name] = {
                                        "enabled": enabled,
                                        "favorite": False,
                                        "ignored": False
                                    }
                                # 保存新格式
                                try:
                                    with open(states_file, 'w', encoding='utf-8') as f:
                                        json.dump(new_data, f, ensure_ascii=False, indent=2)
                                except:
                                    pass
                                return new_data
                        return data
                except Exception as e:
                    print(f"[失败] 加载mod状态失败: {e}")
                    return {}
        except Exception as e:
            print(f"[失败] 加载mod状态失败: {e}")
            return {}
        
        return {}
    
    def save_mod_states(self):
        """保存mod状态（启用、收藏、忽略）"""
        import json
        project_root = self.get_project_root()
        json_dir = os.path.join(project_root, "json")
        os.makedirs(json_dir, exist_ok=True)
        states_file = os.path.join(json_dir, "mod_states.json")
        
        # 先加载现有状态（保留收藏和忽略状态）
        existing_states = self.load_mod_states()
        
        # 获取所有mod的状态
        mod_states = {}
        for row in range(self.mod_table.rowCount()):
            name_item = self.mod_table.item(row, 1)
            if name_item:
                mod_name = name_item.text()
                # 获取启用状态
                is_enabled = False
                if row in self.mod_table.checkbox_widgets:
                    is_enabled = self.mod_table.checkbox_widgets[row].is_checked()
                
                # 保留或创建收藏和忽略状态，以及导入时间
                existing = existing_states.get(mod_name, {})
                mod_states[mod_name] = {
                    "enabled": is_enabled,
                    "favorite": existing.get("favorite", False) if isinstance(existing, dict) else False,
                    "ignored": existing.get("ignored", False) if isinstance(existing, dict) else False
                }
                # 保留导入时间（如果存在）
                if isinstance(existing, dict) and "import_time" in existing:
                    mod_states[mod_name]["import_time"] = existing["import_time"]
        
        # 也保留不在表格中的mod的状态（可能被忽略了）
        for mod_name, state in existing_states.items():
            if mod_name not in mod_states:
                mod_states[mod_name] = state
        
        try:
            with open(states_file, 'w', encoding='utf-8') as f:
                json.dump(mod_states, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存mod状态失败: {e}")
    
    def is_mod_favorite(self, mod_name):
        """检查mod是否被收藏"""
        mod_states = self.load_mod_states()
        mod_state = mod_states.get(mod_name, {})
        if isinstance(mod_state, bool):
            return False
        return mod_state.get("favorite", False)
    
    def is_mod_ignored(self, mod_name):
        """检查mod是否被忽略"""
        mod_states = self.load_mod_states()
        mod_state = mod_states.get(mod_name, {})
        if isinstance(mod_state, bool):
            return False
        return mod_state.get("ignored", False)
    
    def toggle_mod_favorite(self, mod_name, row):
        """切换收藏状态"""
        mod_states = self.load_mod_states()
        mod_state = mod_states.get(mod_name, {})
        
        # 兼容旧格式
        if isinstance(mod_state, bool):
            mod_state = {"enabled": mod_state, "favorite": False, "ignored": False}
        
        # 切换收藏状态
        current_favorite = mod_state.get("favorite", False)
        mod_state["favorite"] = not current_favorite
        mod_states[mod_name] = mod_state
        
        # 保存状态
        self._save_mod_states_direct(mod_states)
        
        # 更新背景色
        if mod_state["favorite"]:
            self.set_mod_favorite_background(row)
        else:
            self.clear_mod_favorite_background(row)
            # 恢复正常的行颜色
            if hasattr(self.mod_table, 'update_row_color'):
                self.mod_table.update_row_color(row)
        
        # 强制刷新表格视图
        self.mod_table.viewport().update()
        
        print(f"[成功] {'收藏' if mod_state['favorite'] else '取消收藏'}: {mod_name}")
    
    def toggle_mod_ignore(self, mod_name, row):
        """切换忽略状态"""
        mod_states = self.load_mod_states()
        mod_state = mod_states.get(mod_name, {})
        
        # 兼容旧格式
        if isinstance(mod_state, bool):
            mod_state = {"enabled": mod_state, "favorite": False, "ignored": False}
        
        # 切换忽略状态
        current_ignored = mod_state.get("ignored", False)
        mod_state["ignored"] = not current_ignored
        mod_states[mod_name] = mod_state
        
        # 保存状态
        self._save_mod_states_direct(mod_states)
        
        # 如果设置为忽略，隐藏该行；如果取消忽略，显示该行
        # 但需要考虑搜索状态：如果正在搜索，被忽略的mod也应该显示
        search_text = self.search_input.text().strip() if hasattr(self, 'search_input') else ""
        if mod_state["ignored"]:
            if not search_text:  # 只有在非搜索状态下才隐藏
                self.mod_table.hideRow(row)
            print(f"[成功] 已忽略: {mod_name}")
        else:
            self.mod_table.showRow(row)
            print(f"[成功] 取消忽略: {mod_name}")
    
    def set_mod_favorite_background(self, row):
        """设置mod行的背景色为浅黄色"""
        if row < 0 or row >= self.mod_table.rowCount():
            return
        
        # 添加到收藏行集合
        if hasattr(self.mod_table, 'favorite_rows'):
            self.mod_table.favorite_rows.add(row)
        
        # 强制刷新视图
        self.mod_table.viewport().update()
    
    def clear_mod_favorite_background(self, row):
        """清除mod行的收藏背景色"""
        if row < 0 or row >= self.mod_table.rowCount():
            return
        
        # 从收藏行集合中移除
        if hasattr(self.mod_table, 'favorite_rows'):
            self.mod_table.favorite_rows.discard(row)
        
        # 强制刷新视图
        self.mod_table.viewport().update()
    
    def _save_mod_states_direct(self, mod_states):
        """直接保存mod状态（不重新读取表格）"""
        import json
        project_root = self.get_project_root()
        json_dir = os.path.join(project_root, "json")
        os.makedirs(json_dir, exist_ok=True)
        states_file = os.path.join(json_dir, "mod_states.json")
        
        try:
            with open(states_file, 'w', encoding='utf-8') as f:
                json.dump(mod_states, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[失败] 保存mod状态失败: {e}")
    
    def log_mod_usage(self, mod_name, enabled):
        """记录mod使用日志到ini文件（启用/禁用事件）"""
        try:
            import configparser
            from datetime import datetime
            import time
            
            project_root = self.get_project_root()
            log_file = os.path.join(project_root, "usage_log.ini")
            
            # 创建ConfigParser对象
            config = configparser.ConfigParser()
            
            # 如果日志文件存在，读取现有内容
            if os.path.exists(log_file):
                try:
                    config.read(log_file, encoding='utf-8')
                except Exception as e:
                    # 读取日志文件失败，不打印详细信息
                    config = configparser.ConfigParser()  # 重新创建
            
            # 创建新的日志条目，使用微秒确保唯一性
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            # 使用微秒和当前时间戳确保唯一性
            unique_id = f"{now.strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000000) % 1000000}"
            section_name = f"Usage_{unique_id}"
            
            # 检查section是否已存在（理论上不应该，但为了安全）
            retry_count = 0
            while section_name in config.sections() and retry_count < 10:
                unique_id = f"{now.strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000000) % 1000000}_{retry_count}"
                section_name = f"Usage_{unique_id}"
                retry_count += 1
            
            config.add_section(section_name)
            config.set(section_name, 'timestamp', timestamp)
            config.set(section_name, 'mod_name', mod_name)
            config.set(section_name, 'action', 'enabled' if enabled else 'disabled')
            
            # 写入日志文件
            try:
                with open(log_file, 'w', encoding='utf-8') as f:
                    config.write(f)
            except Exception as e:
                pass  # 写入日志文件失败，不打印详细信息
                return
            
            # 同时保存状态到mod_states.json
            try:
                self.save_mod_states()
            except Exception as e:
                print(f"[失败] 保存mod状态失败")
            
            # 已记录使用日志，不打印详细信息
        except Exception as e:
            print(f"[失败] 记录使用日志失败")
            import traceback
            traceback.print_exc()
    
    def create_status_bar(self):
        """创建底部状态栏 - 渐变背景"""
        status_bar = QStatusBar()
        # 不显示任何消息，保持空白
        # status_bar.showMessage("就绪")  # 注释掉这行
        # 设置状态栏样式
        status_bar.setStyleSheet(f"""
            QStatusBar {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 200), stop:1 {COLOR_BG_LIGHT});
                border-top: 1px solid rgba(0, 0, 0, 15);
                color: {COLOR_TEXT_DARK};
                font-size: 12px;
            }}
        """)
        return status_bar

    def export_selected_mods(self):
        """导出选中的mod到指定目录"""
        # 获取选中的mod名称
        selected_mods = self.mod_table.get_selected_mod_names()
        
        if not selected_mods:
            QMessageBox.information(self, "提示", "请先选择要导出的mod")
            return
        
        # 显示导出选择面板
        panel = ExportSelectionPanel(self)
        # 使用动画显示面板
        self.show_panel_with_animation(panel, "scale_in", 300, position_center=True)
        result = panel.exec()
        
        if result == 0:  # 取消
            return
        elif result == 1:  # 导出为mod
            self.export_as_single_mod(selected_mods)
        elif result == 2:  # 导出为mods
            self.export_as_multiple_mods(selected_mods)
    
    def export_as_single_mod(self, selected_mods):
        """导出为单个mod（合并）"""
        # 检查冲突
        conflicts = self.check_mod_conflicts(selected_mods)
        if conflicts:
            conflict_text = "选中的mod之间存在文件冲突，无法合并：\n\n"
            for mod1, mod2, file_path in conflicts[:10]:  # 最多显示10个冲突
                conflict_text += f"  • {mod1} 与 {mod2} 冲突: {file_path}\n"
            if len(conflicts) > 10:
                conflict_text += f"\n... 还有 {len(conflicts) - 10} 个冲突"
            QMessageBox.warning(self, "冲突检测", conflict_text)
            return
        
        # 没有冲突，合并mod并进入编辑界面
        # 生成默认名称：用"+"连接
        default_name = " + ".join(selected_mods)
        
        # 合并mod到临时目录
        import shutil
        import tempfile
        project_root = self.get_project_root()
        mods_dir = os.path.join(project_root, "mods")
        
        # 创建临时合并目录
        temp_dir = tempfile.mkdtemp(prefix="mod_merge_")
        
        try:
            # 合并所有mod的文件
            for mod_name in selected_mods:
                mod_folder_name = mod_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
                source_path = os.path.join(mods_dir, mod_folder_name)
                
                if not os.path.exists(source_path):
                    continue
                
                # 复制mod的所有文件（排除modinfo）
                for root, dirs, files in os.walk(source_path):
                    # 跳过modinfo文件夹
                    if 'modinfo' in dirs:
                        dirs.remove('modinfo')
                    rel_path = os.path.relpath(root, source_path)
                    if rel_path.startswith('modinfo') or os.path.basename(root) == 'modinfo':
                        continue
                    
                    # 创建目标目录
                    if rel_path == '.':
                        target_dir = temp_dir
                    else:
                        target_dir = os.path.join(temp_dir, rel_path)
                    os.makedirs(target_dir, exist_ok=True)
                    
                    # 复制文件
                    for file in files:
                        source_file = os.path.join(root, file)
                        target_file = os.path.join(target_dir, file)
                        shutil.copy2(source_file, target_file)
            
            # 进入编辑界面（导出模式）
            self.edit_merged_mod_for_export(default_name, temp_dir, selected_mods)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"合并mod失败：{str(e)}")
            # 清理临时目录
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
    def export_as_multiple_mods(self, selected_mods):
        """导出为多个mod（原有逻辑）"""
        # 打开文件夹选择对话框
        export_dir = QFileDialog.getExistingDirectory(
            self,
            "选择导出目录",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not export_dir:
            return
        
        # 创建mods子文件夹
        mods_export_dir = os.path.join(export_dir, "mods")
        try:
            os.makedirs(mods_export_dir, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法创建导出目录：{str(e)}")
            return
        
        # 获取项目根目录和mods目录
        project_root = self.get_project_root()
        mods_dir = os.path.join(project_root, "mods")
        
        if not os.path.exists(mods_dir):
            QMessageBox.warning(self, "警告", "mods目录不存在")
            return
        
        # 复制选中的mod
        import shutil
        success_count = 0
        failed_mods = []
        
        for mod_name in selected_mods:
            # 将mod名称转换为文件夹名
            mod_folder_name = mod_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
            source_path = os.path.join(mods_dir, mod_folder_name)
            target_path = os.path.join(mods_export_dir, mod_folder_name)
            
            if not os.path.exists(source_path):
                failed_mods.append(f"{mod_name} (源文件夹不存在)")
                continue
            
            try:
                # 如果目标文件夹已存在，先删除
                if os.path.exists(target_path):
                    shutil.rmtree(target_path)
                
                # 复制整个mod文件夹
                shutil.copytree(source_path, target_path)
                success_count += 1
            except Exception as e:
                failed_mods.append(f"{mod_name} ({str(e)})")
        
        # 只在失败时显示结果
        if failed_mods:
            message = f"导出完成，但有以下mod失败：\n\n" + "\n".join(failed_mods)
            QMessageBox.warning(self, "导出部分失败", message)
    
    def edit_merged_mod_for_export(self, default_name, temp_dir, source_mods):
        """编辑合并的mod用于导出"""
        # 标记为导出模式
        self._export_mode = True
        self._export_temp_dir = temp_dir
        self._export_source_mods = source_mods
        
        # 复用导入面板的界面
        self.show_import_panel()
        
        if hasattr(self, 'import_panel') and self.import_panel:
            # 找到标题标签并修改
            title_label = self.import_panel.findChild(QLabel)
            if title_label:
                title_label.setText("导出合并mod")
            
            # 填充默认名称
            self.mod_name_input.setText(default_name)
            
            # 加载合并后的文件树
            self.load_merged_mod_file_tree(temp_dir)
            
            # 修改保存按钮为导出按钮
            save_btn = None
            for widget in self.import_panel.findChildren(QPushButton):
                if widget.text() == "保存":
                    save_btn = widget
                    break
            
            if save_btn:
                save_btn.clicked.disconnect()
                save_btn.setText("导出")
                save_btn.clicked.connect(self.export_merged_mod)
    
    def load_merged_mod_file_tree(self, temp_dir):
        """加载合并mod的文件树"""
        # 复用load_mod_file_tree的逻辑，但使用临时目录
        if hasattr(self, 'file_tree') and self.file_tree:
            self.file_tree.clear()
            
            # 获取文件列表
            file_list = self.get_folder_files(temp_dir)
            self.display_file_tree(file_list)
    
    def export_merged_mod(self):
        """导出合并的mod"""
        if not hasattr(self, '_export_mode') or not self._export_mode:
            return
        
        # 获取表单数据
        mod_name = self.mod_name_input.text().strip() or "未命名模组"
        category = self.category_input.text().strip()
        author = self.author_combo.currentText().strip() or "未知"
        description = self.description_input.text().strip()
        
        # 打开文件夹选择对话框
        export_dir = QFileDialog.getExistingDirectory(
            self,
            "选择导出目录",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not export_dir:
            return
        
        # 创建mods子文件夹
        mods_export_dir = os.path.join(export_dir, "mods")
        try:
            os.makedirs(mods_export_dir, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法创建导出目录：{str(e)}")
            return
        
        # 将临时目录复制到导出目录
        import shutil
        mod_folder_name = mod_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        target_path = os.path.join(mods_export_dir, mod_folder_name)
        
        try:
            # 如果目标文件夹已存在，先删除
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            
            # 复制整个合并的mod文件夹
            shutil.copytree(self._export_temp_dir, target_path)
            
            # 创建modinfo文件夹和XML文件
            modinfo_dir = os.path.join(target_path, "modinfo")
            os.makedirs(modinfo_dir, exist_ok=True)
            
            import xml.etree.ElementTree as ET
            xml_root = ET.Element("mod")
            name_elem = ET.SubElement(xml_root, "name")
            name_elem.text = mod_name
            if category:
                category_elem = ET.SubElement(xml_root, "category")
                category_elem.text = category
            if author:
                author_elem = ET.SubElement(xml_root, "author")
                author_elem.text = author
            if description:
                desc_elem = ET.SubElement(xml_root, "description")
                desc_elem.text = description
            
            # 添加文件结构记录
            file_structure_elem = ET.SubElement(xml_root, "file_structure")
            file_list = self.get_folder_files(target_path)
            for file_path in file_list:
                file_elem = ET.SubElement(file_structure_elem, "file")
                file_elem.text = file_path
                # 如果是文件（不是目录），记录文件大小和修改时间
                if not file_path.endswith('/'):
                    # 将统一的分隔符转换为当前系统的分隔符，确保跨平台兼容
                    normalized_path = file_path.replace('/', os.sep).replace('\\', os.sep)
                    full_path = os.path.join(target_path, normalized_path)
                    if os.path.exists(full_path):
                        file_elem.set("size", str(os.path.getsize(full_path)))
                        file_elem.set("mtime", str(os.path.getmtime(full_path)))
            
            xml_file = os.path.join(modinfo_dir, "modinfo.xml")
            tree = ET.ElementTree(xml_root)
            tree.write(xml_file, encoding='utf-8', xml_declaration=True)
            
            QMessageBox.information(self, "成功", f"合并mod已导出到：{target_path}")
            
            # 清理临时目录
            try:
                shutil.rmtree(self._export_temp_dir)
            except:
                pass
            
            # 关闭导入面板
            self.hide_import_panel()
            
            # 清除导出模式标记
            self._export_mode = False
            self._export_temp_dir = None
            self._export_source_mods = None
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败：{str(e)}")
    
    def uninstall_mod_permanently(self, mod_name, row):
        """永久卸载mod（删除文件夹和表格行）"""
        import shutil
        
        # 获取项目根目录和mods目录
        project_root = self.get_project_root()
        mods_dir = os.path.join(project_root, "mods")
        
        # 将mod名称转换为文件夹名
        mod_folder_name = mod_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        mod_folder_path = os.path.join(mods_dir, mod_folder_name)
        
        # 删除mod文件夹
        if os.path.exists(mod_folder_path):
            try:
                shutil.rmtree(mod_folder_path)
                print(f"[成功] 卸载mod: {mod_name}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法删除mod文件夹：{str(e)}")
                return
        
        # 从mod_states.json中删除
        import json
        from collections import OrderedDict
        
        json_dir = os.path.join(project_root, "json")
        os.makedirs(json_dir, exist_ok=True)
        mod_states_file = os.path.join(json_dir, "mod_states.json")
        if os.path.exists(mod_states_file):
            try:
                with open(mod_states_file, 'r', encoding='utf-8') as f:
                    mod_states = json.load(f, object_pairs_hook=OrderedDict)
                
                if mod_name in mod_states:
                    del mod_states[mod_name]
                
                with open(mod_states_file, 'w', encoding='utf-8') as f:
                    json.dump(mod_states, f, ensure_ascii=False, indent=2)
                # 已从mod_states.json中删除，不打印详细信息
            except Exception as e:
                print(f"[警告] 更新mod_states.json失败")
        
        # 从表格中删除行
        self.mod_table.removeRow(row)
        
        # 更新统计
        self.update_statistics()
    
    def get_mod_file_paths(self, mod_name, mod_folder_path):
        """获取mod的所有文件路径（相对于游戏目录）
        
        Args:
            mod_name: mod名称
            mod_folder_path: mod文件夹路径
            
        Returns:
            set: 文件路径集合（相对于游戏目录）
        """
        file_paths = set()
        
        # 跳过modinfo文件夹
        for root, dirs, files in os.walk(mod_folder_path):
            # 跳过modinfo文件夹
            if 'modinfo' in root:
                continue
            
            rel_path = os.path.relpath(root, mod_folder_path)
            if rel_path.startswith('modinfo'):
                continue
            
            for file in files:
                if rel_path == '.':
                    file_path = file.replace('\\', '/')
                else:
                    file_path = os.path.join(rel_path, file).replace('\\', '/')
                file_paths.add(file_path)
        
        return file_paths
    
    def check_single_mod_conflicts(self, mod_name, mod_folder_path):
        """检测mod与已启用mod的文件冲突
        
        Args:
            mod_name: 要启用的mod名称
            mod_folder_path: mod文件夹路径
            
        Returns:
            dict: {
                'has_conflict': bool,
                'conflicting_mods': list of str, 发生冲突的mod列表
            }
        """
        # 获取当前mod的文件路径
        current_mod_files = self.get_mod_file_paths(mod_name, mod_folder_path)
        
        if not current_mod_files:
            return {'has_conflict': False, 'conflicting_mods': []}
        
        # 获取所有已启用的mod
        enabled_mods = self.mod_table.get_enabled_mods()
        conflicting_mods = []
        
        # 获取mods目录
        project_root = self.get_project_root()
        mods_dir = os.path.join(project_root, "mods")
        
        # 检查每个已启用的mod
        for enabled_mod_name in enabled_mods:
            if enabled_mod_name == mod_name:
                continue  # 跳过自己
            
            # 获取已启用mod的文件路径
            enabled_mod_folder_name = enabled_mod_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
            enabled_mod_folder_path = os.path.join(mods_dir, enabled_mod_folder_name)
            
            if not os.path.exists(enabled_mod_folder_path):
                continue
            
            enabled_mod_files = self.get_mod_file_paths(enabled_mod_name, enabled_mod_folder_path)
            
            # 检查是否有文件路径冲突
            if current_mod_files & enabled_mod_files:  # 集合交集
                conflicting_mods.append(enabled_mod_name)
        
        return {
            'has_conflict': len(conflicting_mods) > 0,
            'conflicting_mods': conflicting_mods
        }
    
    def check_and_resolve_conflicts(self, mod_name, mod_folder_path):
        """检查并处理冲突
        
        Args:
            mod_name: 要启用的mod名称
            mod_folder_path: mod文件夹路径
            
        Returns:
            str: 'cancel'=取消启用, 'override'=直接覆盖, 'manual'=手动修改
        """
        # 检测冲突
        conflict_check = self.check_single_mod_conflicts(mod_name, mod_folder_path)
        
        if not conflict_check['has_conflict']:
            return 'override'  # 无冲突，直接启用
        
        conflicting_mods = conflict_check['conflicting_mods']
        
        # 显示冲突处理面板
        panel = ConflictResolutionPanel(mod_name, conflicting_mods, self)
        result = panel.exec()
        
        if result == 0:  # 取消启用
            return 'cancel'
        elif result == 1:  # 直接覆盖
            return 'override'
        elif result == 2:  # 手动修改
            # 只在虚拟映射开启时显示手动修改界面
            settings = self.load_advanced_settings()
            use_virtual_mapping = settings.get('virtual_mapping', False)
            
            if not use_virtual_mapping:
                # 虚拟映射未开启，提示用户
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    "提示",
                    "手动修改优先级功能仅在虚拟映射模式下可用。\n\n请先启用虚拟映射功能。"
                )
                return 'cancel'
            
            # 显示优先级调整面板
            # 加载已保存的优先级（如果有），延续之前的优先级设置
            priority_order = self.load_mod_priority(mod_name, conflicting_mods)
            
            if priority_order:
                # 使用已保存的优先级顺序（新mod已经在最前面）
                all_conflicting_mods = priority_order
            else:
                # 如果没有保存的优先级，新mod默认放在最前面
                all_conflicting_mods = [mod_name] + conflicting_mods
            
            priority_panel = PriorityAdjustmentPanel(all_conflicting_mods, self)
            priority_result, final_order = priority_panel.exec()
            
            if priority_result == 1 and final_order:
                # 保存优先级顺序
                self.save_mod_priority(mod_name, final_order)
                return 'manual'
            else:
                return 'cancel'
        
        return 'cancel'
    
    def load_mod_priority(self, mod_name, conflicting_mods):
        """加载mod优先级顺序，延续之前的优先级设置
        
        Args:
            mod_name: 当前要启用的mod名称（新启用的mod，应该放在最前面）
            conflicting_mods: 冲突mod列表（包括之前已启用的mod）
            
        Returns:
            list or None: 优先级顺序列表，如果没有保存则返回None
        """
        import json
        try:
            project_root = self.get_project_root()
            json_dir = os.path.join(project_root, "json")
            priority_file = os.path.join(json_dir, "mod_priorities.json")
            
            if not os.path.exists(priority_file):
                return None
            
            with open(priority_file, 'r', encoding='utf-8') as f:
                priorities = json.load(f)
            
            # 首先查找完全匹配的优先级配置
            all_mods = [mod_name] + conflicting_mods
            all_mods_set = set(all_mods)
            for key, value in priorities.items():
                if set(value) == all_mods_set:
                    return value
            
            # 如果没有完全匹配，尝试从已保存的优先级中提取部分mod的相对顺序
            # 新mod（mod_name）应该放在最前面，其他mod保持它们之间的相对顺序
            
            current_mods_set = set(conflicting_mods)  # 不包括新mod
            
            # 找到包含最多当前冲突mod的优先级配置（最相关的配置）
            best_match = None
            best_match_count = 0
            best_match_order = None
            
            for key, value in priorities.items():
                saved_mods_set = set(value)
                common_mods = saved_mods_set & current_mods_set
                
                # 如果这个配置包含至少两个当前冲突的mod，且包含数量最多
                if len(common_mods) >= 2 and len(common_mods) > best_match_count:
                    best_match_count = len(common_mods)
                    best_match_order = value
            
            # 如果找到了最相关的配置，使用它来构建新的顺序
            if best_match_order:
                ordered_mods = []
                used_mods = set()
                
                # 按照已保存的顺序添加mod（保持相对顺序）
                for mod in best_match_order:
                    if mod in conflicting_mods and mod not in used_mods:
                        ordered_mods.append(mod)
                        used_mods.add(mod)
                
                # 添加没有优先级信息的mod
                for mod in conflicting_mods:
                    if mod not in used_mods:
                        ordered_mods.append(mod)
                
                # 新mod放在最前面
                return [mod_name] + ordered_mods
            
        except Exception as e:
            print(f"[警告] 加载优先级失败: {e}")
        
        return None
    
    def save_mod_priority(self, mod_name, priority_order):
        """保存mod优先级顺序
        
        Args:
            mod_name: 当前要启用的mod名称
            priority_order: 优先级顺序列表
        """
        import json
        try:
            project_root = self.get_project_root()
            json_dir = os.path.join(project_root, "json")
            os.makedirs(json_dir, exist_ok=True)
            priority_file = os.path.join(json_dir, "mod_priorities.json")
            
            # 加载现有优先级
            priorities = {}
            if os.path.exists(priority_file):
                with open(priority_file, 'r', encoding='utf-8') as f:
                    priorities = json.load(f)
            
            # 使用冲突mod集合作为key（排序后转为字符串）
            key = ','.join(sorted(priority_order))
            priorities[key] = priority_order
            
            # 保存
            with open(priority_file, 'w', encoding='utf-8') as f:
                json.dump(priorities, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[警告] 保存优先级失败: {e}")



