#!/usr/bin/env python3
"""
Скрипт для запуска backend сервера.
"""
import sys
import os
from pathlib import Path

# Добавляем src в path
sys.path.insert(0, str(Path(__file__).parent / "src"))

if __name__ == "__main__":
    import uvicorn
    from src.main import app
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"]
    )
