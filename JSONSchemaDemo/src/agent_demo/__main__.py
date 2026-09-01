import asyncio
import json

from agent_demo.app import create_demo_app


async def main() -> None:
    run = await create_demo_app().run(
        user_query="帮我找附近评分高的川菜，两个人吃，最好有套餐。",
        lat=31.2304,
        lng=121.4737,
    )
    print(json.dumps(run.response.model_dump(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
