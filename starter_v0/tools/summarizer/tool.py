from __future__ import annotations
import re
from collections import Counter
from typing import Any

def summarize_text(text: str = "", style: str = "bullets", max_sentences: int = 5) -> dict[str, Any]:
    """Summarizes a long piece of text into a concise summary using an extractive algorithm."""
    try:
        if not text.strip():
            return {"tool": "summarizer", "status": "success", "summary": ""}
            
        # Split text into sentences using regex
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= max_sentences:
            selected_sentences = sentences
        else:
            # Simple extractive scoring based on word frequencies
            words = re.findall(r'\b\w{4,}\b', text.lower())
            word_freq = Counter(words)
            
            sentence_scores = []
            for index, sentence in enumerate(sentences):
                score = 0
                sentence_words = re.findall(r'\b\w{4,}\b', sentence.lower())
                for word in sentence_words:
                    score += word_freq.get(word, 0)
                # Lead bias boost: first sentences usually hold more value
                lead_boost = max(0, 10 - index) * 2
                sentence_scores.append((score + lead_boost, index, sentence))
            
            # Sort by score desc, pick top, then sort by original order
            sentence_scores.sort(key=lambda x: x[0], reverse=True)
            top_sentences = sentence_scores[:max_sentences]
            top_sentences.sort(key=lambda x: x[1])
            selected_sentences = [item[2] for item in top_sentences]
            
        if style == "bullets":
            summary = "\n".join(f"- {s}" for s in selected_sentences)
        else:
            summary = " ".join(selected_sentences)
            
        return {
            "tool": "summarizer",
            "status": "success",
            "summary": summary
        }
    except Exception as exc:
        return {"tool": "summarizer", "status": "error", "message": str(exc)}
