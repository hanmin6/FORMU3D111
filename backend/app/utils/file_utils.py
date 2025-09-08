# app/utils/file_utils.py

from datetime import datetime
from pathlib import Path
from fastapi import UploadFile, HTTPException

# 定义上传目录并确保存在
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def save_upload_file(file: UploadFile) -> Path:
    """
    验证并保存上传的图片文件，返回保存后的路径。

    Args:
        file: 从 FastAPI 接收的 UploadFile 对象。

    Returns:
        保存文件的 Path 对象。

    Raises:
        HTTPException: 如果文件不是图片或保存失败。
    """
    content_type = (file.content_type or "").lower()
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="仅支持图片文件上传")

    # 生成不重复文件名：时间戳_原始文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = Path(file.filename).name
    save_name = f"{timestamp}_{safe_name}"
    save_path = UPLOAD_DIR / save_name

    # 保存文件
    try:
        data = await file.read()
        save_path.write_bytes(data)
    except Exception as e:
        # 在服务端记录详细错误，但只给客户端返回通用错误
        # logger.error(f"Failed to save file to {save_path}: {e}")
        raise HTTPException(status_code=500, detail="文件保存失败")

    return save_path