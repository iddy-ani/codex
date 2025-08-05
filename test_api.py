from openai import AzureOpenAI
import json
import traceback

combined_history = []
OPENAI_API_KEY = "1ec57c7402ed46ecbae6b09b12cb0e3c"
azure_openai = AzureOpenAI(
    # azure_ad_token_provider=token_provider,
    azure_endpoint="https://appi-gpt4.openai.azure.com/",
    api_key=OPENAI_API_KEY,
    api_version="2025-04-01-preview"
)

model_descriptions = {
                "o3": "O3 - Flagship multimodal reasoning model, excellent for complex coding tasks",
                "o3-mini": "O3 Mini - Cost-effective reasoning model, 90% cheaper than O3",
                "o3-pro": "O3-Pro - Maximum reasoning power for complex problems",
                "gpt-4.1-nano": "GPT-4.1 Nano - Ultra-fast, sub-second latency for simple tasks", 
                "gpt-4.1-mini": "GPT-4.1 Mini - Balanced speed and quality, 26% cheaper than GPT-4o",
                "gpt-4.1": "GPT-4.1 - Latest flagship with 1M token context, excellent for code diffs",
                "codex-mini": "Codex Mini - Specialized for code completion and generation",
                "gpt-4o": "GPT-4o - Real-time multimodal model with low latency", 
                "gpt-4": "GPT-4 Turbo - High-quality model with vision capabilities",
                "gpt-4-32k": "GPT-4 32k - Large context variant for long documents",
                "o1": "O1 - Advanced reasoning model for complex STEM and coding",
                "gpt-4.5-preview": "GPT-4.5 Preview - Research preview bridging GPT-4 to GPT-5",
                "gpt-35-turbo": "GPT-3.5 Turbo - Fast, cost-effective model for lightweight tasks"
            }

model = "o3"
def process_message(system_message, combined_history):
    try:
        msg = [system_message] + combined_history

        # Pick the right Azure client (your existing logic)

        # ─── SPECIAL CASE: o3-pro  (uses Responses API) ─────────────────────
        if model in ["o3-pro", "codex-mini"]:
            request_params = {
                "input": msg,      # Responses API expects 'input'
                "model": model,
            }
            response = azure_openai.responses.create(**request_params)

            # ---- pull the assistant text out of the Response object -------
            text_content = ""
            tool_call_items = []

            # The final consolidated result lives in response.output
            # Iterate through it to collect message text and any tool calls
            if getattr(response, "output", None):
                for item in response.output:
                    if getattr(item, "type", "") == "message":
                        for part in getattr(item, "content", []):
                            if getattr(part, "type", "") == "output_text":
                                text_content += (part.text or "")
                    elif getattr(item, "type", "") == "tool_call":
                        tool_call_items.append(item)

            # Return text if present
            if text_content:
                return text_content

            # Otherwise return tool-call payload if that’s what we got
            if tool_call_items:
                tool_calls_serialized = json.loads(json.dumps(
                    tool_call_items, default=lambda o: o.__dict__
                ))
                return [tool_calls_serialized, {}]  # second element just a stub

            # Fallback
            return "No response from the model."

        # ─── EVERY OTHER MODEL: Chat-Completions (unchanged) ───────────────
        request_params = {
            "messages": msg,
            "model": model,
        }
        if model not in ['o1', 'o3-mini', 'o3', 'o3-pro', "codex-mini"]:
            request_params["max_tokens"]   = 4096
            request_params["top_p"]        = 0.9
            request_params["temperature"]  = 0.7


        response = azure_openai.chat.completions.create(**request_params)

        # ‣ Standard content / tool-call extraction (your original code)
        if hasattr(response.choices[0].message, 'content') and response.choices[0].message.content:
            return response.choices[0].message.content

        elif hasattr(response.choices[0].message, 'tool_calls'):
            tool_calls_serialized = json.loads(json.dumps(
                response.choices[0].message.tool_calls,
                default=lambda o: o.__dict__
            ))
            tool_info_serialized = json.loads(json.dumps(
                response.choices[0].message,
                default=lambda o: o.__dict__
            ))
            return [tool_calls_serialized, tool_info_serialized]

        else:
            return "No response from the model."

    except Exception as e:
        print(f"Unexpected {traceback.format_exc()}, {type(e)=}")
        return str({traceback.format_exc()})
    
if __name__ == "__main__":
    system_message = {"role": "system", "content": "You are a helpful assistant."}
    prompt = {"role": "user", "content": "hello"}
    combined_history = combined_history + [prompt]

    response = process_message(system_message, combined_history)
    combined_history = combined_history + [response]
    print(response)