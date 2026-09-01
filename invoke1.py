from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
# 从.env文件中加载环境变量
load_dotenv(override=True)

CLOSEAI_API_KEY = os.getenv("API_KEY")
CLOSEAI_BASE_URL = os.getenv("BASE_URL")
model=os.getenv("MODEL")
model = init_chat_model(
    model=model,
    model_provider="openai",
    api_key=CLOSEAI_API_KEY,

    base_url=CLOSEAI_BASE_URL
)
from typing import Optional
from pydantic import BaseModel, Field
class Product(BaseModel):
    """产品信息"""
    name: str = Field(description="产品名称")
    price: float = Field(description="价格")
    description: str = Field(description="产品描述")
    stock: int = Field(default=100, description="库存")

# 测试
structured_llm = model.with_structured_output(Product)
print("\n场景1：完整信息")
result2 = structured_llm.invoke("MacBook Pro 售价 12999 元")
print(result2) 