#!/usr/bin/env python3
"""
FastAPI Server for Trading Bot
===============================
Run this to start the API server
"""

import uvicorn
from trader.api.main import app

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 STARTING TRADING BOT API SERVER")
    print("="*70)
    print("\n📍 Server will be available at:")
    print("   • API: http://localhost:8000")
    print("   • Docs: http://localhost:8000/docs")
    print("   • ReDoc: http://localhost:8000/redoc")
    print("\n💡 Press Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    uvicorn.run(
        "trader.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
