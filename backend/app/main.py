from datetime import datetime
from pathlib import Path
from typing import Optional
import httpx
from fastapi import Depends, FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from cozepy import MessageObjectString

from app.core.middleware import LoggingMiddleware
from app.core.logger import get_logger
from app.api import api_router
from app.services.llm_factory import LLMFactory
from app.core.database import ensure_database_and_tables
from app.services.sora_service import SoraService
from app.services.tripo_service import Tripo3DService
from app.utils.file_utils import save_upload_file
from app.middleware.auth_middleware import check_usage_limit, check_3d_permission, check_prompt_permission 


# 初始化 logger
logger = get_logger(__name__)  # 新增 

# 定义上传目录并确保存在
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 创建应用实例（保持不变）
app = FastAPI(title="FORMU REST API")

# 中间件与路由：移除重复配置
app.add_middleware(LoggingMiddleware)
# 允许的来源域名列表
origins = [
    "https://www.formu.online",  # Vercel 前端的生产域名
    "https://formu.online",      # 备用域名格式
    "http://localhost:5173",     # 本地开发时用的地址
    "http://localhost:3000",     # 备用本地地址
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 请求头
)
app.include_router(api_router, prefix="/api")  # 只保留一次路由挂载

# 健康检查接口
@app.get("/health")
async def health_check():
    """健康检查接口，用于诊断配置问题"""
    try:
        from app.core.railway_config import RailwayConfig
        
        config_status = {
            "coze_authorization": bool(RailwayConfig.get_coze_authorization()),
            "coze_base_url": bool(RailwayConfig.get_coze_base_url()),
            "picture_analysis_bot_id": bool(RailwayConfig.get_bot_id("PICTURE_ANALYSIS")),
            "sora_api_key": bool(RailwayConfig.get_sora_api_key()),
            "sora_base_url": bool(RailwayConfig.get_sora_base_url()),
            "tripo_api_key": bool(RailwayConfig.get_tripo_api_key()),
        }
        
        all_configured = all(config_status.values())
        
        return {
            "status": "healthy" if all_configured else "configuration_issues",
            "config_status": config_status,
            "message": "所有配置正常" if all_configured else "部分配置缺失，请检查环境变量"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"健康检查失败: {str(e)}"
        }

# 注意：Railway 上不挂载本地文件系统，因为文件系统是临时的
# 应用启动时确保数据库和数据表就绪
@app.on_event("startup")
async def _startup_init_db():
    try:
        await ensure_database_and_tables()
        logger.info("Database and tables are ready")
    except Exception as e:
        logger.error(f"Failed to ensure database/tables: {e}")


# ========== 文件上传接口 ==========
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # 校验文件类型
    content_type = (file.content_type or "").lower()
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="仅支持图片文件上传")

    try:
        # 读取文件数据
        data = await file.read()
        
        # 生成不重复文件名：时间戳_原始文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = Path(file.filename).name
        save_name = f"{timestamp}_{safe_name}"
        
        # 在 Railway 上，我们直接返回文件数据，不保存到本地文件系统
        # 因为 Railway 的文件系统是临时的
        import base64
        file_data_base64 = base64.b64encode(data).decode('utf-8')
        
        logger.info(f"Image uploaded: {save_name} ({len(data)} bytes)")
        return {
            "message": "上传完成",
            "filename": save_name,
            "url": f"data:{content_type};base64,{file_data_base64}",
            "size": len(data)
        }
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


