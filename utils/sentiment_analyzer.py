import anthropic


def analyze_sentiment_batch(api_key: str, texts: list[str]) -> list[dict]:
    """
    Use Claude to analyze sentiment for a batch of customer texts.
    Returns list of dicts with sentiment, score, and key_themes.
    """
    client = anthropic.Anthropic(api_key=api_key)

    sample = texts[:10]
    texts_formatted = "\n".join([f"{i+1}. {t}" for i, t in enumerate(sample)])

    prompt = f"""Analyze the sentiment of these customer interaction transcripts.

{texts_formatted}

For each one, return a JSON array with objects containing:
- index (1-based)
- sentiment: "Positive", "Negative", or "Neutral"
- score: float 0.0 to 1.0 (1.0 = most positive)
- key_theme: the main topic/issue in 3-5 words

Return only valid JSON, no other text."""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    try:
        return json.loads(response.content[0].text)
    except Exception:
        return [{"index": i+1, "sentiment": "Neutral", "score": 0.5, "key_theme": "Unknown"} for i in range(len(sample))]