"""
数据模型模块
"""
# 延迟导入，避免打包环境下的导入问题
def _import_all():
    """导入所有模块，兼容开发环境和打包环境"""
    try:
        from .checkbox import ModCheckBox
        from .table import CustomModTable
        from .panels import BinaryDisablePanel, BinarySelectionPanel
        return ModCheckBox, CustomModTable, BinaryDisablePanel, BinarySelectionPanel
    except ImportError:
        try:
            from models.checkbox import ModCheckBox
            from models.table import CustomModTable
            from models.panels import BinaryDisablePanel, BinarySelectionPanel
            return ModCheckBox, CustomModTable, BinaryDisablePanel, BinarySelectionPanel
        except ImportError:
            # 最后尝试：直接导入文件
            import os
            import importlib.util
            models_dir = os.path.dirname(__file__)
            
            checkbox_path = os.path.join(models_dir, 'checkbox.py')
            table_path = os.path.join(models_dir, 'table.py')
            panels_path = os.path.join(models_dir, 'panels.py')
            
            ModCheckBox = None
            CustomModTable = None
            BinaryDisablePanel = None
            BinarySelectionPanel = None
            
            if os.path.exists(checkbox_path):
                spec = importlib.util.spec_from_file_location("models.checkbox", checkbox_path)
                checkbox_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(checkbox_module)
                ModCheckBox = checkbox_module.ModCheckBox
            
            if os.path.exists(table_path):
                spec = importlib.util.spec_from_file_location("models.table", table_path)
                table_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(table_module)
                CustomModTable = table_module.CustomModTable
            
            if os.path.exists(panels_path):
                spec = importlib.util.spec_from_file_location("models.panels", panels_path)
                panels_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(panels_module)
                BinaryDisablePanel = panels_module.BinaryDisablePanel
                BinarySelectionPanel = panels_module.BinarySelectionPanel
            
            return ModCheckBox, CustomModTable, BinaryDisablePanel, BinarySelectionPanel

# 立即导入所有模块
ModCheckBox, CustomModTable, BinaryDisablePanel, BinarySelectionPanel = _import_all()

__all__ = ['ModCheckBox', 'CustomModTable', 'BinaryDisablePanel', 'BinarySelectionPanel']



