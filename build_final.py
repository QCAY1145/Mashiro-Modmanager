"""
最终打包脚本 - 使用英文名称和管理员权限
"""
import os
import subprocess
import sys

def build():
    project_root = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(project_root, "main.pyw")
    background_dir = os.path.join(project_root, "background")
    json_dir = os.path.join(project_root, "json")
    
    # 查找图标文件（优先使用.ico，如果没有则使用.png）
    icon_file = None
    icon_paths = [
        os.path.join(project_root, "icon.ico"),
        os.path.join(background_dir, "icon.ico"),
        os.path.join(background_dir, "title.ico"),
        os.path.join(background_dir, "title.png"),  # 如果没有.ico，尝试使用.png
    ]
    
    for path in icon_paths:
        if os.path.exists(path):
            icon_file = path
            break
    
    # 获取models目录
    models_dir = os.path.join(project_root, "models")
    
    cmd = [
        "pyinstaller",
        "--windowed",
        "--onefile", 
        "--name=ModManager",
        "--uac-admin",  # 请求管理员权限
        "--add-data=" + background_dir + os.pathsep + "background",
        "--add-data=" + json_dir + os.pathsep + "json",
        "--add-data=" + models_dir + os.pathsep + "models",  # 确保models目录被包含
        "--hidden-import=models",  # 确保models包被包含
        "--hidden-import=models.panels",  # 确保panels模块被包含
        "--hidden-import=models.checkbox",  # 确保checkbox模块被包含
        "--hidden-import=models.table",  # 确保table模块被包含
        "--collect-all=models",  # 收集models包的所有子模块
    ]
    
    # 如果找到图标文件，添加到命令中
    if icon_file:
        cmd.append("--icon=" + icon_file)
        print(f"使用图标文件: {icon_file}")
    else:
        print("警告: 未找到图标文件，将使用默认图标")
        print("提示: 可以将 title.png 转换为 icon.ico 并放在项目根目录或 background 目录下")
    
    cmd.append(main_script)
    
    print("开始最终打包...")
    print("命令:", " ".join(cmd))
    
    try:
        result = subprocess.run(cmd, cwd=project_root, shell=True)
        if result.returncode == 0:
            print("打包成功!")
            exe_path = os.path.join(project_root, "dist", "ModManager.exe")
            print(f"文件位置: {exe_path}")
            return True
        else:
            print("打包失败!")
            return False
    except Exception as e:
        print(f"异常: {e}")
        return False

if __name__ == "__main__":
    build()
