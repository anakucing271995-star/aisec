from openai import OpenAI
import os
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

client = OpenAI()

def analyze(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.15,
        max_tokens=900,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content.strip()
