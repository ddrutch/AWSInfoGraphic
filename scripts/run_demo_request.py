import sys, json, os
sys.path.insert(0, r'C:\Users\parkh\OneDrive\Desktop\05i_DEMO_Reinforcement\AWS infographics\AWSInfoGraphic')
from agents.content_analyzer import create_content_analyzer_agent
os.environ['AWSINFOGRAPHIC_DEMO_MODE']='1'
agent = create_content_analyzer_agent()
import asyncio
out = asyncio.run(agent.process('How to accelerate migrations:\n1. Assess workloads\n2. Prioritize critical apps\n3. Automate with CI/CD','general'))
print(json.dumps(out, indent=2))
