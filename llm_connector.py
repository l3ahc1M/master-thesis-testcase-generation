import openai

class OpenAIConnector:
    def __init__(self):
        """
        Initialize the LLM integration instance.
        If no API key is provided, it uses the one from config.
        """
        self.api_key = "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"
        openai.api_key = self.api_key

    def query(self, system_prompt, user_prompt, **kwargs):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = openai.chat.completions.create(
            model=kwargs.get('model', 'gpt-3.5-turbo'),
            messages=messages,
            max_tokens=kwargs.get('max_tokens', 150),
            temperature=kwargs.get('temperature', 0)
        )

        return response.choices[0].message.content.strip()