# ========== 生成图片分析和提示词（SSE） ==========
@app.post("/prompt-generation")
async def prompt_generation(
    style: str, 
    file: UploadFile = File(...),
    current_user = Depends(check_usage_limit)
):
    # 允许的风格映射到工厂方法
    style_factory = {
        "cute": LLMFactory.create_cute_style_prompt_generation_service,
        "steampunk": LLMFactory.create_steampunk_style_prompt_generation_service,
        "japanese_comic": LLMFactory.create_japanese_comic_style_prompt_generation_service,
        "american_comic": LLMFactory.create_american_comic_style_prompt_generation_service,
        "profession": LLMFactory.create_profession_style_prompt_generation_service,
        "cyberpunk": LLMFactory.create_cyberpunk_style_prompt_generation_service,
        "gothic": LLMFactory.create_gothic_style_prompt_generation_service,
        "realistic": LLMFactory.create_realistic_style_prompt_generation_service,
    }

    if style not in style_factory:
        raise HTTPException(status_code=422, detail="无效的风格参数")

    # 处理上传的图片
    content_type = (file.content_type or "").lower()
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="仅支持图片文件")

    try:
        # 读取文件数据
        data = await file.read()
        
        # 生成临时文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = Path(file.filename).name
        save_name = f"{timestamp}_{safe_name}"
        save_path = UPLOAD_DIR / save_name
        
        # 临时保存文件用于 Coze 上传
        save_path.write_bytes(data)

        picture_service = LLMFactory.create_picture_analysis_service()

        # 1) 上传图片到 Coze，拿到 file_id
        try:
            file_id = await picture_service.upload_local_image(str(save_path))
        except ValueError as e:
            # 配置错误
            raise HTTPException(status_code=500, detail=f"服务配置错误: {str(e)}")
        except Exception as e:
            # 其他错误
            raise HTTPException(status_code=500, detail=f"图片上传到分析服务失败: {str(e)}")
        finally:
            # 清理临时文件
            try:
                if save_path.exists():
                    save_path.unlink()
            except:
                pass

        # 2) 先流式输出图片分析信息（event: analysis），同时拼接成完整文本
        prompt_service = style_factory[style]()

    except Exception as e:
        logger.error(f"Prompt generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"提示词生成失败: {str(e)}")

    async def event_stream():
        try:
            # 2.1 流式分析
            analysis_parts = []
            async for chunk in picture_service.generate_stream(
                objects=[
                    MessageObjectString.build_text("请描述一下图片中的内容"),
                    MessageObjectString.build_image(file_id=file_id, file_url=None),
                ],
                meta_data=None,
            ):
                if not chunk.startswith("data:"):
                    continue
                content = chunk[len("data: "):].strip()
                if content == "[DONE]":
                    break
                if content:
                    analysis_parts.append(content)
                    # 标记为图片分析阶段，便于前端区分展示
                    yield f"event: analysis\ndata: {content}\n\n"

            analysis_text = "".join(analysis_parts)

            # 2.2 根据风格生成提示词（event: prompt）
            async for sse_chunk in prompt_service.generate_stream(
                objects=[MessageObjectString.build_text(analysis_text)],
                meta_data=None,
            ):
                if not sse_chunk.startswith("data:"):
                    continue
                prompt_content = sse_chunk[len("data: "):].strip()
                if prompt_content == "[DONE]":
                    break
                yield f"event: prompt\ndata: {prompt_content}\n\n"

            # 结束信号（兼容原有消费方式）
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: 出错: {str(e)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ========== 通过网络图片链接生成提示词（SSE） ==========
class GenerateFromUrlRequest(BaseModel):
    style: str
    image_url: HttpUrl


class SoraGenerationRequest(BaseModel):
    prompt: str
    model: str = "sora_image"  # 您可以设置一个默认模型
    n: int = 1
    size: str = "1024x1024"
    is_async: bool = False
    auth_key: Optional[str] = None # 允许前端临时覆盖 key

class TaskSubmitResponse(BaseModel):
    task_id: str
@app.post("/prompt-generation-url")
async def prompt_generation_by_url(payload: GenerateFromUrlRequest):
    style_factory = {
        "cute": LLMFactory.create_cute_style_prompt_generation_service,
        "steampunk": LLMFactory.create_steampunk_style_prompt_generation_service,
        "japanese_comic": LLMFactory.create_japanese_comic_style_prompt_generation_service,
        "american_comic": LLMFactory.create_american_comic_style_prompt_generation_service,
        "profession": LLMFactory.create_profession_style_prompt_generation_service,
        "cyberpunk": LLMFactory.create_cyberpunk_style_prompt_generation_service,
        "gothic": LLMFactory.create_gothic_style_prompt_generation_service,
        "realistic": LLMFactory.create_realistic_style_prompt_generation_service,
    }

    style = payload.style
    image_url = str(payload.image_url)
    if style not in style_factory:
        raise HTTPException(status_code=422, detail="无效的风格参数")

    picture_service = LLMFactory.create_picture_analysis_service()
    prompt_service = style_factory[style]()

    async def event_stream():
        try:
            # 1) 图片分析（使用远程图片 URL）
            analysis_parts = []
            async for chunk in picture_service.generate_stream(
                objects=[
                    MessageObjectString.build_text("请描述一下图片中的内容"),
                    MessageObjectString.build_image(file_id=None, file_url=image_url),
                ],
                meta_data=None,
            ):
                if not chunk.startswith("data:"):
                    continue
                content = chunk[len("data: "):].strip()
                if content == "[DONE]":
                    break
                if content:
                    analysis_parts.append(content)
                    yield f"event: analysis\ndata: {content}\n\n"

            analysis_text = "".join(analysis_parts)

            # 2) 生成提示词
            async for sse_chunk in prompt_service.generate_stream(
                objects=[MessageObjectString.build_text(analysis_text)],
                meta_data=None,
            ):
                if not sse_chunk.startswith("data:"):
                    continue
                prompt_content = sse_chunk[len("data: "):].strip()
                if prompt_content == "[DONE]":
                    break
                yield f"event: prompt\ndata: {prompt_content}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: 出错: {str(e)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/3d-generation/submit", response_model=TaskSubmitResponse)
async def submit_3d_generation_task(
    file: UploadFile = File(...),
    current_user = Depends(check_3d_permission),
    service: Tripo3DService = Depends(LLMFactory.create_tripo_3D_image_to_3D_service)
):
    save_path = await save_upload_file(file) # 假设您已将 save_upload_file 提取
    task_id = await service.submit_task(file_path=save_path)
    return {"task_id": task_id}


@app.get("/3d-generation/tasks/{task_id}")
async def get_3d_generation_task_status(
    task_id: str,
    service: Tripo3DService = Depends(LLMFactory.create_tripo_3D_image_to_3D_service)
):
    status = await service.get_task_status(task_id)
    return status


# ========== Sora 文生图接口 ==========

@app.post("/sora/generate")
async def sora_image_generation(
    payload: SoraGenerationRequest,
    # 使用您已有的工厂类来获取服务实例
    service: SoraService = Depends(LLMFactory.create_sora_service)
):
    """
    Sora 文生图接口。
    """
    try:
        # 调用您提供的 SoraService.generate_image 方法
        result = await service.generate_image(
            prompt=payload.prompt,
            model=payload.model,
            n=payload.n,
            size=payload.size,
            is_async=payload.is_async,
            auth_key=payload.auth_key
        )
        return result
    except httpx.HTTPStatusError as e:
        # 如果是外部API的错误，可以更具体地返回
        logger.error(f"Sora upstream API error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code, 
            detail=f"Upstream API error: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"Sora generation failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An internal error occurred during image generation."
        )

@app.get("/sora/tasks/{task_id}")
async def get_sora_task_status(
    task_id: str,
    # 允许通过查询参数提供 auth_key，以匹配您 service 方法的定义
    auth_key: Optional[str] = None,
    service: SoraService = Depends(LLMFactory.create_sora_service)
):
    """
    查询 Sora 异步任务的状态。
    """
    try:
        # 调用您提供的 SoraService.get_task_status 方法
        status = await service.get_task_status(task_id, auth_key=auth_key)
        return status
    except httpx.HTTPStatusError as e:
        logger.error(f"Sora upstream API error while fetching task: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code, 
            detail=f"Upstream API error: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"Failed to get Sora task status for {task_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve task status."
        )
