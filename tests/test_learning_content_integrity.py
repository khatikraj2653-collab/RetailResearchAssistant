"""
Confirms the Learning section has exactly one canonical content source
per chapter, and that the downloadable document is built from that same
source rather than a separately-maintained copy.
Run with: python tests/test_learning_content_integrity.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from data.learning_content import CHAPTERS, get_chapter, build_full_document


def test_exactly_five_chapters():
    assert len(CHAPTERS) == 5
    numbers = sorted(c["number"] for c in CHAPTERS)
    assert numbers == [1, 2, 3, 4, 5]
    print("test_exactly_five_chapters: PASS")


def test_get_chapter_matches_list():
    for c in CHAPTERS:
        fetched = get_chapter(c["number"])
        assert fetched is c, "get_chapter must return the SAME object as in CHAPTERS, not a copy"
    print("test_get_chapter_matches_list: PASS")


def test_full_document_contains_every_chapter_once():
    full_doc = build_full_document()
    for c in CHAPTERS:
        title_count = full_doc.count(c["title"])
        assert title_count == 1, f"Chapter '{c['title']}' should appear exactly once in the full download"
        assert c["content"] in full_doc, "Full document must contain the exact same content as the in-app version"
    print("test_full_document_contains_every_chapter_once: PASS")


if __name__ == "__main__":
    test_exactly_five_chapters()
    test_get_chapter_matches_list()
    test_full_document_contains_every_chapter_once()
    print("\nAll Learning content integrity tests passed -- single source of truth confirmed.")