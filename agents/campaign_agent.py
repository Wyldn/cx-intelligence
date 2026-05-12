import anthropic
import json


def generate_campaign(api_key: str, context: dict) -> list[dict]:
    """
    Use Claude to generate targeted advertising campaign strategies.
    Returns a list of campaign dicts.
    """
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are a performance marketing director. Based on this CX data, design 3 targeted advertising campaigns to improve engagement and conversion.

CONTEXT:
- Customer Segments: {', '.join(context['segments'])}
- Channels: {', '.join(context['channels'])}
- Conversion Rate: {context['conversion_rate']}%
- NPS: {context['nps']}
- Negative Sentiment: {context['negative_pct']}%
- Top Traffic Sources: {context['top_traffic']}
- Primary Drop-off: {context['top_dropoff']}
- Budget Tier: {context['budget_tier']}
- Strategic Focus: {context['focus']}

Design 3 campaigns. Return ONLY a valid JSON array, no other text or markdown.
Each campaign object must have exactly these keys:
- "name": campaign name (creative, max 8 words)
- "tags": array of 3-4 short tags (channel type, format, goal)
- "description": 3-4 sentence campaign brief with specific tactics, creative angle, and messaging strategy
- "target": target audience description
- "channel": primary distribution channel(s)
- "roi": estimated ROI range (e.g. "2.8x–4.1x")

Make the campaigns specific, creative, and tied to the actual data insights."""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw.strip())
    except Exception:
        return [{
            "name": "Campaign generation error",
            "tags": ["ERROR"],
            "description": "Unable to parse campaign data. Please try again.",
            "target": "N/A",
            "channel": "N/A",
            "roi": "N/A"
        }]