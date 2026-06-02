from __future__ import annotations
import os
from pathlib import Path
from typing import Any

def export_to_file(content: str = "", filename: str = "research_report.md") -> dict[str, Any]:
    """Exports markdown content physically to a file on the local machine under data/exports/ folder."""
    try:
        if not content.strip():
            return {"tool": "exporter", "status": "error", "message": "Content is empty"}
            
        # Standardize safe filename
        safe_filename = os.path.basename(filename)
        if not safe_filename.endswith((".md", ".txt")):
            safe_filename += ".md"
            
        # Target exports folder: starter_v0/data/exports/
        export_dir = Path(__file__).resolve().parents[2] / "data" / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = export_dir / safe_filename
        file_path.write_text(content, encoding="utf-8")
        
        return {
            "tool": "exporter",
            "status": "success",
            "filename": safe_filename,
            "filepath": str(file_path.resolve()),
            "message": f"Successfully exported report to {safe_filename}"
        }
    except Exception as exc:
        return {"tool": "exporter", "status": "error", "message": str(exc)}
