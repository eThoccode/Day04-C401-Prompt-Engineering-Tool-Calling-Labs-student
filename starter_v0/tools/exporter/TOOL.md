---
name: exporter
track: custom
kind: local_processing
provider: Local File System
requires_env: []
inputs: [content, filename]
outputs: [filepath, status]
side_effect: true
---
# exporter

Exports markdown report content into a physical file on the local machine under data/exports/ folder.
