import openai
import time

class OpenAIAssistantConnector:
    def __init__(self):
        self.api_key = "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"
        openai.api_key = self.api_key

    def query_with_file(self, system_prompt, user_prompt, file_path, model="gpt-40-mini"):
        try:
            # Upload the file for file_search tool
            with open(file_path, "rb") as f:
                uploaded_file = openai.files.create(file=f, purpose="assistants")

            # Create assistant with file_search tool (NO file_ids)
            assistant = openai.beta.assistants.create(
                name="TestCaseGenerator",
                instructions=system_prompt,
                model=model,
                tools=[{"type": "file_search"}]
            )

            # Create a thread
            thread = openai.beta.threads.create()

            # Post user message
            openai.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_prompt
            )

            # Start the run — no file_ids passed here either
            run = openai.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id,
                temperature=0
            )

            # Wait for run to complete
            while run.status not in ["completed", "failed"]:
                time.sleep(1)
                run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            if run.status == "failed":
                raise RuntimeError("Assistant run failed")

            # Fetch and return result
            messages = openai.beta.threads.messages.list(thread_id=thread.id)
            return messages.data[0].content[0].text.value

        except Exception as e:
            raise RuntimeError(f"Failed to query assistant API: {e}")
