from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMenu, QDialog
)
from PySide6.QtCore import Qt, QDate, QModelIndex, Signal, QItemSelectionModel
from PySide6.QtGui import QColor, QPainter
import sys
import os
# 添加项目根目录到Python路径，以便导入config模块
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from config import ROW_HEIGHT, COLOR_TEXT_DARK, COLOR_BG_GRAY, COLOR_PRIMARY, COLOR_TEXT_LIGHT

# 延迟导入，在需要时才导入，避免打包环境下的导入问题
def _import_checkbox():
    """导入ModCheckBox类"""
    try:
        from .checkbox import ModCheckBox
        return ModCheckBox
    except ImportError:
        try:
            from models.checkbox import ModCheckBox
            return ModCheckBox
        except ImportError:
            # 最后尝试：直接导入文件
            import importlib.util
            checkbox_path = os.path.join(os.path.dirname(__file__), 'checkbox.py')
            if os.path.exists(checkbox_path):
                spec = importlib.util.spec_from_file_location("models.checkbox", checkbox_path)
                checkbox_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(checkbox_module)
                return checkbox_module.ModCheckBox
            raise

def _import_panels():
    """导入panels模块中的类"""
    try:
        from .panels import BinaryDisablePanel, BinarySelectionPanel
        return BinaryDisablePanel, BinarySelectionPanel
    except ImportError:
        try:
            from models.panels import BinaryDisablePanel, BinarySelectionPanel
            return BinaryDisablePanel, BinarySelectionPanel
        except ImportError:
            # 最后尝试：直接导入文件
            import importlib.util
            panels_path = os.path.join(os.path.dirname(__file__), 'panels.py')
            if os.path.exists(panels_path):
                spec = importlib.util.spec_from_file_location("models.panels", panels_path)
                panels_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(panels_module)
                return panels_module.BinaryDisablePanel, panels_module.BinarySelectionPanel
            raise

