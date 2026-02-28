#!/usr/bin/env python3
"""Run news ingestion: fetch, store, index in Endee."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.progress import Progress, SpinnerColumn

from src.news_ingestion.fetcher import NewsFetcher
from src.news_ingestion.storage import NewsStorage
from src.vector_db.endee_client import EndeeVectorStore

console = Console()


async def main():
    console.print("[bold blue]News Intelligence - Ingestion Pipeline[/bold blue]\n")

    with Progress(SpinnerColumn(), console=console) as progress:
        t1 = progress.add_task("Fetching news...", total=None)
        fetcher = NewsFetcher()
        articles = await fetcher.fetch_all()
        progress.update(t1, completed=True)
        console.print(f"  [green]✓[/green] Fetched {len(articles)} articles")

        t2 = progress.add_task("Storing (weekly/monthly)...", total=None)
        storage = NewsStorage()
        storage.save_articles(articles)
        deleted = storage.run_auto_deletion()
        progress.update(t2, completed=True)
        console.print(f"  [green]✓[/green] Stored | Deleted {deleted} old buckets")

        t3 = progress.add_task("Indexing in Endee...", total=None)
        vector_store = EndeeVectorStore()
        indexed = vector_store.upsert_articles(articles)
        progress.update(t3, completed=True)
        console.print(f"  [green]✓[/green] Indexed {indexed} vectors in Endee")

    console.print("\n[bold green]Ingestion complete![/bold green]")


if __name__ == "__main__":
    asyncio.run(main())
