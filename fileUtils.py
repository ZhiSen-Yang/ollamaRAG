import datetime
import os
import sys
import traceback

from init import config


def get_save_dir(dir_type: int) -> str:
    """
    根据操作系统自动生成合规路径
    :param dir_type: 0-文档目录 1-图片目录
    :return: 合规的完整路径
    """
    # 根据操作系统选择基础路径
    folder_path = config["app"]["file"]["path"]
    if sys.platform.startswith('win'):
        base_dir = folder_path  # Windows系统默认路径
    else:
        base_dir = os.path.expanduser(folder_path)  # Linux/Mac用户目录

    # 动态生成子目录名称
    sub_dir = 'pdffile' if dir_type == 0 else 'imgfile'

    try:
        # 构建完整路径
        full_path = os.path.join(base_dir) + os.sep

        # 智能创建目录（exist_ok=True可防止并发冲突）
        os.makedirs(full_path, exist_ok=True)

        return full_path

    except Exception as e:
        # 错误处理增强：记录操作系统和路径信息
        error_info = {
            "os": sys.platform,
            "path_attempted": full_path,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

        # 结构化日志记录
        log_entry = (
            f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"ERROR in get_save_dir:\n"
            f"OS: {error_info['os']}\n"
            f"Path: {error_info['path_attempted']}\n"
            f"Error: {error_info['error']}\n"
            f"Traceback:\n{error_info['traceback']}\n"
        )

        # 原子化写入日志
        with open("path_errors.log", "a", encoding='utf-8') as f:
            f.write(log_entry)

        # 创建应急目录
        fallback_dir = os.path.join(os.getcwd(), 'temp_storage') + os.sep
        os.makedirs(fallback_dir, exist_ok=True)
        return fallback_dir