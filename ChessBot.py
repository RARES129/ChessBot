import os

from openai import OpenAI
from dotenv import load_dotenv


class ChessBot:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('API_KEY')
        self.client = OpenAI(api_key=api_key)
        self.exit_condition = ['close', 'exit']

    def answer_question(self, inpt):
        if inpt in self.exit_condition:
            return "Goodbye!"

        if inpt[-1] != '?':
            inpt += '?'

        response = self.client.chat.completions.create(
            model="ft:gpt-3.5-turbo-1106:personal::8XuB9Rp8",
            messages=[
                {
                    "role": "user",
                    "content": inpt
                }
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        return response.choices[0].message.content
