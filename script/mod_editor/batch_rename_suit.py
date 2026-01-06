"""
批量重命名套装脚本
功能：将当前mod中的套装编号替换为其他套装编号
"""
import sys
import os
import json
import re
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QMessageBox,
    QLineEdit,
    QInputDialog,
)
from PySide6.QtCore import Qt


def get_project_root():
    """获取项目根目录（脚本在 script/mod_editor 下，向上两级）"""
    current_dir = os.path.dirname(os.path.abspath(__file__))  # script/mod_editor
    return os.path.dirname(os.path.dirname(current_dir))      # 项目根目录


def get_main_window():
    """获取主窗口实例"""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app:
        # 查找主窗口
        for widget in app.allWidgets():
            if hasattr(widget, 'mod_name_input') and hasattr(widget, 'get_mod_file_path'):
                return widget
    return None


def load_f_equipment_dict():
    """加载f_equipment字典"""
    project_root = get_project_root()
    dict_path = os.path.join(project_root, "dictionary", "f_equipment.json")
    
    if not os.path.exists(dict_path):
        return None
    
    try:
        with open(dict_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载字典失败: {e}")
        return None


def parse_folder_name(folder_name, dict_data):
    """解析文件夹名称，返回对应的套装名称"""
    # 在字典中查找（不区分大小写），并规范显示文本
    def normalize_display(text):
        import re as _re
        return _re.sub(r"^【(.*)】\s*服装$", r"\1", text).strip() if isinstance(text, str) else text

    if isinstance(dict_data, list):
        for item in dict_data:
            if isinstance(item, list) and len(item) >= 2:
                path = str(item[0]).replace("\\", "/").lower()
                meaning = normalize_display(item[1])
                # 取路径最后一段文件夹名，例如 pl027_0500
                last_seg = path.split("/")[-1]
                if last_seg == folder_name.lower():
                    return meaning

    return None


def get_f_equip_folders(mod_file_path):
    """获取nativePC/pl/f_equip/下的所有文件夹（忽略大小写，兼容zip/文件夹）"""
    folders = []
    
    try:
        if mod_file_path.endswith('.zip'):
            import zipfile
            with zipfile.ZipFile(mod_file_path, 'r') as zip_file:
                for name in zip_file.namelist():
                    # 统一路径分隔
                    name = name.replace("\\", "/")
                    lower_name = name.lower()
                    if '/pl/f_equip/' in lower_name:
                        parts = lower_name.split('/pl/f_equip/')
                        if len(parts) > 1:
                            folder_part = parts[1].split('/')[0]
                            if folder_part:
                                folders.append(folder_part)
        elif os.path.isdir(mod_file_path):
            # 兼容 nativePC / nativepc / 直接 pl/f_equip
            candidates = [
                os.path.join(mod_file_path, "nativePC", "pl", "f_equip"),
                os.path.join(mod_file_path, "nativepc", "pl", "f_equip"),
                os.path.join(mod_file_path, "pl", "f_equip"),
            ]
            for f_equip_path in candidates:
                if os.path.exists(f_equip_path):
                    for item in os.listdir(f_equip_path):
                        item_path = os.path.join(f_equip_path, item)
                        if os.path.isdir(item_path):
                            folders.append(item)
    except Exception as e:
        print(f"获取文件夹列表失败: {e}")
    
    # 去重并保持顺序
    return list(dict.fromkeys(folders))


def find_pl_number_in_mod(mod_file_path):
    """在mod内查找任意plXXXX编号（遍历f_equip内所有路径）"""
    def extract_number(text):
        m = re.search(r'pl(\d{4})', text, re.IGNORECASE)
        return m.group(1) if m else None

    # zip模式
    if mod_file_path.endswith('.zip'):
        import zipfile
        try:
            with zipfile.ZipFile(mod_file_path, 'r') as zip_file:
                for name in zip_file.namelist():
                    name = name.replace("\\", "/")
                    lower_name = name.lower()
                    if '/pl/f_equip/' in lower_name:
                        num = extract_number(lower_name)
                        if num:
                            return num
        except Exception as e:
            print(f"扫描zip获取编号失败: {e}")
        return None

    # 文件夹模式
    if os.path.isdir(mod_file_path):
        candidates = [
            os.path.join(mod_file_path, "nativePC", "pl", "f_equip"),
            os.path.join(mod_file_path, "nativepc", "pl", "f_equip"),
            os.path.join(mod_file_path, "pl", "f_equip"),
        ]
        for base in candidates:
            if os.path.exists(base):
                for root, dirs, files in os.walk(base):
                    for name in dirs + files:
                        num = extract_number(name)
                        if num:
                            return num
    return None


def extract_suit_number_from_folder(folder_name: str):
    """从文件夹名中提取套装编号，兼容 pl027_0500 / pl0527_0000 / pl1234 等形式"""
    if not folder_name:
        return None
    name = folder_name.lower()
    # 先按 plxxx_xxxx 这种拆
    if name.startswith("pl"):
        base = name.split("_")[0]  # pl027_0500 -> pl027
        num = base[2:]
        if num.isdigit():
            return num
    # 兜底：匹配 pl后面3-4位数字
    m = re.search(r"pl(\d{3,4})", name)
    if m:
        return m.group(1)
    return None


def get_all_suit_names(dict_data):
    """获取所有套装名称"""
    suit_names = []
    if isinstance(dict_data, list):
        for item in dict_data:
            if isinstance(item, list) and len(item) >= 2:
                meaning = item[1]
                # 统一去掉形如【xxx】服装的包装
                if isinstance(meaning, str):
                    import re as _re
                    meaning = _re.sub(r"^【(.*)】\s*服装$", r"\1", meaning).strip()
                suit_names.append(meaning)
    # 去重并排序
    return sorted(set(suit_names))


def get_suit_number(suit_name, dict_data):
    """根据套装名称获取对应的套装文件夹ID（如 pl027_0500）"""
    # 规范化名字：去掉【】服装
    def normalize_display(text):
        import re as _re
        return _re.sub(r"^【(.*)】\s*服装$", r"\1", text).strip() if isinstance(text, str) else text

    if isinstance(dict_data, list):
        for item in dict_data:
            if isinstance(item, list) and len(item) >= 2:
                path = str(item[0]).replace("\\", "/").lower()
                meaning = normalize_display(item[1])
                # 与下拉框显示的一致名字比较
                if meaning == suit_name:
                    # 返回路径最后一段作为ID，例如 pl027_0500
                    last_seg = path.split("/")[-1]
                    return last_seg
    return None


def replace_suit_numbers(mod_file_path, old_id, new_id):
    """在指定套装文件夹范围内，将旧ID替换为新ID
    只要命中编号段 xxx_xxxx 就替换，不再要求前面是 pl。
    """
    replaced_count = 0
    
    try:
        if mod_file_path.endswith('.zip'):
            import zipfile
            import tempfile
            import shutil
            
            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            temp_zip = os.path.join(temp_dir, "temp_mod.zip")
            
            try:
                # 复制zip文件
                shutil.copy2(mod_file_path, temp_zip)
                
                # 读取zip内容
                with zipfile.ZipFile(temp_zip, 'r') as zip_read:
                    file_list = zip_read.namelist()
                    new_file_list = []
                    
                    # 编号段，去掉前缀 pl，仅替换数字段
                    def split_id(val: str):
                        v = val.lower()
                        return v[2:] if v.startswith("pl") else v

                    old_seg = split_id(old_id)
                    new_seg = split_id(new_id)
                    pattern = re.compile(re.escape(old_seg), re.IGNORECASE)
                    lower_old = old_id.lower()
                    for file_path in file_list:
                        norm = file_path.replace("\\", "/").lower()
                        # 只处理位于指定套装文件夹下的文件
                        if f"/pl/f_equip/{lower_old}/" in norm:
                            new_path = pattern.sub(new_seg, file_path)
                            if new_path != file_path:
                                replaced_count += 1
                            new_file_list.append((file_path, new_path))
                        else:
                            new_file_list.append((file_path, file_path))
                    
                    # 创建新的zip文件
                    with zipfile.ZipFile(mod_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_write:
                        for old_path, new_path in new_file_list:
                            if old_path != new_path:
                                # 读取旧文件内容
                                data = zip_read.read(old_path)
                                # 写入新路径
                                zip_write.writestr(new_path, data)
                            else:
                                # 直接复制
                                data = zip_read.read(old_path)
                                zip_write.writestr(new_path, data)
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
        
        elif os.path.isdir(mod_file_path):
            # 文件夹模式：仅在指定套装文件夹下重命名
            # 先定位 f_equip 目录
            base_dir = None
            candidates = [
                os.path.join(mod_file_path, "nativePC", "pl", "f_equip"),
                os.path.join(mod_file_path, "nativepc", "pl", "f_equip"),
                os.path.join(mod_file_path, "pl", "f_equip"),
            ]
            for c in candidates:
                if os.path.exists(c):
                    base_dir = c
                    break
            if base_dir is None:
                return 0

            # 当前套装根目录
            suit_root = os.path.join(base_dir, old_id)
            if not os.path.exists(suit_root):
                return 0

            # 编号段，去掉前缀 pl，仅替换数字段
            def split_id(val: str):
                v = val.lower()
                return v[2:] if v.startswith("pl") else v

            old_seg = split_id(old_id)
            new_seg = split_id(new_id)
            pattern = re.compile(re.escape(old_seg), re.IGNORECASE)

            # 先重命名内部文件和子文件夹
            for root, dirs, files in os.walk(suit_root, topdown=False):
                # 重命名文件
                for file_name in files:
                    if pattern.search(file_name):
                        old_path = os.path.join(root, file_name)
                        new_file_name = pattern.sub(new_seg, file_name)
                        new_path = os.path.join(root, new_file_name)
                        os.rename(old_path, new_path)
                        replaced_count += 1
                # 重命名子文件夹
                for dir_name in dirs:
                    if pattern.search(dir_name):
                        old_path = os.path.join(root, dir_name)
                        new_dir_name = pattern.sub(new_seg, dir_name)
                        new_path = os.path.join(root, new_dir_name)
                        os.rename(old_path, new_path)
                        replaced_count += 1

            # 最后重命名套装根文件夹本身
            if pattern.search(old_id):
                new_root_name = pattern.sub(new_seg, old_id)
                new_root_path = os.path.join(base_dir, new_root_name)
                if suit_root != new_root_path:
                    os.rename(suit_root, new_root_path)
                    replaced_count += 1
    
    except Exception as e:
        print(f"替换失败: {e}")
        raise
    
    return replaced_count


class SuitRenameDialog(QDialog):
    """套装重命名对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = get_main_window()
        self.dict_data = load_f_equipment_dict()
        self.all_suit_names = []
        self.current_folder = None
        self.current_number = None
        self.setup_ui()
        self.load_current_mod()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("批量重命名套装")
        self.setMinimumSize(500, 200)
        self.resize(600, 250)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # 样式
        label_style = """
            QLabel {
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
            }
        """
        
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """
        
        # 主要内容区域
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # 左侧：当前套装名称
        self.current_suit_label = QLabel("当前套装：")
        self.current_suit_label.setStyleSheet(label_style)
        self.current_suit_value = QLabel("未找到")
        self.current_suit_value.setStyleSheet("""
            QLabel {
                color: #8B4513;
                font-size: 14px;
                padding: 5px;
                border: 1px solid #8B4513;
                border-radius: 4px;
                background-color: rgba(255, 255, 255, 200);
            }
        """)
        self.current_suit_value.setMinimumWidth(200)
        
        # 中间：替换为标签
        replace_label = QLabel("替换为：")
        replace_label.setStyleSheet(label_style)
        
        # 右侧：输入 + 下拉（实时过滤）
        right_layout = QVBoxLayout()
        right_layout.setSpacing(8)

        self.suit_input = QLineEdit()
        self.suit_input.setPlaceholderText("输入套装名称进行过滤")
        self.suit_input.textChanged.connect(self.update_filtered_suits)
        self.suit_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
                padding: 6px;
                min-width: 200px;
            }
            QLineEdit:focus {
                border: 2px solid #8B4513;
            }
        """)

        self.suit_combo = QComboBox()
        self.suit_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #8B4513;
                border-radius: 4px;
                color: #8B4513;
                font-size: 14px;
                padding: 5px;
                min-width: 200px;
            }
            QComboBox:hover {
                background-color: rgba(255, 182, 193, 200);
            }
        """)

        right_layout.addWidget(self.suit_input)
        right_layout.addWidget(self.suit_combo)
        
        content_layout.addWidget(self.current_suit_label)
        content_layout.addWidget(self.current_suit_value, stretch=1)
        content_layout.addWidget(replace_label)
        content_layout.addLayout(right_layout, stretch=1)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.replace_btn = QPushButton("替换")
        self.replace_btn.setStyleSheet(button_style)
        self.replace_btn.clicked.connect(self.do_replace)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setStyleSheet(button_style)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.replace_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_current_mod(self):
        """加载当前mod信息"""
        if not self.main_window:
            QMessageBox.warning(self, "错误", "无法获取主窗口实例")
            self.reject()
            return
        
        # 获取当前mod名称
        mod_name = self.main_window.mod_name_input.text().strip()
        if not mod_name:
            QMessageBox.warning(self, "错误", "请先输入或选择要编辑的mod")
            self.reject()
            return
        
        # 获取mod文件路径
        mod_file_path = self.main_window.get_mod_file_path(mod_name)
        if not mod_file_path or not os.path.exists(mod_file_path):
            QMessageBox.warning(self, "错误", f"找不到mod文件: {mod_name}")
            self.reject()
            return
        
        # 获取f_equip文件夹
        folders = get_f_equip_folders(mod_file_path)
        if not folders:
            QMessageBox.warning(self, "错误", "未找到nativePC/pl/f_equip/文件夹")
            self.reject()
            return
        
        # 使用第一个找到的文件夹
        # 选择包含plXXXX的文件夹；若没有，则取第一个
        pl_folders = [f for f in folders if re.search(r'pl\d{4}', f, re.IGNORECASE)]
        self.current_folder = pl_folders[0] if pl_folders else folders[0]
        
        # 解析文件夹名称
        if self.dict_data:
            suit_name = parse_folder_name(self.current_folder, self.dict_data)
            if suit_name:
                self.current_suit_value.setText(suit_name)
            else:
                self.current_suit_value.setText(f"未解析 ({self.current_folder})")
        else:
            self.current_suit_value.setText(self.current_folder)
        
        # 提取当前编号（优先从文件夹名解析，失败再全局扫描）
        self.current_number = extract_suit_number_from_folder(self.current_folder)
        if not self.current_number:
            self.current_number = find_pl_number_in_mod(mod_file_path)
        
        # 加载所有套装名称，供过滤使用
        self.all_suit_names = get_all_suit_names(self.dict_data) if self.dict_data else []
        self.update_filtered_suits("")
        
        # 保存mod文件路径
        self.mod_file_path = mod_file_path
    
    def update_filtered_suits(self, text):
        """根据输入实时过滤套装列表"""
        keyword = (text or "").strip().lower()
        self.suit_combo.blockSignals(True)
        self.suit_combo.clear()
        for name in self.all_suit_names:
            if keyword in name.lower():
                self.suit_combo.addItem(name)
        self.suit_combo.blockSignals(False)
        if self.suit_combo.count() > 0:
            self.suit_combo.setCurrentIndex(0)
    
    def do_replace(self):
        """执行替换"""
        selected_suit = self.suit_combo.currentText()
        if not selected_suit:
            QMessageBox.warning(self, "错误", "请选择要替换的套装")
            return

        # 当前套装ID（文件夹名，例如 pl027_0500）
        if not self.current_folder:
            QMessageBox.warning(self, "错误", "无法确定当前套装文件夹")
            return
        old_id = self.current_folder

        # 获取目标套装编号
        if not self.dict_data:
            QMessageBox.warning(self, "错误", "字典数据未加载")
            return
        
        new_id = get_suit_number(selected_suit, self.dict_data)
        if not new_id:
            QMessageBox.warning(self, "错误", f"无法获取套装 '{selected_suit}' 的路径ID")
            return
        
        if old_id.lower() == new_id.lower():
            QMessageBox.information(self, "提示", "当前套装和目标套装相同，无需替换")
            return
        
        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认替换",
            f"要将 {old_id} 改为 {new_id}（{selected_suit}），该操作不可撤销，且仅作用于当前套装文件夹范围内。\n\n是否继续？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            # 执行替换
            replaced_count = replace_suit_numbers(self.mod_file_path, old_id, new_id)
            # 替换成功后，刷新文件树并重新应用字典
            if replaced_count > 0 and self.main_window:
                try:
                    mod_name = self.main_window.mod_name_input.text().strip()
                    if mod_name:
                        mod_path = self.main_window.get_mod_file_path(mod_name)
                        if mod_path and os.path.exists(mod_path):
                            file_list = []
                            if mod_path.endswith(".zip"):
                                import zipfile
                                with zipfile.ZipFile(mod_path, "r") as zip_file:
                                    file_list = zip_file.namelist()
                            elif os.path.isdir(mod_path):
                                file_list = self.main_window.get_folder_files(mod_path)
                            if file_list:
                                self.main_window.display_file_tree(file_list)
                                # 重新应用字典解析
                                if hasattr(self.main_window, "parse_mod_with_dictionaries"):
                                    self.main_window.parse_mod_with_dictionaries()
                except Exception as _e:
                    # 刷新失败不阻止对话框关闭
                    print(f"刷新文件列表或重新解析字典失败: {_e}")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "替换失败", f"替换过程中发生错误:\n{str(e)}")


def main():
    """主函数"""
    from PySide6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    dialog = SuitRenameDialog()
    dialog.exec()


if __name__ == "__main__":
    main()

