"""生成 MiniClaw Logo"""
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 获取 Qwen API Key
qwen_api_key = os.getenv("QWEN_API_KEY")
if not qwen_api_key:
    raise ValueError("需要在 .env 文件中设置 QWEN_API_KEY")

# 导入 DashScope
try:
    from dashscope import ImageSynthesis
except ImportError:
    print("❌ 未安装 dashscope，请运行：pip install dashscope")
    exit(1)

# Logo 设计提示词（中文，Qwen 对中文支持更好）
prompt = """
设计一个可爱的卡通小龙虾logo，需要包含中国元素：
- 小龙虾要圆润可爱，有大大的眼睛和友好的笑容，卡哇伊风格
- 戴着红色的传统中国帽子或者装饰着中国结
- 手持小灯笼或者周围有梅花点缀
- 配色：鲜艳的红橙色小龙虾，金黄色的中国元素装饰
- 简洁的现代扁平化设计，适合作为logo
- 纯色背景或透明背景
- 专业精致的外观

风格：现代扁平化设计，融合中国文化美学，可爱友好，适合科技产品logo
"""

print("🎨 正在使用阿里云 Qwen 生成 MiniClaw Logo...")
print(f"📝 提示词: {prompt[:50]}...")

# 调用 Qwen 图片生成 API
try:
    response = ImageSynthesis.call(
        api_key=qwen_api_key,
        model='qwen-image-plus',  # 使用 qwen-image-plus 模型
        prompt=prompt,
        negative_prompt='',  # 不需要的元素
        size='1024*1024',
        n=1,
        watermark=False,  # 不添加水印
        prompt_extend=True  # 自动优化提示词
    )

    if response.status_code == 200:
        # 获取图片 URL（OSS 链接，24 小时有效）
        image_url = response.output.results[0].url
        print(f"✅ 图片生成成功！")
        print(f"🔗 图片URL: {image_url}")
        print("⏰ 注意：OSS 链接仅 24 小时内有效")

        # 下载图片
        print("📥 正在下载图片...")
        img_data = requests.get(image_url).content

        # 保存到 assets 目录
        output_path = Path(__file__).parent / "assets" / "logo.png"
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(img_data)

        print(f"💾 Logo 已保存到: {output_path}")
        print("🎉 完成！")
    else:
        print(f"❌ 生成失败: {response.code} - {response.message}")

except Exception as e:
    print(f"❌ 生成失败: {e}")
    print("\n💡 提示：")
    print("1. 确保已安装 dashscope：pip install dashscope")
    print("2. 确保在 .env 文件中设置了 QWEN_API_KEY")
    print("3. 检查 API Key 是否有效")
