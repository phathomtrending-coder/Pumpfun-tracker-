import os
import requests

RUGCHECK_ENABLED = os.getenv("RUGCHECK_ENABLED", "false").lower() == "true"
RUGCHECK_API_KEY = os.getenv("RUGCHECK_API_KEY", "")
RUGCHECK_TIMEOUT = int(os.getenv("RUGCHECK_TIMEOUT", "12"))

# Put the exact token-scan endpoint from RugCheck Swagger here.
# Example format only — replace once you confirm the official path in Swagger:
# https://api.rugcheck.xyz/v1/tokens/{token}/report
RUGCHECK_TOKEN_URL_TEMPLATE = os.getenv("RUGCHECK_TOKEN_URL_TEMPLATE", "")


def rugcheck_scan(token_address: str) -> dict:
    if not RUGCHECK_ENABLED:
        return {
            "ok": True,
            "status": "disabled",
            "passed": True,
            "raw": None,
        }

    if not RUGCHECK_TOKEN_URL_TEMPLATE:
        return {
            "ok": False,
            "status": "missing_url_template",
            "passed": False,
            "raw": None,
        }

    url = RUGCHECK_TOKEN_URL_TEMPLATE.format(token=token_address)

    headers = {}
    if RUGCHECK_API_KEY:
        headers["Authorization"] = f"Bearer {RUGCHECK_API_KEY}"

    try:
        response = requests.get(url, headers=headers, timeout=RUGCHECK_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        # Keep this generic until you confirm the exact RugCheck response fields.
        score = (
            data.get("score")
            or data.get("riskScore")
            or data.get("trustScore")
            or 0
        )

        risks = data.get("risks") or data.get("warnings") or []
        is_known_bad = False

        # Conservative fail conditions
        lowered = str(data).lower()
        if "honeypot" in lowered or "scam" in lowered or "malicious" in lowered:
            is_known_bad = True

        passed = not is_known_bad

        return {
            "ok": True,
            "status": "ok",
            "passed": passed,
            "score": score,
            "risks": risks,
            "raw": data,
        }

    except Exception as e:
        return {
            "ok": False,
            "status": f"error:{e}",
            "passed": False,
            "raw": None,
        }
