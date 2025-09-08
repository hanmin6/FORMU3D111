export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

// 获取认证头
const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// --- Helper Functions ---
async function safeText(resp) {
  try { return await resp.text(); } catch { return ''; }
}

function parseSSE(block) {
  const lines = block.split(/\r?\n/);
  let event;
  const dataParts = [];
  for (const line of lines) {
    if (line.startsWith('event:')) {
      event = line.slice(6).trim();
    } else if (line.startsWith('data:')) {
      dataParts.push(line.slice(5).trim());
    }
  }
  return { event, data: dataParts.join('\n') };
}

// --- Image Upload ---
export async function uploadImage(file) {
  const form = new FormData();
  form.append('file', file);
  const resp = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: form,
  });
  if (!resp.ok) {
    const msg = await safeText(resp);
    throw new Error(`上传失败: ${resp.status} ${msg}`);
  }
  return resp.json();
}

// --- Prompt Generation (from File & URL) ---
export async function streamPrompt({ file, style, onAnalysis, onPrompt, onDone }) {
  const form = new FormData();
  form.append('file', file);

  const resp = await fetch(`${API_BASE}/prompt-generation?style=${encodeURIComponent(style)}`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: form,
  });
  if (!resp.ok || !resp.body) {
    const msg = await safeText(resp);
    throw new Error(`生成失败: ${resp.status} ${msg}`);
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let idx;
    while ((idx = buffer.indexOf('\n\n')) !== -1) {
      const rawEvent = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);

      const { event, data } = parseSSE(rawEvent);
      if (data === '[DONE]') {
        onDone?.();
        return;
      }
      if (event === 'analysis') {
        onAnalysis?.(data);
      } else if (event === 'prompt' || event === undefined) {
        onPrompt?.(data);
      }
    }
  }
  onDone?.();
}

export async function streamPromptFromUrl({ imageUrl, style, onAnalysis, onPrompt, onDone }) {
  const resp = await fetch(`${API_BASE}/prompt-generation-url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ style, image_url: imageUrl })
  })
  if (!resp.ok || !resp.body) {
    const msg = await safeText(resp)
    throw new Error(`生成失败: ${resp.status} ${msg}`)
  }
  const reader = resp.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    let idx
    while ((idx = buffer.indexOf('\n\n')) !== -1) {
      const rawEvent = buffer.slice(0, idx)
      buffer = buffer.slice(idx + 2)
      const { event, data } = parseSSE(rawEvent)
      if (data === '[DONE]') { onDone?.(); return }
      if (event === 'analysis') onAnalysis?.(data)
      else if (event === 'prompt' || event === undefined) onPrompt?.(data)
    }
  }
  onDone?.()
}

// --- Sora Text-to-Image ---
export async function generateSoraImage({ prompt, model, n, size, is_async = false }) {
  const payload = { prompt, model, n, size, is_async };
  const resp = await fetch(`${API_BASE}/sora/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!resp.ok) {
    const data = await resp.json().catch(() => ({}));
    const msg = data.detail || await safeText(resp);
    throw new Error(`Sora 生成失败: ${resp.status} ${msg}`);
  }
  return resp.json();
}

export function pollSoraTask({ taskId, onProgress, onSuccess, onError }) {
  const pollInterval = 3000;
  const maxAttempts = 60;
  let attempts = 0;
  const intervalId = setInterval(async () => {
    if (attempts >= maxAttempts) {
      clearInterval(intervalId);
      onError?.({ detail: '任务轮询超时。' });
      return;
    }
    attempts++;
    try {
      const resp = await fetch(`${API_BASE}/sora/tasks/${taskId}`);
      const result = await resp.json();
      if (!resp.ok) {
        clearInterval(intervalId);
        onError?.(result);
        return;
      }
      onProgress?.(result);
      if (result.status === 'succeeded' || result.status === 'failed') {
        clearInterval(intervalId);
        if (result.status === 'succeeded') {
          onSuccess?.(result);
        } else {
          onError?.(result);
        }
      }
    } catch (err) {
      clearInterval(intervalId);
      onError?.({ detail: err.message });
    }
  }, pollInterval);
  return { cancel: () => clearInterval(intervalId) };
}

// --- 3D Model Generation ---
/**
 * Submits an image file and an optional prompt to start the 3D model generation process.
 * @param {File} file The image file to upload.
 * @param {string} [prompt] An optional text prompt.
 * @returns {Promise<{task_id: string}>} An object containing the task ID.
 */
export async function submit3DTask(file, prompt) {
  const form = new FormData();
  form.append('file', file);
  if (prompt) {
    form.append('prompt', prompt);
  }

  const resp = await fetch(`${API_BASE}/3d-generation/submit`, {
    method: 'POST',
    body: form,
  });

  if (!resp.ok) {
    const data = await resp.json().catch(() => ({}));
    const msg = data.detail || await safeText(resp);
    throw new Error(`3D任务提交失败: ${resp.status} ${msg}`);
  }
  return resp.json();
}

/**
 * Polls the status of an asynchronous 3D generation task.
 * @param {object} options - Polling options.
 * @returns {{cancel: () => void}} An object with a function to cancel polling.
 */
export function poll3DTask({ taskId, onProgress, onSuccess, onError }) {
  const pollInterval = 5000;
  const maxAttempts = 120;
  let attempts = 0;

  const intervalId = setInterval(async () => {
    if (attempts >= maxAttempts) {
      clearInterval(intervalId);
      onError?.({ detail: 'Task polling timed out.' });
      return;
    }
    attempts++;
    try {
      const resp = await fetch(`${API_BASE}/3d-generation/tasks/${taskId}`);
      const result = await resp.json();
      if (!resp.ok) {
        clearInterval(intervalId);
        onError?.(result);
        return;
      }
      
      const statusData = result.data || {};
      onProgress?.(statusData);

      if (statusData.status === 'success' || statusData.status === 'failed') {
        clearInterval(intervalId);
        if (statusData.status === 'success') {
          onSuccess?.(result); 
        } else {
          onError?.(statusData);
        }
      }
    } catch (err) {
      clearInterval(intervalId);
      onError?.({ detail: err.message });
    }
  }, pollInterval);

  return { cancel: () => clearInterval(intervalId) };
}

/**
 * 触发浏览器下载给定的图片URL或base64数据。
 * @param {string} imageUrl 图片的来源.
 * @param {string} filename 下载时希望保存的文件名.
 */
export const handleDownload = (imageUrl, filename) => {
  const link = document.createElement('a');
  link.href = imageUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};