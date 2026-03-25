import json
import logging
from typing import Dict

import yaml

from confluence import ConfluenceHandler

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)



class PRBodyParser:

    @staticmethod
    def parse(pr_body: str) -> Dict:
        if "```yaml" not in pr_body:
            raise ValueError("No ```yaml block found in PR body.")

        try:
            raw_yaml = pr_body.split("```yaml")[1].split("```")[0].strip()
            return yaml.safe_load(raw_yaml)
        except (IndexError, yaml.YAMLError) as exc:
            raise ValueError(f"Failed to parse YAML: {exc}") from exc



def lambda_handler(event: Dict, _) -> Dict:
    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON body: %s", exc)
        return {"statusCode": 400, "message": "Invalid JSON payload"}

    action = body.get("action")
    pr = body.get("pull_request", {})

    # _: str = pr.get("title", "Release")
    pr_body: str = pr.get("body", "")

    # ── Process only edited + merged PRs ───────────────────────────────────
    if action not in ("edited", "closed"):
        return {"statusCode": 200, "message": "Ignored: unsupported event"}

    if action == "closed" and not pr.get("merged_at"):
        return {"statusCode": 200, "message": "Ignored: PR closed but not merged"}

    # ── Parse YAML ────────────────────────────────────────────────────────
    try:
        parsed_data = PRBodyParser.parse(pr_body)
    except ValueError as exc:
        logger.error("PR body parse error: %s", exc)
        return {"statusCode": 422, "message": str(exc)}

    try:
        result = ConfluenceHandler().process(_data=parsed_data)

        return {
            "statusCode": 200,
            "message": "Success",
            "result": result,
        }

    except Exception as exc:
        logger.exception("Confluence error: %s", exc)
        return {"statusCode": 500, "message": str(exc)}