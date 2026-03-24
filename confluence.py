import json
import logging
from typing import Any, Dict, List, Optional

import requests

from config import Configuration

logger = logging.getLogger(__name__)


class ConfluenceHandler:
    """Builds and publishes a Confluence release-note page from structured PR data."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _fmt_key(key: str) -> str:
        return key.replace("_", " ").title()

    @staticmethod
    def _para(heading: str, contents: Optional[List[str] | str], level: str = "h2") -> str:
        """Return an HTML paragraph/list block, empty string if contents is falsy."""
        if not contents and contents != 0:
            return ""

        if isinstance(contents, list):
            items = "".join(f"<li>{c}</li>" for c in contents) if contents else "<li>-</li>"
            body = f"<ul>{items}</ul>"
        else:
            body = f"<p>{contents or '-'}</p>"

        header = f"<{level}>{heading}</{level}>\n" if heading else ""
        return f"{header}{body}"

    def _table(self, heading: Optional[str], data: Dict[str, Any]) -> str:
        """Return an HTML table block, empty string if data is empty."""
        if not data:
            return ""

        rows = ""
        for key, value in data.items():
            display_key = self._fmt_key(key)
            if isinstance(value, bool):
                display_value = "✅ YES" if value else "❌ NO"
            elif isinstance(value, list):
                display_value = "<br/>".join(map(str, value)) if value else "-"
            else:
                display_value = str(value) if value else "-"

            rows += (
                f"<tr>"
                f"<td><b>{display_key}</b></td>"
                f"<td>{display_value}</td>"
                f"</tr>"
            )

        header = f"<h2>{heading}</h2>\n" if heading else ""
        return f"{header}<table><tbody>{rows}</tbody></table>"

    # ------------------------------------------------------------------
    # Page Builder
    # ------------------------------------------------------------------

    def build_page(self, data: Dict) -> str:
        r = data.get("release", {})
        dep = r.get("deployment", {})
        sw = r.get("software_changes", {})

        sections = [
            self._table(None, r.get("metadata", {})),
            self._para("Objective", r.get("objective")),
            self._para("Features Included in this Release", r.get("features"), "h3"),
            self._para("Issue Fixes", r.get("issue_fixes"), "h3"),
            self._para("Known Issues & Workarounds", r.get("known_issues"), "h3"),
            self._table("Code Version Details", r.get("code_version_details", {})),
            self._para("Compute Changes (Lambda/EC2/ECS/EKS)", sw.get("compute"), "h3"),
            self._para("Other Component Changes", sw.get("other_components"), "h3"),
            self._para("Configuration Changes", r.get("configuration_changes"), "h3"),
            self._para("Database Changes", r.get("database_changes"), "h3"),
            self._para("Infrastructure Changes", r.get("infra_changes"), "h3"),
            self._table("Dev Testing Details", r.get("testing", {})),
            self._table("Impact Analysis", r.get("impact_analysis", {})),
            self._table("Checklist", r.get("checklist", {})),
            self._para("Pre-requisites for Deployment", dep.get("pre_requisites"), "h3"),
            self._para("Rollback Method", dep.get("rollback_method"), "h3"),
            self._para("Post-Deployment Testing", dep.get("post_deployment_testing"), "h3"),
            self._para("Post-Deployment Monitoring", dep.get("monitoring_details"), "h3"),
            self._table("Communication Plan", r.get("communication", {})),
        ]

        return "".join(s for s in sections if s)

    # ------------------------------------------------------------------
    # Publish
    # ------------------------------------------------------------------

    def process(self, _data: Dict, release_name: str = "ReleaseX") -> Dict:
        xhtml_body = self.build_page(_data)
        payload = {
            "type": "page",
            "title": release_name,
            "space": {"key": Configuration.SPACE_KEY},
            "ancestors": [{"id": Configuration.PARENT_PAGE_ID}],
            "body": {
                "storage": {
                    "value": xhtml_body,
                    "representation": "storage",
                }
            },
        }

        url = f"{Configuration.BASE_URL}/rest/api/content"
        response = requests.post(
            url,
            auth=(Configuration.EMAIL, Configuration.API_TOKEN),
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=15,
        )

        page_data = response.json()
        logger.info(f"Confluence API token : {Configuration.API_TOKEN} ::: {Configuration.PARENT_PAGE_ID}")
        page_url = (
            f"{Configuration.BASE_URL}{page_data.get("_links").get("webui")}"
        )
        logger.info("Confluence page created: %s", page_url)
        return {"page_id": page_data.get("id"), "page_url": page_url}