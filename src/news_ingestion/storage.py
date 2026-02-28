"""News storage with weekly/monthly retention and auto-deletion."""

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from config.settings import settings


class NewsStorage:
    """Manages news storage with configurable retention and auto-deletion."""

    def __init__(
        self,
        data_dir: str = "data/news",
        retention_weeks: Optional[int] = None,
        retention_months: Optional[int] = None,
        auto_delete: Optional[bool] = None,
    ):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.retention_weeks = retention_weeks or settings.retention_weeks
        self.retention_months = retention_months or settings.retention_months
        self.auto_delete = auto_delete if auto_delete is not None else settings.auto_delete_enabled

    def _get_weekly_path(self, date: Optional[datetime] = None) -> Path:
        """Get path for weekly storage bucket."""
        dt = date or datetime.utcnow()
        week_start = dt - timedelta(days=dt.weekday())
        return self.data_dir / "weekly" / week_start.strftime("%Y-W%W")

    def _get_monthly_path(self, date: Optional[datetime] = None) -> Path:
        """Get path for monthly storage bucket."""
        dt = date or datetime.utcnow()
        return self.data_dir / "monthly" / dt.strftime("%Y-%m")

    def save_articles(self, articles: list[dict], bucket: str = "weekly") -> Path:
        """Save articles to weekly or monthly bucket."""
        if bucket == "weekly":
            path = self._get_weekly_path()
        else:
            path = self._get_monthly_path()

        path.mkdir(parents=True, exist_ok=True)
        file_path = path / "articles.json"

        existing = []
        if file_path.exists():
            with open(file_path, encoding="utf-8") as f:
                existing = json.load(f)

        existing_ids = {a["id"] for a in existing}
        new_articles = [a for a in articles if a["id"] not in existing_ids]
        combined = existing + new_articles

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(combined, f, indent=2, ensure_ascii=False)

        return file_path

    def load_all_articles(self) -> list[dict]:
        """Load all articles from weekly and monthly storage."""
        all_articles: list[dict] = []
        seen_ids: set[str] = set()

        for bucket in ["weekly", "monthly"]:
            bucket_path = self.data_dir / bucket
            if not bucket_path.exists():
                continue
            for subdir in bucket_path.iterdir():
                if subdir.is_dir():
                    articles_file = subdir / "articles.json"
                    if articles_file.exists():
                        with open(articles_file, encoding="utf-8") as f:
                            articles = json.load(f)
                        for a in articles:
                            if a["id"] not in seen_ids:
                                seen_ids.add(a["id"])
                                a["_bucket"] = bucket
                                a["_path"] = str(subdir)
                                all_articles.append(a)

        return all_articles

    def _get_old_weekly_dirs(self) -> list[Path]:
        """Get weekly directories older than retention period."""
        cutoff = datetime.utcnow() - timedelta(weeks=self.retention_weeks)
        old_dirs = []
        weekly_path = self.data_dir / "weekly"
        if not weekly_path.exists():
            return []
        for subdir in weekly_path.iterdir():
            if subdir.is_dir():
                try:
                    parts = subdir.name.split("-")
                    if len(parts) >= 2:
                        year, week = int(parts[0]), int(parts[1].replace("W", ""))
                        week_start = datetime(year, 1, 1) + timedelta(weeks=week - 1)
                        if week_start < cutoff:
                            old_dirs.append(subdir)
                except (ValueError, IndexError):
                    pass
        return old_dirs

    def _get_old_monthly_dirs(self) -> list[Path]:
        """Get monthly directories older than retention period."""
        cutoff = datetime.utcnow() - timedelta(days=30 * self.retention_months)
        old_dirs = []
        monthly_path = self.data_dir / "monthly"
        if not monthly_path.exists():
            return []
        for subdir in monthly_path.iterdir():
            if subdir.is_dir():
                try:
                    dt = datetime.strptime(subdir.name, "%Y-%m")
                    if dt < cutoff:
                        old_dirs.append(subdir)
                except ValueError:
                    pass
        return old_dirs

    def run_auto_deletion(self) -> int:
        """Delete old data beyond retention. Returns count of deleted items."""
        if not self.auto_delete:
            return 0
        deleted = 0
        for d in self._get_old_weekly_dirs() + self._get_old_monthly_dirs():
            shutil.rmtree(d, ignore_errors=True)
            deleted += 1
        return deleted
