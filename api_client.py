from openai import OpenAI
import anthropic
from config import Config

class APIClient:
    def __init__(self):
        Config.validate_config()
        self.provider = Config.API_PROVIDER
        
        if self.provider == 'anthropic':
            self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        else:  # openai
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def generate_response(self, prompt):
        if self.provider == 'anthropic':
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        else:  # openai
            response = self.client.chat.completions.create(
                model="gpt-4o",  # or your preferred model
                messages=[
                    {"role": "system", "content": "You are an ontology engineering assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
            )
            return response.choices[0].message.content