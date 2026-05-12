import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid

def generate_sample_data(n_days: int, channels: tuple, segments: tuple) -> dict:
    """Generate realistic synthetic customer interaction data."""
    random.seed(42)
    np.random.seed(42)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=n_days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # ── Interactions (Sentiment Source) ──────────────────────────────────────
    n_interactions = n_days * 40
    interaction_dates = [start_date + timedelta(
        days=random.randint(0, n_days),
        hours=random.randint(7, 22),
        minutes=random.randint(0, 59)
    ) for _ in range(n_interactions)]

    channel_list = list(channels) if channels else ['Phone','Chat','Web']
    segment_list = list(segments) if segments else ['Enterprise','SMB','Consumer','Trial']

    # Sentiment scores with channel-specific biases
    channel_biases = {'Phone': -0.05, 'Chat': 0.08, 'Web': 0.02}
    segment_biases = {'Enterprise': 0.06, 'SMB': 0.02, 'Consumer': -0.02, 'Trial': -0.08}

    records = []
    for d in interaction_dates:
        ch = random.choice(channel_list)
        seg = random.choice(segment_list)

        base_score = 0.62
        bias = channel_biases.get(ch, 0) + segment_biases.get(seg, 0)
        score = float(np.clip(np.random.normal(base_score + bias, 0.18), 0.0, 1.0))

        if score >= 0.65:
            sentiment = 'Positive'
        elif score <= 0.35:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'

        csat = float(np.clip(np.random.normal(3.8 + (score - 0.5) * 2, 0.6), 1.0, 5.0))
        nps_raw = float(np.clip(np.random.normal(32 + (score - 0.5) * 80, 20), -100, 100))

        records.append({
            'interaction_id': str(uuid.uuid4())[:8],
            'date': d,
            'channel': ch,
            'segment': seg,
            'sentiment_score': round(score, 3),
            'sentiment': sentiment,
            'csat': round(csat, 1),
            'nps': round(nps_raw, 0),
            'resolution_time_min': round(abs(np.random.normal(14, 8)), 1),
            'agent_id': f"AGT-{random.randint(100,199)}",
        })

    df_interactions = pd.DataFrame(records)

    # ── Customer Journey (Funnel) ─────────────────────────────────────────────
    journey_records = []
    for seg in segment_list:
        awareness = random.randint(1800, 3200)
        consideration = int(awareness * random.uniform(0.55, 0.75))
        intent = int(consideration * random.uniform(0.45, 0.65))
        purchase = int(intent * random.uniform(0.40, 0.60))
        retention = int(purchase * random.uniform(0.70, 0.85))

        journey_records.append({
            'segment': seg,
            'awareness': awareness,
            'consideration': consideration,
            'intent': intent,
            'purchase': purchase,
            'retention': retention,
        })
    df_journey = pd.DataFrame(journey_records)

    # ── Web Analytics ─────────────────────────────────────────────────────────
    n_sessions = n_days * 200
    web_records = []
    traffic_sources = ['Organic Search','Paid Search','Social Media','Direct','Email','Referral']
    source_weights = [0.38, 0.24, 0.18, 0.12, 0.05, 0.03]
    pages = ['/home','/pricing','/features','/demo','/blog','/contact','/signup']

    for _ in range(n_sessions):
        seg = random.choice(segment_list)
        src = random.choices(traffic_sources, weights=source_weights)[0]
        pages_viewed = max(1, int(np.random.exponential(2.5)))
        time_on_site = max(0.1, float(np.random.exponential(3.2)))
        bounced = pages_viewed == 1
        conv_prob = 0.04 + (pages_viewed * 0.02) + (time_on_site * 0.01)
        if src == 'Email': conv_prob += 0.05
        if src == 'Paid Search': conv_prob += 0.03
        converted = random.random() < min(conv_prob, 0.35)

        web_records.append({
            'session_id': str(uuid.uuid4())[:8],
            'date': start_date + timedelta(days=random.randint(0, n_days)),
            'segment': seg,
            'source': src,
            'pages_viewed': pages_viewed,
            'time_on_site': round(time_on_site, 2),
            'bounced': bounced,
            'converted': converted,
            'landing_page': random.choice(pages),
        })

    df_web = pd.DataFrame(web_records)
    df_web['date'] = pd.to_datetime(df_web['date']).dt.date

    return {
        'interactions': df_interactions,
        'journey': df_journey,
        'web': df_web,
    }