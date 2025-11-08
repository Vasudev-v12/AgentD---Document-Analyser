import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
import textstat
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# from nltk.downloader import DownloadError
import json

try:
    nltk.data.find('tokenizers/punkt')
except Exception:
    nltk.download('punkt')

try:
    nltk.data.find('sentiment/vader_lexicon')
except Exception:
    nltk.download('vader_lexicon')

FOCUS_KEYWORDS = {
    "Business & Finance": [
        "revenue", "profit", "cost", "risk", "efficiency", "compliance",
        "innovation", "market share", "growth", "strategy", "investment", "debt", "earnings"
    ],
    "Policy & Government": [
        "citizen", "community", "public safety", "healthcare", "education", "infrastructure",
        "regulation", "statute", "mandate", "amendment", "judiciary", "freedom", "equality", "taxpayer"
    ],
    "Customer Service & Experience": [
        "love", "great", "fast", "easy", "helpful", "excellent", "satisfied",
        "frustrated", "slow", "rude", "issue", "broken", "shipping", "refund", "account"
    ],
    "Academic & Theory (CSR)": [
        "carbon", "climate", "emissions", "sustainability", "biodiversity",
        "diversity", "inclusion", "equity", "wages", "human rights", "ethics", "accountability"
    ]
}

def perform_quantitative_analysis(doc_list):
    """
    Performs quantitative text analysis on a list of documents.

    Args:
        doc_list (list): A list of strings, where each string is a document.

    Returns:
        str: A JSON formatted string containing the quantitative metrics for each document.
    """
    analyzer = SentimentIntensityAnalyzer()
    results = []

    # Define a set of keywords for a simple frequency analysis (e.g., business focus)
    keywords = ["revenue", "profit", "cost", "risk", "efficiency", "compliance","innovation", "market share", "growth", "strategy", 
                "investment", "debt", "earnings","carbon", "climate", "emissions", "sustainability", "biodiversity",
                "diversity", "inclusion", "equity", "wages", "human rights", "ethics", "accountability","love", "great", "fast", "easy",
                "helpful", "excellent", "satisfied","frustrated", "slow", "rude", "issue", "broken", "shipping", "refund", "account",
                "citizen", "community", "public safety", "healthcare", "education", "infrastructure",
                "regulation", "statute", "mandate", "amendment", "judiciary", "freedom", "equality", "taxpayer"]

    for i, text in enumerate(doc_list):
        # --- 1. Frequency and Length Metrics ---
        word_count = textstat.lexicon_count(text)
        sentence_count = textstat.sentence_count(text)
        
        # Simple Keyword Frequency
        tokens = word_tokenize(text.lower())
        keyword_counts = {kw: tokens.count(kw) for kw in keywords}

        # --- 2. Readability Metrics ---
        # Flesch-Kincaid Grade Level (e.g., US school grade level required to understand)
        fk_grade = textstat.flesch_kincaid_grade(text)
        # Gunning Fog Index (measure of clarity)
        fog_index = textstat.gunning_fog(text)
        
        # --- 3. Sentiment Analysis ---
        vader_scores = analyzer.polarity_scores(text)

        # Compile all metrics for the current document
        doc_metrics = {
            "document_id": i + 1,
            
            # Length and Frequency
            "word_count": word_count,
            "sentence_count": sentence_count,
            "keyword_frequencies": keyword_counts,
            
            # Readability
            "flesch_kincaid_grade": fk_grade,
            "gunning_fog_index": fog_index,
            
            # Sentiment (VADER)
            "sentiment_compound_score": vader_scores['compound'],  # Normalized, most useful score (-1 to +1)
            "sentiment_neg": vader_scores['neg'],
            "sentiment_neu": vader_scores['neu'],
            "sentiment_pos": vader_scores['pos'],
        }
        results.append(doc_metrics)

    # Return the list of dictionaries as a JSON formatted string
    return results

def determine_document_focus(text, keyword_dict):
    """
    Analyzes text to determine the dominant focus area based on keyword frequency.

    Args:
        text (str): The document content.
        keyword_dict (dict): A dictionary mapping focus areas to their keywords.

    Returns:
        dict: A dictionary containing scores and the most likely focus area.
    """
    # Tokenize and normalize the text
    tokens = word_tokenize(text.lower())
    
    focus_scores = {}
    total_keyword_mentions = 0
    
    # Calculate raw score for each focus area
    for focus, keywords in keyword_dict.items():
        score = sum(tokens.count(kw) for kw in keywords)
        focus_scores[focus] = score
        total_keyword_mentions += score

    # Determine the dominant focus and normalize scores
    if total_keyword_mentions == 0:
        dominant_focus = "Undetermined (No keywords found)"
        normalized_scores = {focus: 0.0 for focus in keyword_dict.keys()}
    else:
        dominant_focus = max(focus_scores, key=focus_scores.get)
        normalized_scores = {
            focus: round(score / total_keyword_mentions, 3) 
            for focus, score in focus_scores.items()
        }

    return {
        "analysis_type": "Focus Area Determination",
        "total_relevant_keywords_found": total_keyword_mentions,
        "raw_focus_scores": focus_scores,
        "normalized_focus_scores": normalized_scores,
        "dominant_focus": dominant_focus
    }