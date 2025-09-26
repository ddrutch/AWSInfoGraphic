import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.content_analyzer import create_content_analyzer_agent


async def main():
    agent = create_content_analyzer_agent()
    sample = (
        "Serverless architectures let teams build faster. Key benefits include pay-per-use pricing, automatic scaling, and simplified operations."
    )
    res = await agent.process(sample, platform='twitter')
    print(json.dumps(res, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
