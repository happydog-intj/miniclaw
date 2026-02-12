"""Telegram Bot - 消息监听和路由"""
import json
import asyncio
from pathlib import Path
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from loguru import logger

from agent import Agent
import config


class TelegramBot:
    """Telegram Bot 封装"""
    
    def __init__(self):
        self.agent = Agent(
            model=config.LLM_MODEL,
            workspace=config.WORKSPACE,
            max_iterations=config.MAX_ITERATIONS,
            shell_timeout=config.SHELL_TIMEOUT,
            api_base=config.BASE_URL,
            user_agent=config.CUSTOM_USER_AGENT
        )
        logger.info("TelegramBot initialized")
    
    def _get_session_file(self, chat_id: int) -> Path:
        """获取会话文件路径"""
        return config.SESSION_DIR / f"{chat_id}.json"
    
    def _load_history(self, chat_id: int) -> list:
        """加载会话历史"""
        session_file = self._get_session_file(chat_id)
        if session_file.exists():
            try:
                history = json.loads(session_file.read_text(encoding="utf-8"))
                logger.debug(f"Loaded history for {chat_id}: {len(history)} messages")
                return history
            except Exception as e:
                logger.error(f"Failed to load history for {chat_id}: {e}")
                return []
        return []
    
    def _save_history(self, chat_id: int, history: list):
        """保存会话历史"""
        session_file = self._get_session_file(chat_id)
        try:
            session_file.write_text(
                json.dumps(history, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            logger.debug(f"Saved history for {chat_id}: {len(history)} messages")
        except Exception as e:
            logger.error(f"Failed to save history for {chat_id}: {e}")
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        chat_id = update.effective_chat.id
        welcome_msg = (
            "👋 你好！我是一个极简版的 AI 助手。\n\n"
            "我可以：\n"
            "📁 读写文件\n"
            "💻 执行命令\n"
            "🤔 回答问题\n\n"
            "直接发消息给我吧！\n\n"
            "命令：\n"
            "/start - 显示欢迎消息\n"
            "/clear - 清空对话历史\n"
            "/status - 查看状态"
        )
        await update.message.reply_text(welcome_msg)
        logger.info(f"User {chat_id} started the bot")
    
    async def handle_clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /clear 命令（清空历史）"""
        chat_id = update.effective_chat.id
        session_file = self._get_session_file(chat_id)
        
        if session_file.exists():
            session_file.unlink()
            await update.message.reply_text("✅ 已清空对话历史")
            logger.info(f"Cleared history for {chat_id}")
        else:
            await update.message.reply_text("ℹ️ 没有对话历史")
    
    async def handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /status 命令"""
        chat_id = update.effective_chat.id
        history = self._load_history(chat_id)
        
        # 统计消息数
        user_msgs = len([m for m in history if m.get("role") == "user"])
        assistant_msgs = len([m for m in history if m.get("role") == "assistant"])
        
        status_msg = (
            f"📊 状态信息\n\n"
            f"🆔 Chat ID: {chat_id}\n"
            f"🤖 模型: {config.LLM_MODEL}\n"
            f"💬 历史消息: {len(history)} 条\n"
            f"  - 用户: {user_msgs} 条\n"
            f"  - 助手: {assistant_msgs} 条\n"
            f"📂 工作目录: {config.WORKSPACE}\n"
            f"🔧 最大迭代: {config.MAX_ITERATIONS}"
        )
        await update.message.reply_text(status_msg)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理普通消息"""
        chat_id = update.effective_chat.id
        user_text = update.message.text
        
        logger.info(f"Received message from {chat_id}: {user_text[:50]}...")
        
        # 发送"正在输入"状态
        await update.message.chat.send_action("typing")
        
        try:
            # 加载历史
            history = self._load_history(chat_id)
            
            # 调用 agent 处理
            response = await self.agent.process(user_text, history)
            
            # 保存历史
            history.append({"role": "user", "content": user_text})
            history.append({"role": "assistant", "content": response})
            self._save_history(chat_id, history)
            
            # 发送响应（处理长消息）
            await self._send_response(update, response)
            
            logger.info(f"Sent response to {chat_id}: {response[:50]}...")
        
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text(f"❌ 处理消息时出错：{str(e)}")
    
    async def _send_response(self, update: Update, text: str):
        """发送响应（处理 Telegram 4096 字符限制）"""
        MAX_LENGTH = 4096
        
        if len(text) <= MAX_LENGTH:
            await update.message.reply_text(text)
        else:
            # 分段发送
            chunks = [text[i:i+MAX_LENGTH] for i in range(0, len(text), MAX_LENGTH)]
            for i, chunk in enumerate(chunks, 1):
                prefix = f"📄 {i}/{len(chunks)}\n\n" if len(chunks) > 1 else ""
                await update.message.reply_text(prefix + chunk)
                await asyncio.sleep(0.5)  # 避免速率限制
    
    def run(self):
        """启动 Bot"""
        logger.info("Starting Telegram bot...")
        
        # 创建 Application
        app = Application.builder().token(config.TELEGRAM_TOKEN).build()
        
        # 注册处理器
        app.add_handler(CommandHandler("start", self.handle_start))
        app.add_handler(CommandHandler("clear", self.handle_clear))
        app.add_handler(CommandHandler("status", self.handle_status))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # 启动轮询
        logger.info(f"Bot is running (model: {config.LLM_MODEL})")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """入口函数"""
    logger.info("=" * 50)
    logger.info("MiniClaw - 极简版 AI 助手")
    logger.info("=" * 50)
    
    bot = TelegramBot()
    bot.run()


if __name__ == "__main__":
    main()
