"""
NVIDIA API service for AI chat
"""
import httpx
from typing import List, Dict, Optional, AsyncGenerator
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class NVIDIAAPIService:
    """Service for interacting with NVIDIA API"""

    def __init__(self):
        self.api_key = settings.nvidia_api_key
        self.base_url = settings.nvidia_api_base_url
        self.default_model = settings.default_model

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> AsyncGenerator[str, None]:
        """
        Send a chat completion request to NVIDIA API

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model ID (uses default if not specified)
            stream: Whether to stream the response
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            str: Response chunks if streaming
        """
        if not model:
            model = self.default_model

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                if stream:
                    async with client.stream(
                        "POST",
                        self.base_url,
                        headers=headers,
                        json=payload
                    ) as response:
                        if response.status_code != 200:
                            error_text = await response.aread()
                            logger.error(f"NVIDIA API error: {error_text}")
                            yield f"Error: API returned status {response.status_code}"
                            return

                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data = line[6:]  # Remove "data: " prefix
                                if data == "[DONE]":
                                    break
                                try:
                                    import json
                                    chunk = json.loads(data)
                                    if "choices" in chunk and len(chunk["choices"]) > 0:
                                        delta = chunk["choices"][0].get("delta", {})
                                        content = delta.get("content", "")
                                        if content:
                                            yield content
                                except json.JSONDecodeError:
                                    continue
                else:
                    response = await client.post(
                        self.base_url,
                        headers=headers,
                        json=payload
                    )

                    if response.status_code != 200:
                        error_text = response.text
                        logger.error(f"NVIDIA API error: {error_text}")
                        yield f"Error: API returned status {response.status_code}"
                        return

                    data = response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0]["message"]["content"]
                        yield content
                    else:
                        yield "Error: No response content"

        except httpx.TimeoutException:
            logger.error("NVIDIA API timeout")
            yield "Error: Request timeout"
        except Exception as e:
            logger.error(f"NVIDIA API error: {str(e)}")
            yield f"Error: {str(e)}"

    async def generate_summary(self, conversation_messages: List[Dict[str, str]]) -> str:
        """
        Generate a summary of a conversation

        Args:
            conversation_messages: List of conversation messages

        Returns:
            str: Generated summary
        """
        summary_prompt = [
            {
                "role": "system",
                "content": "你是一个专业的文档整理助手。请根据以下对话内容，生成一个简洁、准确的摘要（不超过200字）。"
            },
            {
                "role": "user",
                "content": f"请为以下对话生成摘要：\n\n" + "\n".join([
                    f"{msg['role']}: {msg['content']}"
                    for msg in conversation_messages[-10:]  # Last 10 messages
                ])
            }
        ]

        response_text = ""
        async for chunk in self.chat(summary_prompt, stream=False):
            response_text += chunk

        return response_text.strip()

    async def generate_document(
        self,
        conversation_messages: List[Dict[str, str]],
        title: str
    ) -> str:
        """
        Generate a structured document from a conversation

        Args:
            conversation_messages: List of conversation messages
            title: Document title

        Returns:
            str: Generated document content in Markdown format
        """
        document_prompt = [
            {
                "role": "system",
                "content": """你是一个专业的文档编写助手。请将对话内容整理成结构清晰的 Markdown 文档。
文档格式要求：
# 标题

## 概述
简要概述对话主题

## 主要内容
- 要点1
- 要点2
- 要点3

## 结论
总结对话的结论或行动计划

## 备注
其他需要记录的信息"""
            },
            {
                "role": "user",
                "content": f"请将以下对话整理成标题为\"{title}\"的文档：\n\n" + "\n".join([
                    f"{msg['role']}: {msg['content']}"
                    for msg in conversation_messages
                ])
            }
        ]

        response_text = ""
        async for chunk in self.chat(document_prompt, stream=False):
            response_text += chunk

        return response_text.strip()

    async def suggest_tags(self, content: str) -> List[str]:
        """
        Suggest tags for document content

        Args:
            content: Document or conversation content

        Returns:
            List[str]: Suggested tags
        """
        tag_prompt = [
            {
                "role": "system",
                "content": "你是一个标签建议助手。请根据内容建议3-5个相关标签，每个标签2-4个字，用逗号分隔。只返回标签，不要其他内容。"
            },
            {
                "role": "user",
                "content": f"为以下内容建议标签：\n\n{content[:1000]}"
            }
        ]

        response_text = ""
        async for chunk in self.chat(tag_prompt, stream=False):
            response_text += chunk

        # Parse tags from response
        tags = [tag.strip() for tag in response_text.split(",") if tag.strip()]
        return tags[:5]  # Return max 5 tags


# Global NVIDIA API service instance
nvidia_service = NVIDIAAPIService()
