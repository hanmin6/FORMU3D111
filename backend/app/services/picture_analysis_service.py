import os
import sys
import asyncio
import uuid  # 添加uuid模块导入
from pathlib import Path
from typing import List, Dict, Optional, AsyncGenerator
from cozepy import AsyncCoze, TokenAuth, Message, ChatEventType, MessageObjectString

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.append(str(project_root))

from app.core.railway_config import RailwayConfig

class PictureAnalysisService:
    '''异步的Coze服务类'''
    
    def __init__(self):
        self.user_id = uuid.uuid4().hex
        self._coze = None  # 延迟初始化
    
    async def _get_coze_client(self):
        """获取 Coze 客户端，延迟初始化"""
        if self._coze is None:
            base_url = RailwayConfig.get_coze_base_url()
            authorization = RailwayConfig.get_coze_authorization()
            bot_id = RailwayConfig.get_bot_id("PICTURE_ANALYSIS")
            
            if not all([base_url, authorization, bot_id]):
                raise ValueError(f"缺少必要的 Coze 配置: base_url={bool(base_url)}, auth={bool(authorization)}, bot_id={bool(bot_id)}")
            
            self.base_url = base_url
            self.authorization = authorization
            self.bot_id = bot_id
            
            # 使用异步Coze客户端替代同步客户端
            self._coze = AsyncCoze(
                auth=TokenAuth(token=self.authorization), 
                base_url=self.base_url
            )
        return self._coze
    
    async def upload_local_image(self, file_path: str) -> str:
        """
        上传本地图片并返回file_id
        
        Args:
            file_path: 本地图片文件路径
            
        Returns:
            上传成功后的file_id
            
        Raises:
            RuntimeError: 上传失败时抛出异常
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"图片文件不存在: {file_path}")
            
            # 检查文件格式是否为图片
            valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in valid_extensions:
                raise ValueError(f"不支持的图片格式: {ext}，仅支持{valid_extensions}")
            
            # 获取 Coze 客户端
            coze = await self._get_coze_client()
            
            loop = asyncio.get_event_loop()
            
            # 同步读取文件内容的函数
            def sync_read_file():
                with open(file_path, 'rb') as f:
                    return f.read()
            
            # 通过线程池执行同步读取
            file_content = await loop.run_in_executor(None, sync_read_file)
            
            # 上传文件内容
            response = await coze.files.upload(
                file=file_content  # 传递文件内容字节流
            )
            
            
            return response.id
            
        except Exception as e:
            raise RuntimeError(f"图片上传失败: {str(e)}")
    
    async def generate_stream(
        self, 
        objects: List[MessageObjectString], 
        meta_data: Optional[Dict[str, str]] = None
    ) -> AsyncGenerator[str, None]:
        try:
            # 获取 Coze 客户端
            coze = await self._get_coze_client()
            
            user_message = Message.build_user_question_objects(
                objects=objects, 
                meta_data=meta_data
            )
            
            # 直接调用异步stream方法，返回异步生成器
            async for event in coze.chat.stream(
                bot_id=self.bot_id,
                user_id=self.user_id,
                additional_messages=[user_message],
            ):
                if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                    # 添加空内容过滤
                    if event.message.content.strip():
                        yield f"data: {event.message.content}\n\n"
                elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                    print(f"Token使用量: {event.chat.usage.token_count}")
                    # 添加结束信号
                    yield "data: [DONE]\n\n"
                    break
                elif event.event == ChatEventType.ERROR:
                    raise Exception(f"Coze API错误: {event.error}")
                    
        except Exception as e:
            raise RuntimeError(f"调用Coze服务失败: {str(e)}")