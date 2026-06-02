---
name: summarizer
track: custom
kind: local_processing
provider: Python
requires_env: []
inputs: [text, style, max_sentences]
outputs: [summary]
side_effect: false
---
# summarizer

Summarizes long text into a brief summary (bullet points or a single paragraph) using an extractive scoring algorithm.
