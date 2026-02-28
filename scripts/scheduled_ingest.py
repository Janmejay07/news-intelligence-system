#!/usr/bin/env python3
"""Scheduled news ingestion - run periodically (e.g., via cron or Task Scheduler)."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.ingest import main

if __name__ == "__main__":
    asyncio.run(main())
