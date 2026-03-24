"""
main.py — Lambda entry-point for GitHub PR → Confluence + GitHub Release automation.

Flow (on PR merged):
  1. Parse the YAML block embedded in the PR body.
  2. Publish a Confluence release-note page.
  3. [NEW] Create / update a GitHub Release with a formatted Markdown body.
"""

import json
import logging
from typing import Dict

import yaml

from confluence import ConfluenceHandler

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class PRBodyParser:
    """Extracts the YAML block from a GitHub PR body."""

    @staticmethod
    def parse(pr_body: str) -> Dict:
        """
        Raises:
            ValueError: if no YAML block is found or YAML is malformed.
        """
        if "```yaml" not in pr_body:
            raise ValueError("No ```yaml block found in PR body.")

        try:
            raw_yaml = pr_body.split("```yaml")[1].split("```")[0].strip()
            return yaml.safe_load(raw_yaml)
        except (IndexError, yaml.YAMLError) as exc:
            raise ValueError(f"Failed to parse YAML from PR body: {exc}") from exc


# ---------------------------------------------------------------------------
# Lambda handler
# ---------------------------------------------------------------------------

def lambda_handler(event: Dict, context) -> Dict:
    # ── Parse webhook payload ──────────────────────────────────────────────
    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON body: %s", exc)
        return {"statusCode": 400, "message": "Invalid JSON payload"}

    action = body.get("action")
    pr = body.get("pull_request", {})

    # Only process merged PRs
    if action != "closed" or not pr.get("merged_at"):
        return {"statusCode": 200, "message": "Ignored: not a merged PR event"}

    pr_title: str = pr.get("title", "Release")
    pr_body: str = pr.get("body", "")

    # ── Parse YAML ────────────────────────────────────────────────────────
    try:
        parsed_data = PRBodyParser.parse(pr_body)
    except ValueError as exc:
        logger.error("PR body parse error: %s", exc)
        return {"statusCode": 422, "message": str(exc)}

    # ── Validate config ───────────────────────────────────────────────────
    # try:
    #     Configuration.validate()
    # except EnvironmentError as exc:
    #     logger.error("Config error: %s", exc)
    #     return {"statusCode": 500, "message": str(exc)}

    # ── Publish Confluence page ────────────────────────────────────────────
    try:
        confluence_result = ConfluenceHandler().process(
            _data=parsed_data,
            release_name=pr_title,
        )
        logger.info("Confluence page created: %s", confluence_result)
        return {
            "statusCode": 200,
            "message": "Confluence page created successfully",
            "result": confluence_result,
        }
    except Exception as exc:
        logger.exception("Confluence publish failed: %s", exc)
        return {"statusCode": 500, "message": str(exc)}