class CustomModTable(QTableWidget):
    """自定义Mod表格类"""
    # 定义信号：当统计数据需要更新时发出
    statistics_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hovered_row = -1  # 当前悬停的行
        self.checkbox_widgets = {}  # 存储复选框控件的引用 {row: ModCheckBox}
        self.saved_enabled_mods = []  # 保存的启用Mod配置（用于二分禁用恢复）
        self.green_rows = set()  # 应该显示绿色的行（完全独立于Qt的selection机制）
        self.favorite_rows = set()  # 应该显示黄色的行（收藏的行）
        self.init_table()
        self.setup_columns()
        self.apply_styles()
        # 启用鼠标跟踪以实现悬停效果
        self.setMouseTracking(True)
        # 延迟连接selectionModel，避免在窗口显示前出现问题
        # 使用QTimer延迟连接，确保selectionModel已初始化
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self._connect_selection_model)
    
    def _connect_selection_model(self):
        """延迟连接selectionModel信号"""
        try:
            selection_model = self.selectionModel()
            if selection_model:
                selection_model.selectionChanged.connect(self.on_selection_changed)
        except Exception as e:
            # 如果连接失败，忽略错误（可能在窗口显示后重试）
            pass
    
    def init_table(self):
        """初始化表格基本设置"""
        # 设置列数
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["启用", "Mod名称", "分类", "作者", "添加日期"])
        
        # 表格基本属性
        self.setAlternatingRowColors(True)        # 启用交替行颜色
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # 启用整行选择
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)  # 扩展选择模式 - 支持Ctrl多选和Shift范围选择
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
        # 注意：selectionModel()的连接延迟到窗口显示后，避免在初始化时出现问题
        # 连接右键菜单事件
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)  # 启用右键菜单
        self.setSortingEnabled(False)  # 禁用排序
        
        # 设置行高（增加到38px）
        vertical_header = self.verticalHeader()
        vertical_header.setDefaultSectionSize(ROW_HEIGHT)
        # 禁用垂直表头的点击（行号不接受点击）
        vertical_header.setSectionsClickable(False)
        
        # 设置表头
        header = self.horizontalHeader()
        header.setDefaultSectionSize(100)
        # 设置列宽
        self.setColumnWidth(0, 50)  # 启用列更窄
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 启用列固定宽度
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Mod名称列自动扩展
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # 分类列固定宽度
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # 作者列固定宽度
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # 添加日期列固定宽度
        header.setStretchLastSection(False)  # 不自动拉伸最后一列
        
        # 设置具体的列宽
        self.setColumnWidth(2, 180)   # 分类列：180px（增加二分之一，120 * 1.5 = 180）
        self.setColumnWidth(3, 93)    # 作者列：93px（减少二分之一，140 * 0.67 ≈ 93）
        self.setColumnWidth(4, 120)   # 添加日期列：120px（和分类一样长）
        
        # 隐藏垂直表头（可选）
        self.verticalHeader().setVisible(True)
    
    def setup_columns(self):
        """设置各列的显示和编辑属性"""
        # 设置列对齐方式（通过设置代理或在添加数据时设置）
        # 这里我们会在添加数据的方法中设置对齐方式
        
        # 第0列：启用 - 使用QCheckBox（在添加行时动态创建）
        # 第1列：Mod名称 - 左对齐，可编辑（默认）
        # 第2列：分类 - 居中对齐，带下拉框（在添加行时动态创建）
        # 第3列：作者 - 居中对齐
        # 第4列：添加日期 - 居中对齐，格式"YYYY-MM-DD"
        pass
    
    def insertRow(self, row):
        """重写insertRow方法，在插入行后触发统计更新"""
        super().insertRow(row)
        # 更新复选框行号
        new_checkbox_widgets = {}
        for old_row, checkbox in self.checkbox_widgets.items():
            if old_row >= row:
                checkbox.row = old_row + 1
                new_checkbox_widgets[old_row + 1] = checkbox
            else:
                new_checkbox_widgets[old_row] = checkbox
        self.checkbox_widgets = new_checkbox_widgets
        self.statistics_changed.emit()
    
    def removeRow(self, row):
        """重写removeRow方法，在删除行后触发统计更新"""
        # 删除复选框引用
        if row in self.checkbox_widgets:
            del self.checkbox_widgets[row]
        # 更新复选框行号
        new_checkbox_widgets = {}
        for old_row, checkbox in self.checkbox_widgets.items():
            if old_row > row:
                checkbox.row = old_row - 1
                new_checkbox_widgets[old_row - 1] = checkbox
            else:
                new_checkbox_widgets[old_row] = checkbox
        self.checkbox_widgets = new_checkbox_widgets
        
        super().removeRow(row)
        self.statistics_changed.emit()
    
    def add_mod_row(self, mod_name, category="未分类", author="未知", add_date=None, enabled=True):
        """添加一行Mod数据"""
        row = self.rowCount()
        self.insertRow(row)
        
        # 第0列：启用 - 添加自定义复选框
        ModCheckBox = _import_checkbox()
        checkbox_widget = ModCheckBox(row)
        checkbox_widget.set_checked(enabled)  # 设置初始状态
        checkbox_widget.state_changed.connect(self.on_checkbox_state_changed)
        self.checkbox_widgets[row] = checkbox_widget
        self.setCellWidget(row, 0, checkbox_widget)
        
        # 第1列：Mod名称
        name_item = QTableWidgetItem(mod_name)
        name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        # 设置字体加粗
        from PySide6.QtGui import QFont
        font = name_item.font()
        font.setBold(True)
        name_item.setFont(font)
        self.setItem(row, 1, name_item)

        
        # 第2列：分类
        category_item = QTableWidgetItem(category)
        category_item.setTextAlignment(Qt.AlignCenter)
        category_item.setFlags(category_item.flags() & ~Qt.ItemIsEditable)
        # 设置字体加粗
        from PySide6.QtGui import QFont
        font = category_item.font()
        font.setBold(True)
        category_item.setFont(font)
        self.setItem(row, 2, category_item)
        
        # 第3列：作者
        author_item = QTableWidgetItem(author)
        author_item.setTextAlignment(Qt.AlignCenter)
        author_item.setFlags(author_item.flags() & ~Qt.ItemIsEditable)
        # 设置字体加粗
        font = author_item.font()
        font.setBold(True)
        author_item.setFont(font)
        self.setItem(row, 3, author_item)
        
        # 第4列：添加日期
        from PySide6.QtCore import QDate
        if add_date is None:
            add_date = QDate.currentDate().toString("yyyy-MM-dd")
        date_item = QTableWidgetItem(add_date)
        date_item.setTextAlignment(Qt.AlignCenter)
        date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
        # 设置字体加粗
        font = date_item.font()
        font.setBold(True)
        date_item.setFont(font)
        self.setItem(row, 4, date_item)
        
        self.statistics_changed.emit()
        return row
    
    def apply_styles(self):
        """应用QSS样式"""
        style_sheet = f"""
            /* 表头样式：浅粉色背景 */
            QHeaderView::section {{
                background-color: rgba(255, 192, 203, 180);
                color: {COLOR_TEXT_DARK};
                padding: 8px;
                border: none;
                border-bottom: 2px solid rgba(0, 0, 0, 30);
                font-weight: bold;
                font-size: 13px;
            }}
            
            /* 第一列表头样式：浅粉色背景 */
            QHeaderView::section:first {{
                background-color: rgba(255, 192, 203, 180);
            }}
            
            /* 表格整体样式：半透明背景，圆角边框 */
            QTableWidget {{
                gridline-color: rgba(200, 200, 200, 150);  /* 保持网格线可见 */
                background-color: rgba(255, 255, 255, 120);
                alternate-background-color: rgba(245, 245, 245, 100);
                border: 2px solid rgba(200, 200, 200, 200);
                border-radius: 8px;
                selection-background-color: transparent;  /* 完全禁用Qt的选中背景色 */
                selection-color: black;
                outline: none;  /* 去掉选中框 */
            }}
            
            /* 行样式 - 禁止单元格单独选中 */
            QTableWidget::item {{
                border: 0.5px solid rgba(200, 200, 200, 100);  /* 保持分隔线 */
                padding: 4px;
                background-color: transparent;
                outline: none;  /* 去掉选中框 */
            }}
            
            /* 完全禁用Qt的选中行样式 */
            QTableWidget::item:selected {{
                background-color: transparent;
                color: black;
                border: 0.5px solid rgba(200, 200, 200, 100);
                outline: none;
            }}
            
            /* 禁用任何单元格级别的选中效果 */
            QTableWidget::item:focus {{
                background-color: transparent;
                outline: none;
                border: 0.5px solid rgba(200, 200, 200, 100);
            }}
            
            /* 悬浮效果完全透明 */
            QTableWidget::item:hover {{
                background-color: transparent;
            }}
            
            /* 悬浮时选中也透明（我们用自己的绿色绘制） */
            QTableWidget::item:hover:selected {{
                background-color: transparent;
            }}
            
            /* 复选框样式 - 完全删除 */
            
            /* 滚动条样式：半透明美化 */
            QScrollBar:vertical {{
                border: none;
                background: rgba(240, 240, 240, 100);
                width: 14px;
                margin: 0;
                border-radius: 7px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(180, 180, 180, 150);
                min-height: 30px;
                border-radius: 7px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(150, 150, 150, 180);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background: rgba(240, 240, 240, 100);
                height: 14px;
                margin: 0;
                border-radius: 7px;
            }}
            QScrollBar::handle:horizontal {{
                background: rgba(180, 180, 180, 150);
                min-width: 30px;
                border-radius: 7px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: rgba(150, 150, 150, 180);
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
            }}
            
            /* 下拉框样式统一 */
            QComboBox {{
                background-color: white;
                border: 1px solid {COLOR_BG_GRAY};
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 80px;
            }}
            QComboBox:hover {{
                border: 1px solid {COLOR_PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {COLOR_TEXT_DARK};
                width: 0;
                height: 0;
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                border: 1px solid {COLOR_BG_GRAY};
                selection-background-color: {COLOR_PRIMARY};
                selection-color: {COLOR_TEXT_LIGHT};
                border-radius: 4px;
            }}
        """
        self.setStyleSheet(style_sheet)
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，实现悬停行效果"""
        super().mouseMoveEvent(event)
        item = self.itemAt(event.position().toPoint())
        if item:
            current_row = item.row()
            if current_row != self.hovered_row:
                # 更新之前的悬停行
                if self.hovered_row >= 0:
                    self.update_row_color(self.hovered_row)
                # 设置新的悬停行
                self.hovered_row = current_row
                self.update_row_color(self.hovered_row)
        else:
            # 鼠标不在任何行上
            if self.hovered_row >= 0:
                self.update_row_color(self.hovered_row)
                self.hovered_row = -1
        
        # 确保所有选中行的绿色被保持（防止鼠标移动时绿色消失）
        self._ensure_selected_rows_green()
    
    def leaveEvent(self, event):
        """鼠标离开表格时清除悬停效果，但保持选中行的绿色"""
        if self.hovered_row >= 0:
            self.update_row_color(self.hovered_row)
            self.hovered_row = -1
        
        # 确保所有选中行的绿色被保持
        self._ensure_selected_rows_green()
        
        super().leaveEvent(event)
    
    def paintEvent(self, event):
        """重写绘制事件，直接绘制绿色背景和黄色收藏背景（完全独立于Qt的selection机制）"""
        super().paintEvent(event)
        
        painter = QPainter(self.viewport())
        painter.setPen(Qt.PenStyle.NoPen)
        
        # 先绘制收藏行的黄色背景
        if self.favorite_rows:
            favorite_color = QColor(255, 255, 200, 150)  # 浅黄色，半透明
            painter.setBrush(favorite_color)
            
            for row in self.favorite_rows:
                if row >= 0 and row < self.rowCount():
                    # 计算整行的矩形区域：从第一列到最后一列
                    y_pos = self.rowViewportPosition(row)
                    row_height = self.rowHeight(row) if self.rowHeight(row) > 0 else ROW_HEIGHT
                    
                    # 计算第一列和最后一列的x坐标
                    x_start = self.columnViewportPosition(0)
                    x_end = self.columnViewportPosition(self.columnCount() - 1) + self.columnWidth(self.columnCount() - 1)
                    
                    # 创建整行的矩形
                    from PySide6.QtCore import QRect
                    row_rect = QRect(x_start, y_pos, x_end - x_start, row_height)
                    
                    # 绘制整行的黄色背景
                    painter.drawRect(row_rect)
        
        # 再绘制选中行的绿色背景（覆盖在黄色上面）
        if self.green_rows:
            green_color = QColor(144, 238, 144, 150)
            painter.setBrush(green_color)
            
            for row in self.green_rows:
                if row >= 0 and row < self.rowCount():
                    # 计算整行的矩形区域：从第一列到最后一列
                    y_pos = self.rowViewportPosition(row)
                    row_height = self.rowHeight(row) if self.rowHeight(row) > 0 else ROW_HEIGHT
                    
                    # 计算第一列和最后一列的x坐标
                    x_start = self.columnViewportPosition(0)
                    x_end = self.columnViewportPosition(self.columnCount() - 1) + self.columnWidth(self.columnCount() - 1)
                    
                    # 创建整行的矩形
                    from PySide6.QtCore import QRect
                    row_rect = QRect(x_start, y_pos, x_end - x_start, row_height)
                    
                    # 绘制整行的绿色背景
                    painter.drawRect(row_rect)
                    
                    # 同时设置所有单元格的背景色（双重保险）
                    # 注意：复选框列（col=0）不设置widget背景色，只让paintEvent绘制，避免不自然的绿色
                    for col in range(self.columnCount()):
                        item = self.item(row, col)
                        if item:
                            item.setBackground(green_color)
                        else:
                            # 对于复选框列，不设置widget背景色，避免不自然的绿色
                            if col != 0:
                                widget = self.cellWidget(row, col)
                                if widget:
                                    from PySide6.QtGui import QPalette
                                    palette = widget.palette()
                                    palette.setColor(QPalette.ColorRole.Window, green_color)
                                    widget.setPalette(palette)
                                    widget.setAutoFillBackground(True)
                                    r, g, b, a = green_color.red(), green_color.green(), green_color.blue(), green_color.alpha()
                                    widget.setStyleSheet(f"background-color: rgba({r}, {g}, {b}, {a});")
            
            painter.end()
    
    def focusInEvent(self, event):
        """焦点进入事件 - 确保选中行的绿色被保持"""
        super().focusInEvent(event)
        # 当焦点回到表格时（比如右键菜单关闭后），确保选中行的绿色被保持
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self._ensure_selected_rows_green)
        QTimer.singleShot(10, self._ensure_selected_rows_green)
    
    def _update_green_rows(self):
        """更新绿色行集合（完全独立于Qt的selection机制）"""
        # 从selectionModel获取选中的行，更新我们的绿色行集合
        selection_model = self.selectionModel()
        new_green_rows = set()
        if selection_model:
            for index in selection_model.selectedRows():
                row = index.row()
                if row >= 0 and row < self.rowCount():
                    new_green_rows.add(row)
        
        # 更新绿色行集合
        self.green_rows = new_green_rows
        
        # 强制重绘
        self.viewport().update()
    
    def _ensure_selected_rows_green(self):
        """确保所有选中行的绿色被保持（内部方法）"""
        self._update_green_rows()
    
    def update_row_color(self, row):
        """更新行的背景颜色（非绿色行）"""
        if row < 0 or row >= self.rowCount():
            return
        
        # 如果行在绿色行集合中，不更新（绿色由paintEvent绘制）
        if row in self.green_rows:
            return
        
        # 根据行号确定基础颜色（交替行颜色，半透明）
        if row % 2 == 0:
            base_color = QColor(255, 255, 255, 120)  # 半透明白色
        else:
            base_color = QColor(245, 245, 245, 100)  # 半透明浅灰色
        
        # 如果是悬停行，应用柔和的悬停效果
        if row == self.hovered_row:
            base_color = QColor(227, 242, 253, 150)  # 浅蓝色，半透明
        
        # 更新该行的所有项目背景色
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(base_color)
            else:
                # 对于使用widget的列（如checkbox和combobox），需要清除widget的背景
                widget = self.cellWidget(row, col)
                if widget:
                    # 清除widget的背景色，恢复透明
                    widget.setAutoFillBackground(False)
                    widget.setStyleSheet("")  # 清除样式表
                    # 重置palette
                    from PySide6.QtGui import QPalette
                    palette = widget.palette()
                    palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 0))  # 透明
                    widget.setPalette(palette)
    
    def on_checkbox_state_changed(self, row, is_checked):
        """复选框状态改变处理"""
        # 记录使用日志并操作文件
        name_item = self.item(row, 1)
        if name_item:
            mod_name = name_item.text()
            # 通过parent找到MainWindow来记录日志和操作文件
            parent = self.parent()
            while parent and not hasattr(parent, 'log_mod_usage'):
                parent = parent.parent()
            if parent:
                if is_checked:
                    # 启用前先检查游戏目录是否设置
                    if not parent.check_game_path_set():
                        # 游戏目录未设置，回滚复选框状态
                        if row in self.checkbox_widgets:
                            self.checkbox_widgets[row].set_checked(False)
                        # 弹出提示并打开高级设置
                        from PySide6.QtWidgets import QMessageBox
                        QMessageBox.warning(
                            parent,
                            "请先设置游戏目录",
                            "请先设置游戏目录！\n\n将自动打开高级设置界面。"
                        )
                        parent.show_advanced_settings_panel()
                        return  # 不更新统计信息，因为实际上没有启用
                    
                    # 启用时，先尝试应用mod，如果失败则回滚复选框状态
                    success = parent.apply_mod_to_game(mod_name, is_checked)
                    if not success:
                        # 应用失败，回滚复选框状态
                        if row in self.checkbox_widgets:
                            self.checkbox_widgets[row].set_checked(False)
                        return  # 不记录日志，因为操作失败了
                    parent.log_mod_usage(mod_name, is_checked)
                else:
                    # 禁用时，直接操作文件并记录日志
                    parent.apply_mod_to_game(mod_name, is_checked)
                    parent.log_mod_usage(mod_name, is_checked)
            else:
                print(f"[错误] 无法找到主窗口")
        
        # 更新统计数据（只有在成功启用/禁用后才更新）
        self.statistics_changed.emit()
        
        # 确保选中行的绿色被保持（复选框状态改变可能触发重绘）
        # 使用QTimer.singleShot延迟执行，确保在重绘后恢复绿色
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self.restore_all_green)
    
    def get_enabled_mods(self):
        """获取所有启用的Mod名称列表"""
        enabled_mods = []
        for row, checkbox in self.checkbox_widgets.items():
            if checkbox.is_checked():
                name_item = self.item(row, 1)
                if name_item:
                    enabled_mods.append(name_item.text())
        return enabled_mods
    
    def set_mod_enabled(self, mod_name, enabled):
        """设置指定Mod的启用状态"""
        # 获取主窗口以调用文件操作
        parent = self.parent()
        while parent and not hasattr(parent, 'apply_mod_to_game'):
            parent = parent.parent()
        
        for row in range(self.rowCount()):
            name_item = self.item(row, 1)
            if name_item and name_item.text() == mod_name:
                if row in self.checkbox_widgets:
                    self.checkbox_widgets[row].set_checked(enabled)
                    # 手动调用文件操作（因为set_checked使用了blockSignals）
                    if parent:
                        parent.log_mod_usage(mod_name, enabled)
                        parent.apply_mod_to_game(mod_name, enabled)
                break
    
    def set_all_mods_enabled(self, enabled):
        """设置所有Mod的启用状态"""
        # 获取主窗口以调用文件操作
        parent = self.parent()
        while parent and not hasattr(parent, 'apply_mod_to_game'):
            parent = parent.parent()
        
        # 遍历所有mod并设置状态，同时执行文件操作
        for row, checkbox in self.checkbox_widgets.items():
            name_item = self.item(row, 1)
            if name_item:
                mod_name = name_item.text()
                checkbox.set_checked(enabled)
                # 手动调用文件操作（因为set_checked使用了blockSignals）
                if parent:
                    parent.log_mod_usage(mod_name, enabled)
                    parent.apply_mod_to_game(mod_name, enabled)
        
        self.statistics_changed.emit()
        
        # 打印批量操作结果
        if enabled:
            print(f"[成功] 全部启用完成")
        else:
            print(f"[成功] 全部禁用完成")
    
    def get_enabled_count(self):
        """获取启用的Mod数量"""
        return sum(1 for checkbox in self.checkbox_widgets.values() if checkbox.is_checked())
    
    def save_current_config(self):
        """保存当前启用的Mod配置"""
        self.saved_enabled_mods = self.get_enabled_mods().copy()
        # 配置已保存，不打印详细信息
    
    def restore_saved_config(self):
        """恢复保存的Mod配置"""
        # 获取主窗口以调用文件操作
        parent = self.parent()
        while parent and not hasattr(parent, 'apply_mod_to_game'):
            parent = parent.parent()
        
        # 首先禁用所有Mod（但不打印，因为这是批量操作的一部分）
        for row, checkbox in self.checkbox_widgets.items():
            name_item = self.item(row, 1)
            if name_item:
                mod_name = name_item.text()
                checkbox.set_checked(False)
                # 手动调用文件操作
                if parent:
                    parent.log_mod_usage(mod_name, False)
                    parent.apply_mod_to_game(mod_name, False)
        
        # 然后启用保存的Mod
        for mod_name in self.saved_enabled_mods:
            for row in range(self.rowCount()):
                name_item = self.item(row, 1)
                if name_item and name_item.text() == mod_name:
                    if row in self.checkbox_widgets:
                        self.checkbox_widgets[row].set_checked(True)
                        # 手动调用文件操作
                        if parent:
                            parent.log_mod_usage(mod_name, True)
                            parent.apply_mod_to_game(mod_name, True)
                    break
        
        print(f"[成功] 批量禁用还原完成")
    
    def binary_disable_dialog(self):
        """显示二分禁用对话框"""
        # 获取当前启用的Mod
        current_enabled = self.get_enabled_mods()
        
        if not current_enabled:
            return "none"  # 没有启用的Mod
        
        # 保存当前配置
        self.save_current_config()
        
        # 显示选择面板
        BinaryDisablePanel, _ = _import_panels()
        dialog = BinaryDisablePanel(self)
        
        # 在内嵌模式下，我们需要直接处理结果
        # 这里需要连接到主窗口的处理方法
        parent = self.parent()
        while parent and not hasattr(parent, 'handle_binary_disable_result'):
            parent = parent.parent()
        
        if parent:
            # 将面板添加到主窗口
            parent.show_binary_disable_panel(dialog)
            return "showing_panel"
        
        return "error"
    
    def binary_selection_dialog(self, mod_list):
        """显示二分选择对话框"""
        while True:
            if len(mod_list) <= 1:
                # 只有一个或没有Mod，直接禁用
                for mod_name in mod_list:
                    self.set_mod_enabled(mod_name, False)
                print(f"[成功] 批量禁用完成")
                return "completed"
            
            _, BinarySelectionPanel = _import_panels()
            dialog = BinarySelectionPanel(mod_list, self)
            result = dialog.exec()
            
            if result == 1:  # 用户点击了确认
                selected_mods = dialog.get_selected_mods()
                
                # 禁用选中的Mod
                for mod_name in selected_mods:
                    self.set_mod_enabled(mod_name, False)
                
                # 获取剩余启用的Mod
                remaining_enabled = self.get_enabled_mods()
                
                if not remaining_enabled:
                    print(f"[成功] 批量禁用完成")
                    return "completed"  # 没有剩余的Mod了
                
                # 继续二分选择
                mod_list = remaining_enabled
                continue
            else:  # result == 0，用户点击了取消
                # 用户取消，恢复保存的配置
                self.restore_saved_config()
                return "cancelled"
    
    def on_selection_changed(self, selected, deselected):
        """选择变化事件 - 更新绿色行集合"""
        self._update_green_rows()
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 彻底拦截右键取消绿色，忽略垂直表头点击"""
        pos = event.position().toPoint()
        
        # 检查点击位置是否在垂直表头（行号）区域
        vertical_header = self.verticalHeader()
        if vertical_header.isVisible():
            header_width = vertical_header.width()
            if pos.x() < header_width:
                # 点击在垂直表头区域，忽略点击，不做任何处理
                return
        
        if event.button() == Qt.LeftButton:
            row = self.rowAt(pos.y())
            
            if row >= 0:
                # 检查是否按下了Ctrl键
                modifiers = event.modifiers()
                is_ctrl_pressed = modifiers & Qt.KeyboardModifier.ControlModifier
                
                current_selected = self.selectionModel().selectedRows()
                is_selected = any(idx.row() == row for idx in current_selected)
                
                if is_ctrl_pressed:
                    # Ctrl+点击：切换选中状态（多选模式）
                    if is_selected:
                        # 如果已选中，取消选中
                        self.selectionModel().select(
                            self.model().index(row, 0),
                            QItemSelectionModel.Deselect | QItemSelectionModel.Rows
                        )
                    else:
                        # 如果未选中，添加到选中
                        self.selectionModel().select(
                            self.model().index(row, 0),
                            QItemSelectionModel.Select | QItemSelectionModel.Rows
                        )
                else:
                    # 普通点击：单选模式
                    if is_selected:
                        # 如果已选中，取消选中
                        self.selectionModel().clearSelection()
                    else:
                        # 选中新行：先清除选择，然后选择新行
                        self.selectionModel().clearSelection()
                        self.selectionModel().select(
                            self.model().index(row, 0),
                            QItemSelectionModel.Select | QItemSelectionModel.Rows
                        )
                return
        
        elif event.button() == Qt.RightButton:
            # 右键：从源头拦截，不让Qt处理任何可能取消绿色的操作
            pos = event.position().toPoint()
            row = self.rowAt(pos.y())
            
            if row >= 0:
                # 如果点击的行未选中，先选中它
                current_selected = self.selectionModel().selectedRows()
                if not any(idx.row() == row for idx in current_selected):
                    self.selectionModel().clearSelection()
                    self.selectionModel().select(
                        self.model().index(row, 0),
                        QItemSelectionModel.Select | QItemSelectionModel.Rows
                    )
                    # on_selection_changed会自动设置绿色
                
                # 在显示菜单前，确保选中行的绿色被保持
                self._ensure_selected_rows_green()
                
                # 显示右键菜单
                self.show_context_menu_at(pos, row)
                
                # 菜单关闭后，再次确保选中行的绿色被保持
                self._ensure_selected_rows_green()
                return
        
        super().mousePressEvent(event)
    
    def show_context_menu(self, position):
        """显示右键菜单 - 处理customContextMenuRequested信号"""
        pos = position.toPoint() if hasattr(position, 'toPoint') else position
        row = self.rowAt(pos.y())
        if row >= 0:
            self.show_context_menu_at(pos, row)
    
    def show_context_menu_at(self, position, row):
        """在指定位置显示右键菜单"""
        # 在显示菜单前，确保选中行的绿色被保持
        self._ensure_selected_rows_green()
        
        menu = QMenu(self)
        
        # 设置右键菜单样式，符合项目风格（紧凑设计）
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(255, 182, 193, 200);
                border: 2px solid #8B4513;
                border-radius: 8px;
                padding: 2px;
            }
            QMenu::item {
                background-color: transparent;
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
                padding: 4px 12px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: rgba(255, 255, 255, 180);
                color: #8B4513;
            }
            QMenu::separator {
                height: 1px;
                background-color: #8B4513;
                margin: 2px 6px;
            }
        """)
        
        # 添加详情选项
        details_action = menu.addAction("详情")
        details_action.triggered.connect(lambda: self.show_mod_details(row))
        
        # 获取mod名称
        mod_name = self.item(row, 1).text() if self.item(row, 1) else None
        
        # 添加收藏和忽略选项
        menu.addSeparator()
        favorite_action = menu.addAction("收藏")
        ignore_action = menu.addAction("忽略")
        
        # 检查当前状态并设置勾选标记
        # 查找MainWindow（向上遍历parent）
        parent = self.parent()
        while parent and not hasattr(parent, 'is_mod_favorite'):
            parent = parent.parent()
        
        if mod_name and parent:
            if parent.is_mod_favorite(mod_name):
                favorite_action.setText("取消收藏")
            if parent.is_mod_ignored(mod_name):
                ignore_action.setText("取消忽略")
        
        # 连接收藏和忽略功能
        favorite_action.triggered.connect(lambda: self.toggle_favorite(row))
        ignore_action.triggered.connect(lambda: self.toggle_ignore(row))
        
        # 添加打开到文件夹选项
        menu.addSeparator()
        open_folder_action = menu.addAction("打开到文件夹")
        open_folder_action.triggered.connect(lambda: self.open_mod_folder(row))
        
        # 检查mod是否禁用，如果禁用则添加卸载选项
        if row in self.checkbox_widgets:
            checkbox = self.checkbox_widgets[row]
            if not checkbox.is_checked():  # mod已禁用
                menu.addSeparator()  # 添加分隔线
                uninstall_action = menu.addAction("卸载")
                uninstall_action.triggered.connect(lambda: self.uninstall_mod(row))
        
        # 显示菜单（阻塞执行）
        menu.exec(self.mapToGlobal(position))
        
        # 菜单关闭后，立即确保选中行的绿色被保持
        # 使用QTimer延迟执行，确保在菜单关闭后的重绘完成后再恢复绿色
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self._ensure_selected_rows_green)
        QTimer.singleShot(10, self._ensure_selected_rows_green)  # 双重保险
        QTimer.singleShot(50, self._ensure_selected_rows_green)  # 三重保险
    
    def clear_all_green(self):
        """清除所有行的绿色，恢复交替行颜色"""
        # 先清除所有widget的背景色
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                widget = self.cellWidget(row, col)
                if widget:
                    widget.setAutoFillBackground(False)
                    widget.setStyleSheet("")  # 清除样式表
                    # 重置palette
                    from PySide6.QtGui import QPalette
                    palette = widget.palette()
                    palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 0))  # 透明
                    widget.setPalette(palette)
        
        self.green_rows.clear()
        self.viewport().update()  # 触发重绘
    
    def set_row_green(self, row):
        """设置指定行的绿色（添加到绿色行集合）"""
        if row >= 0 and row < self.rowCount():
            self.green_rows.add(row)
            self.viewport().update()  # 触发重绘
    
    def restore_all_green(self):
        """恢复所有选中行的绿色"""
        self._update_green_rows()
    
    def get_selected_mod_names(self):
        """获取所有选中行的Mod名称列表"""
        selected_mods = []
        selection_model = self.selectionModel()
        if selection_model:
            for index in selection_model.selectedRows():
                row = index.row()
                name_item = self.item(row, 1)
                if name_item:
                    selected_mods.append(name_item.text())
        return selected_mods
    
    def uninstall_mod(self, row):
        """卸载mod（永久移除）"""
        mod_name = self.item(row, 1).text() if self.item(row, 1) else None
        if not mod_name:
            return
        
        # 确认对话框
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "确认卸载",
            f"确定要永久卸载mod '{mod_name}' 吗？\n此操作无法撤销！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # 通过parent找到MainWindow来执行卸载
        parent = self.parent()
        while parent and not hasattr(parent, 'uninstall_mod_permanently'):
            parent = parent.parent()
        
        if parent:
            parent.uninstall_mod_permanently(mod_name, row)
        else:
            QMessageBox.warning(self, "错误", "无法找到主窗口")
    
    def toggle_favorite(self, row):
        """切换收藏状态"""
        mod_name = self.item(row, 1).text() if self.item(row, 1) else None
        if not mod_name:
            return
        
        # 查找MainWindow（向上遍历parent）
        parent = self.parent()
        while parent and not hasattr(parent, 'toggle_mod_favorite'):
            parent = parent.parent()
        
        if parent:
            parent.toggle_mod_favorite(mod_name, row)
    
    def toggle_ignore(self, row):
        """切换忽略状态"""
        mod_name = self.item(row, 1).text() if self.item(row, 1) else None
        if not mod_name:
            return
        
        # 查找MainWindow（向上遍历parent）
        parent = self.parent()
        while parent and not hasattr(parent, 'toggle_mod_ignore'):
            parent = parent.parent()
        
        if parent:
            parent.toggle_mod_ignore(mod_name, row)
    
    def open_mod_folder(self, row):
        """打开mod对应的文件夹"""
        mod_name = self.item(row, 1).text() if self.item(row, 1) else None
        if not mod_name:
            return
        
        # 查找MainWindow（向上遍历parent）
        parent = self.parent()
        while parent and not hasattr(parent, 'get_project_root'):
            parent = parent.parent()
        
        if parent:
            import os
            import subprocess
            import platform
            
            project_root = parent.get_project_root()
            mods_dir = os.path.join(project_root, "mods")
            mod_folder_name = mod_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
            mod_folder_path = os.path.join(mods_dir, mod_folder_name)
            
            if os.path.exists(mod_folder_path):
                try:
                    # 根据操作系统使用不同的命令打开文件夹
                    if platform.system() == "Windows":
                        os.startfile(mod_folder_path)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.Popen(["open", mod_folder_path])
                    else:  # Linux
                        subprocess.Popen(["xdg-open", mod_folder_path])
                except Exception as e:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "错误", f"无法打开文件夹：{str(e)}")
            else:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "错误", f"找不到mod文件夹：{mod_folder_path}")
    
    def show_mod_details(self, row):
        """显示模组详情"""
        mod_name = self.item(row, 1).text() if self.item(row, 1) else "未知模组"
        category = self.item(row, 2).text() if self.item(row, 2) else "未分类"
        author = self.item(row, 3).text() if self.item(row, 3) else "未知"
        
        parent = self.parent()
        while parent and not hasattr(parent, 'edit_mod'):
            parent = parent.parent()
        
        if parent:
            parent.edit_mod(mod_name, category, author)

