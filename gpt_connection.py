from helpers import get_api
from openai import OpenAI

try:
    client = OpenAI(api_key=get_api())
except Exception as e:
    print(e)
    
    
