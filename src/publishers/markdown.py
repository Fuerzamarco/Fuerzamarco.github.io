from __future__ import annotations

from pathlib import Path

from .base import Article, Publisher, PublishResult


class MarkdownPublisher(Publisher):
    def __init__(self, output_dir: Path | str) -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def publish(self, article: Article) -> PublishResult:
        if not article.slug:
            return PublishResult(ok=False, location="", detail="Article has no slug")
        path = self._output_dir / f"{article.slug}.md"
        path.write_text(article.markdown, encoding="utf-8")
        return PublishResult(ok=True, location=path)
