import base64
import json
import logging
from typing import Any, Dict, Optional

import requests

from config import Configuration

logger = logging.getLogger(__name__)


class ConfluenceHandler:

    @staticmethod
    def _fmt_key(key: str) -> str:
        return key.replace("_", " ").title()

    @staticmethod
    def _para(heading: str, contents, level: str = "h2") -> str:
        if not contents and contents != 0:
            return ""

        if isinstance(contents, list):
            items = "".join(f"<li>{c}</li>" for c in contents) or "<li>-</li>"
            body = f"<ul>{items}</ul>"
        else:
            body = f"<p>{contents or '-'}</p>"

        header = f"<{level}>{heading}</{level}>\n" if heading else ""
        return f"{header}{body}"

    def _table(self, heading: Optional[str], data: Dict[str, Any]) -> str:
        if not data:
            return ""

        rows = ""
        for key, value in data.items():
            k = self._fmt_key(key)

            if isinstance(value, bool):
                v = "✅ YES" if value else "❌ NO"
            elif isinstance(value, list):
                v = "<br/>".join(map(str, value)) or "-"
            else:
                v = str(value) if value else "-"

            rows += f"<tr><td><b>{k}</b></td><td>{v}</td></tr>"

        header = f"<h2>{heading}</h2>\n" if heading else ""
        return f"{header}<table><tbody>{rows}</tbody></table>"

    # ...

    def build_page(self, data: Dict) -> str:
        r = data.get("release", {})
        dep = r.get("deployment", {})
        sw = r.get("software_changes", {})

        sections = [
            self._table(None, r.get("metadata", {})),
            self._para("Objective", r.get("objective")),
            self._para("Features", r.get("features"), "h3"),
            self._para("Issue Fixes", r.get("issue_fixes"), "h3"),
            self._para("Known Issues", r.get("known_issues"), "h3"),
            self._table("Code Version Details", r.get("code_version_details", {})),
            self._para("Compute Changes", sw.get("compute"), "h3"),
            self._para("Other Components", sw.get("other_components"), "h3"),
            self._para("Configuration Changes", r.get("configuration_changes"), "h3"),
            self._para("Database Changes", r.get("database_changes"), "h3"),
            self._para("Infra Changes", r.get("infra_changes"), "h3"),
            self._table("Testing", r.get("testing", {})),
            self._table("Impact Analysis", r.get("impact_analysis", {})),
            self._table("Checklist", r.get("checklist", {})),
            self._para("Pre-requisites", dep.get("pre_requisites"), "h3"),
            self._para("Rollback", dep.get("rollback_method"), "h3"),
            self._para("Post Deployment Testing", dep.get("post_deployment_testing"), "h3"),
            self._para("Monitoring", dep.get("monitoring_details"), "h3"),
            self._table("Communication", r.get("communication", {})),
        ]

        return "".join(filter(None, sections))

    # ...

    @staticmethod
    def _request(method: str, url: str, **kwargs) -> Dict:
        creds = f"{Configuration.EMAIL}:{Configuration.API_TOKEN}"
        encoded = base64.b64encode(creds.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
        }

        res = requests.request(
            method,
            url,
            headers = headers,
            timeout = 15,
            **kwargs,
        )

        try:
            data = res.json()
        except Exception:
            raise ValueError(f"Invalid JSON response: {res.text}")

        if res.status_code not in (200, 201):
            logger.error("Confluence API error: %s", data)
            raise RuntimeError(f"Confluence API failed: {data}")

        return data

    @staticmethod
    def _extract_page_url(data: Dict) -> str:
        links = data.get("_links")
        if not links or "webui" not in links:
            raise ValueError(f"Missing '_links.webui': {data}")
        return f"{Configuration.BASE_URL}{links['webui']}"

    # ...

    def _get_page_by_title(self, title: str) -> Optional[Dict]:
        url = f"{Configuration.BASE_URL}/rest/api/content"

        data = self._request(
            "GET",
            url,
            params={
                "title": title,
                "spaceKey": Configuration.SPACE_KEY,
                "expand": "version",
            },
        )

        results = data.get("results", [])
        return results[0] if results else None

    @staticmethod
    def _create_page(title: str, body: str) -> Dict:
        url = f"{Configuration.BASE_URL}/rest/api/content"

        payload = {
            "type": "page",
            "title": title,
            "space": {"key": Configuration.SPACE_KEY},
            "ancestors": [{"id": Configuration.PARENT_PAGE_ID}],
            "body": {
                "storage": {"value": body, "representation": "storage"}
            },
        }

        return ConfluenceHandler._request("POST", url, data=json.dumps(payload))

    @staticmethod
    def _update_page(page_id: str, title: str, body: str, version: int) -> Dict:
        url = f"{Configuration.BASE_URL}/rest/api/content/{page_id}"

        payload = {
            "id": page_id,
            "type": "page",
            "title": title,
            "version": {"number": version + 1},
            "body": {
                "storage": {"value": body, "representation": "storage"}
            },
        }

        return ConfluenceHandler._request("PUT", url, data=json.dumps(payload))

    # ...

    def process(self, _data: Dict, release_name: str) -> Dict:
        body = self.build_page(_data)

        existing = self._get_page_by_title(release_name)

        if existing:
            data = self._update_page(
                existing["id"],
                release_name,
                body,
                existing["version"]["number"],
            )
            action = "updated"
            page_id = existing["id"]
        else:
            data = self._create_page(release_name, body)
            action = "created"
            page_id = data.get("id")

        page_url = self._extract_page_url(data)

        logger.info("%s page: %s", action.upper(), page_url)

        return {
            "page_id": page_id,
            "page_url": page_url,
            action: True,
        }