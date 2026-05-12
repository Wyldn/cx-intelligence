import anthropic
import json


def generate_recommendations(api_key: str, context: dict) -> list[dict]:
    """
    Use Claude to generate actionable recommendations based on CX data context.
    Returns a list of recommendation dicts.
    """
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are a senior Customer Experience strategist. Analyze this CX performance data and generate 5 specific, actionable recommendations.

PERFORMANCE DATA:
- Time Range: {context['time_range']}
- Total Interactions: {context['total_interactions']:,}
- Average Sentiment Score: {context['avg_sentiment']} (scale 0–1)
- Positive Sentiment: {context['positive_pct']}%
- Negative Sentiment: {context['negative_pct']}%
- Web Conversion Rate: {context['conversion_rate']}%
- CSAT Score: {context['csat']}/5
- Net Promoter Score: {context['nps']}
- Active Channels: {', '.join(context['channels'])}
- Customer Segments: {', '.join(context['segments'])}
- Top Drop-off Reasons: {context['top_dropoff']}
- Traffic Sources: {context['top_traffic']}
- Recommendation Focus: {context['focus']}

Generate exactly 5 recommendations. Return ONLY a JSON array with no other text.
Each object must have these exact keys:
- "title": concise recommendation title (max 10 words)
- "priority": "High", "Medium", or "Low"
- "description": 2-3 sentence specific action description
- "impact": specific expected metric improvement (e.g. "↑ Conversion by 18% · ↓ Churn by 12%")

Prioritize based on the focus: {context['focus']}. Be specific and data-driven."""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw.strip())
    except Exception:
        return [{
            "title": "Unable to parse recommendations",
            "priority": "Medium",
            "description": "There was an issue parsing the AI response. Please try again.",
            "impact": "N/A"
        }]