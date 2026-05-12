import pandas as pd


def map_customer_journeys(df_interactions: pd.DataFrame, df_web: pd.DataFrame) -> dict:
    """
    Map customer journeys across channels.
    Returns summary metrics per segment and common path sequences.
    """
    journey_summary = {}

    for segment in df_interactions['segment'].unique():
        seg_int = df_interactions[df_interactions['segment'] == segment]
        seg_web = df_web[df_web['segment'] == segment]

        avg_sentiment = seg_int['sentiment_score'].mean()
        positive_rate = (seg_int['sentiment'] == 'Positive').mean()
        avg_csat = seg_int['csat'].mean()
        avg_nps = seg_int['nps'].mean()
        web_conversion = seg_web['converted'].mean() if len(seg_web) > 0 else 0
        avg_pages = seg_web['pages_viewed'].mean() if len(seg_web) > 0 else 0

        journey_summary[segment] = {
            'avg_sentiment': round(float(avg_sentiment), 3),
            'positive_rate': round(float(positive_rate), 3),
            'avg_csat': round(float(avg_csat), 2),
            'avg_nps': round(float(avg_nps), 1),
            'web_conversion': round(float(web_conversion), 3),
            'avg_pages_per_session': round(float(avg_pages), 1),
            'total_interactions': len(seg_int),
            'total_sessions': len(seg_web),
        }

    return journey_summary