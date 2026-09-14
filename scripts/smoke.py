"""Read-only smoke check against the local API. Run make up first."""
import json
from urllib.request import urlopen

from bootstrap import ROOT, read_env

port = read_env(ROOT / ".env").get("API_PORT", "8000")
for path in ("/health/live", "/health/ready", "/api/v1/campaigns", "/openapi.json"):
    with urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as response:
        data = json.load(response)
        if path.endswith("campaigns"):
            assert isinstance(data, list) and len(data) >= 3, "Run make seed to create example campaigns"
        print(f"OK {path}")
