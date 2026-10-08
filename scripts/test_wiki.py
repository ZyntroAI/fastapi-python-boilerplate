import pytest
from unittest.mock import patch

class TestWikiEndpoint:
    def test_wiki_get_missing_title(self, client):
        """ไม่ส่งชื่อ — 400"""
        resp = client.get("/api/v1/wiki/get")
        assert resp.status_code == 400
        assert "title" in str(resp.get_json()["errors"])

    def test_wiki_get_invalid_lang(self, client):
        """ภาษาไม่รองรับ — 400"""
        resp = client.get("/api/v1/wiki/get?title=Python&lang=xx")
        assert resp.status_code == 400

    @patch("app.api.v1.wiki.fetch_wikipedia_article")
    def test_wiki_get_success(self, mock_fetch, client):
        """ดึงข้อมูลสำเร็จ — ตรวจสอบรูปแบบผลลัพธ์"""
        mock_fetch.return_value = {
            "title": "Python (programming language)",
            "summary": "Python is a high-level...",
            "full_url": "https://en.wikipedia.org/wiki/Python",
            "accessed_at": "2026-10-08T00:00:00",
            "revision_id": "12345",
            "license": "CC BY-SA 4.0",
        }

        resp = client.get("/api/v1/wiki/get?title=Python&lang=en")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["data"]["title"] == "Python (programming language)"
        mock_fetch.assert_called_once_with(
            title="Python", lang="en", use_cache=True
        )

    @patch("app.api.v1.wiki.fetch_wikipedia_article")
    def test_wiki_not_found(self, mock_fetch, client):
        """ไม่พบบทความ — 404"""
        mock_fetch.side_effect = ValueError("ไม่พบบทความ: NotExistArticle")
        resp = client.get("/api/v1/wiki/get?title=NotExistArticle")
        assert resp.status_code == 404
        assert "ไม่พบ" in resp.get_json()["message"]
