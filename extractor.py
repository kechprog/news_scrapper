from openai import OpenAI

SYSTEM_PROMPT = """
You are a helpful assistant specialized in extracting and converting news articles from webpage screenshots into well-structured Markdown. Your task is to analyze the provided screenshot of a news page and extract only the relevant article content while discarding all website navigation, ads, related articles, and other unrelated elements.

**CRITICAL**: Pay special attention to metadata that appears at the top or bottom of the article:
- Publication date and time (including "last updated" timestamps)
- Publisher/source name
- Author name(s)
- Any timestamps or date information

This metadata is essential as it provides historical context that may not be available elsewhere.

### **Formatting Requirements:**
- Extract the **title** of the article or return `None` if unavailable.
- Extract the **publication date** (including time if visible) or return `None` if unavailable.
- Extract the **last updated date/time** if different from publication date, or return `None` if unavailable.
- Extract the **publisher name** (e.g., CNN, New York Times) or return `None` if unavailable.
- Extract the **author name(s)** or return `None` if unavailable.
- Extract the **main content** while maintaining paragraphs, bullet points, and formatting where appropriate.

### **Strict Extraction Rules:**
- **Do not modify, rephrase, or summarize any text.**
- **Extract only the exact text as it appears in the screenshot.**
- **Preserve the order and structure exactly as in the source.**
- **Do not add any additional content or infer missing details.**
- **If any required field is missing, return `None`.**
- **Carefully scan the entire screenshot for date/time information - it may appear anywhere on the page.**

### **Response Formatting:**
```
# <Title or None>
# <Publication Date or None>
# <Last Updated or None>
# <Publisher Name or None>
# <Author Name or None>

## Content
<Extracted Content>
```
"""

# Nexa AI Server endpoint (OpenAI-compatible)
# Set timeout to 10 minutes for large vision model processing
CLIENT = OpenAI(
    base_url="http://127.0.0.1:18181/v1",
    api_key="not-needed",  # Nexa AI doesn't require a real key, but the client expects one
    timeout=600.0  # 10 minute timeout for vision processing (must be on client, not individual calls)
)

def use_ai(screenshot_b64: str) -> None:
    """
    Sends a screenshot to a vision-capable LLM and extracts article content.
    Uses Qwen3-VL-8B-Thinking model via Nexa SDK server.

    Args:
        screenshot_b64: Base64 encoded PNG screenshot of the full webpage
    """
    try:
        print("\n[API] Sending screenshot to Nexa AI server...")
        print(f"[API] Screenshot size: {len(screenshot_b64)} chars ({len(screenshot_b64)/1024:.1f} KB base64)")
        print(f"[API] Endpoint: http://127.0.0.1:18181/v1")
        print(f"[API] Model: NexaAI/Qwen3-VL-8B-Thinking-GGUF:Q8_0")
        print(f"[API] Max output tokens: 32768 (32K)")
        print(f"[API] Timeout: 600 seconds (10 minutes)")
        print("[API] This may take several minutes for large images...")

        response = CLIENT.chat.completions.create(
            model="NexaAI/Qwen3-VL-8B-Thinking-GGUF:Q8_0",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please analyze this webpage screenshot and extract the article information according to the format specified."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{screenshot_b64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=32768,  # 32K tokens - Qwen3-VL supports up to 40960 for thinking models
            temperature=0.1,  # Low temperature for more consistent extraction
            stream=False  # Disable streaming for simpler response handling
        )
        print("\n[API] ✓ Response received!\n")
        print("=" * 80)
        print(response.choices[0].message.content)
        print("=" * 80)
    except Exception as e:
        print(f"\n[API] ✗ Error calling vision API: {e}")
