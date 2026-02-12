"""Agent - LLM 调用和工具执行"""
import json
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from litellm import acompletion
from loguru import logger


class Agent:
    """极简 AI Agent，支持工具调用"""

    def __init__(
        self,
        model: str,
        workspace: Path,
        max_iterations: int = 10,
        shell_timeout: int = 30,
        api_base: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        self.model = model
        self.workspace = workspace
        self.max_iterations = max_iterations
        self.shell_timeout = shell_timeout
        self.api_base = api_base
        self.user_agent = user_agent

        # 检测是否使用自定义 API 端点
        # 参考 nanobot 的实现
        if api_base:
            # 对于使用 OpenAI 兼容接口的自定义端点
            # 使用 openai/ 前缀，这样 LiteLLM 会调用 OpenAI 兼容的路径
            if not any(prefix in model for prefix in ["openai/", "anthropic/", "openrouter/", "gemini/", "zhipu/", "zai/", "groq/", "hosted_vllm/"]):
                self.model = f"openai/{model}"
        logger.info(f"Agent initialized: model={self.model}, workspace={workspace}, api_base={api_base}, user_agent={user_agent}")
    
    async def process(self, user_message: str, history: List[Dict[str, Any]]) -> str:
        """
        处理用户消息，返回响应
        
        Args:
            user_message: 用户消息
            history: 历史对话（OpenAI 格式的 messages）
        
        Returns:
            Agent 的响应文本
        """
        # 构建 messages
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            *history,  # 历史对话
            {"role": "user", "content": user_message}
        ]
        
        # 工具定义
        tools = self._get_tools()
        
        # 迭代调用（支持多次工具调用，类似 ReAct）
        for iteration in range(1, self.max_iterations + 1):
            logger.debug(f"Iteration {iteration}/{self.max_iterations}")
            
            try:
                # 构建 LLM 调用参数
                llm_kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "tools": tools,
                    "tool_choice": "auto"
                }

                # 添加自定义 API base URL
                if self.api_base:
                    llm_kwargs["api_base"] = self.api_base
                    api_key = os.getenv("API_KEY")
                    if not api_key:
                        raise ValueError("API_KEY 环境变量未设置")
                    llm_kwargs["api_key"] = api_key

                # 添加自定义 User-Agent
                if self.user_agent:
                    llm_kwargs["extra_headers"] = {"User-Agent": self.user_agent}

                # 调用 LLM
                response = await acompletion(**llm_kwargs)
                
                msg = response.choices[0].message
                
                # 没有工具调用，返回最终响应
                if not msg.tool_calls:
                    final_response = msg.content or "（无响应内容）"
                    logger.info(f"Final response: {final_response[:100]}...")
                    return final_response
                
                # 有工具调用，执行工具
                logger.info(f"Tool calls: {[tc.function.name for tc in msg.tool_calls]}")
                
                # 添加 assistant 消息（包含 tool_calls）
                messages.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in msg.tool_calls
                    ]
                })
                
                # 执行每个工具
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.function.name

                    # 解析工具参数，增加错误处理
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        error_msg = f"工具参数 JSON 解析失败: {e}"
                        logger.error(error_msg)
                        logger.debug(f"原始参数内容: {tool_call.function.arguments[:500]}...")

                        # 尝试修复常见的转义问题
                        try:
                            # 方法1: 使用 ast.literal_eval（更宽松）
                            import ast
                            tool_args = ast.literal_eval(tool_call.function.arguments)
                            logger.info("使用 ast.literal_eval 成功解析参数")
                        except:
                            # 如果还是失败，返回错误信息
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": f"❌ 参数解析失败: {error_msg}\n\n提示：请确保字符串中的特殊字符正确转义（如 \\ 应写作 \\\\）"
                            })
                            continue

                    logger.debug(f"Executing: {tool_name}({tool_args})")
                    result = self._execute_tool(tool_name, tool_args)
                    
                    # 添加工具结果
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                    
                    logger.debug(f"Tool result: {result[:200]}...")
            
            except Exception as e:
                logger.error(f"Error in iteration {iteration}: {e}")
                return f"处理消息时出错：{str(e)}"
        
        # 达到最大迭代次数
        logger.warning("Reached max iterations")
        return "达到最大处理轮次，任务可能未完成。"
    
    def _get_system_prompt(self) -> str:
        """系统提示词"""
        return f"""你是一个有用的 AI 助手，可以使用工具完成任务。

工作目录: {self.workspace}

你可以：
- 读写文件（路径相对于工作目录）
- 执行 shell 命令（谨慎使用，在工作目录中执行）
- 列出目录内容

规则：
1. 使用工具前先思考
2. 文件操作时检查路径是否合理
3. Shell 命令要安全，避免危险操作（如 rm -rf /）
4. 完成任务后给出清晰的总结
5. **重要**：在工具参数中使用字符串时，确保特殊字符正确转义：
   - 反斜杠 \ 应写作 \\
   - 换行符应使用 \\n（两个反斜杠+n）
   - 引号应使用 \\" 或 \'

当前工作目录是独立的沙盒环境，你可以安全地进行实验。
"""
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        """定义工具（OpenAI function calling 格式）"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "读取文件内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "文件路径（相对于工作目录）"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "写入文件内容（会覆盖已存在的文件）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "文件路径（相对于工作目录）"
                            },
                            "content": {
                                "type": "string",
                                "description": "要写入的内容"
                            }
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_dir",
                    "description": "列出目录内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "目录路径（相对于工作目录，留空表示当前目录）"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "exec_shell",
                    "description": "执行 shell 命令（在工作目录中执行）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "要执行的 shell 命令"
                            }
                        },
                        "required": ["command"]
                    }
                }
            }
        ]
    
    def _execute_tool(self, name: str, args: Dict[str, Any]) -> str:
        """
        执行工具
        
        Args:
            name: 工具名称
            args: 工具参数
        
        Returns:
            工具执行结果（字符串）
        """
        try:
            if name == "read_file":
                path = self.workspace / args["path"]
                if not path.exists():
                    return f"错误：文件不存在 {path}"
                if not path.is_file():
                    return f"错误：{path} 不是文件"
                content = path.read_text(encoding="utf-8")
                return f"文件内容（{len(content)} 字符）：\n{content}"
            
            elif name == "write_file":
                path = self.workspace / args["path"]
                # 创建父目录
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(args["content"], encoding="utf-8")
                return f"✅ 已写入文件：{path.relative_to(self.workspace)}"
            
            elif name == "list_dir":
                dir_path = self.workspace / args.get("path", "")
                if not dir_path.exists():
                    return f"错误：目录不存在 {dir_path}"
                if not dir_path.is_dir():
                    return f"错误：{dir_path} 不是目录"
                
                items = []
                for item in sorted(dir_path.iterdir()):
                    item_type = "📁" if item.is_dir() else "📄"
                    rel_path = item.relative_to(self.workspace)
                    items.append(f"{item_type} {rel_path}")
                
                if not items:
                    return "目录为空"
                return "目录内容：\n" + "\n".join(items)
            
            elif name == "exec_shell":
                command = args["command"]
                
                # 安全检查（简单版）
                dangerous_patterns = ["rm -rf /", "mkfs", "dd if=", "> /dev/"]
                if any(pattern in command for pattern in dangerous_patterns):
                    return f"🚫 拒绝执行危险命令：{command}"
                
                logger.info(f"Executing shell: {command}")
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.workspace,
                    capture_output=True,
                    text=True,
                    timeout=self.shell_timeout
                )
                
                output = result.stdout if result.stdout else result.stderr
                if not output:
                    output = f"命令执行完成（退出码：{result.returncode}）"
                
                return f"Shell 输出：\n{output}"
            
            else:
                return f"❌ 未知工具：{name}"
        
        except subprocess.TimeoutExpired:
            return f"❌ 命令执行超时（{self.shell_timeout}秒）"
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return f"❌ 工具执行失败：{str(e)}"
