import os
import ssl
import httpx
import base64
from datetime import datetime
from typing import Optional, List, Any, Dict
from pathlib import Path
import sys 


current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.append(str(project_root))

from app.core.railway_config import RailwayConfig


LOG_FILE = 'image_log.txt'

class SoraService:
    def __init__(self):
        self.api_key = RailwayConfig.get_sora_api_key()
        # 存储并规范化 base_url，去除末尾的斜杠
        base_url = RailwayConfig.get_sora_base_url()
        self.api_base_url = base_url.rstrip('/') if base_url else None
        
        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
        self._client = httpx.AsyncClient(verify=ssl_context, timeout=300)

    async def close(self):
        await self._client.aclose()

    def _get_effective_auth_key(self, provided_key: Optional[str]) -> str:
        return provided_key if provided_key else self.api_key

    async def _make_api_request(self, api_url: str, auth_key: str, data: Dict[str, Any], files: Optional[Dict] = None, is_async: bool = False) -> Dict:
        headers = {'Authorization': f'{auth_key}'}
        params = {'async': 'true'} if is_async else None
        print(f"\n--- Sending API Request via SoraService ---\nURL: {api_url}\nParams: {params}\nData: {data}\n")
        
        if files:
            response = await self._client.post(api_url, headers=headers, data=data, files=files, params=params)
        else:
            response = await self._client.post(api_url, headers=headers, json=data, params=params)
        
        response.raise_for_status()
        return response.json()

    async def generate_image(self, prompt: str, model: str, n: int, size: str, is_async: bool, auth_key: Optional[str] = None) -> Dict:
        """使用内部的 base_url 构建请求 URL"""
        effective_auth_key = self._get_effective_auth_key(auth_key)
        # 内部构建完整的 API URL
        full_url = f"{self.api_base_url}/v1/images/generations"
        payload = {'model': model, 'prompt': prompt, 'n': n, 'size': size}
        
        result = await self._make_api_request(full_url, effective_auth_key, payload, is_async=is_async)
        
        if not is_async and result.get('data'):
            self.log_image_id(result.get('id'), prompt)
            await self.save_images_from_data(result['data'], prompt)
            
        return result

    async def edit_image(self, prompt: str, image_bytes: bytes, image_filename: str, model: str, n: int, size: str, is_async: bool, auth_key: Optional[str] = None, mask_bytes: Optional[bytes] = None, mask_filename: Optional[str] = None) -> Dict:
        """使用内部的 base_url 构建请求 URL"""
        effective_auth_key = self._get_effective_auth_key(auth_key)
        # 内部构建完整的 API URL
        full_url = f"{self.api_base_url}/v1/images/edits"
        data = {'prompt': prompt, 'model': model, 'size': size, 'n': n}
        files = {'image': (image_filename, image_bytes)}
        if mask_bytes and mask_filename:
            files['mask'] = (mask_filename, mask_bytes)

        result = await self._make_api_request(full_url, effective_auth_key, data, files=files, is_async=is_async)

        if not is_async and result.get('data'):
            self.log_image_id(result.get('id'), prompt)
            await self.save_images_from_data(result['data'], prompt)

        return result

    async def get_task_status(self, task_id: str, auth_key: Optional[str] = None) -> Dict:
        """使用内部的 base_url 构建请求 URL"""
        effective_auth_key = self._get_effective_auth_key(auth_key)
        # 内部构建完整的任务 URL
        task_url = f"{self.api_base_url}/v1/images/tasks/{task_id}"
        headers = {'Authorization': f'Bearer {effective_auth_key}'}
        
        response = await self._client.get(task_url, headers=headers)
        response.raise_for_status()
        return response.json()

    def log_image_id(self, task_id: str, prompt: str):
        """Logs the task ID and prompt to a file."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sanitized_prompt = ' '.join(prompt.split())
            log_entry = f"{timestamp} - ID: {task_id} - Prompt: {sanitized_prompt}\n"
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing to log file: {e}")

    async def save_images_from_data(self, data_list: List[Dict[str, Any]], prompt: str):
        """Decodes or downloads and saves images from API response data."""
        output_dir = 'outputs'
        os.makedirs(output_dir, exist_ok=True)
        
        for i, item in enumerate(data_list):
            img_data = None
            if item.get('b64_json'):
                try:
                    img_data = base64.b64decode(item['b64_json'])
                except Exception as e:
                    print(f"Error decoding base64 image: {e}")
                    continue
            elif item.get('url'):
                try:
                    print(f"Downloading image from URL: {item['url']}")
                    # Use the service's client for async download
                    img_response = await self._client.get(item['url'], timeout=60)
                    img_response.raise_for_status()
                    img_data = img_response.content
                except Exception as e:
                    print(f"Error downloading image from URL {item['url']}: {e}")
                    continue

            if img_data:
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_prompt = "".join([c for c in prompt if c.isalnum() or c in (' ', '-')]).rstrip()[:30].replace(' ', '_')
                    filename = f"{timestamp}_{safe_prompt}_{i+1}.png"
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(img_data)
                    print(f"Image saved to {filepath}")
                except Exception as e:
                    print(f"Error saving image file: {e}")