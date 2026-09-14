"""Generate local config without overwriting existing files or printing tokens."""
import argparse
from pathlib import Path
import secrets
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]


def read_env(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return dict(line.split("=", 1) for line in path.read_text().splitlines()
                if "=" in line and not line.lstrip().startswith("#"))


def write_new(path: Path, text: str) -> None:
    if path.exists():
        print(f"Preserved: {path.relative_to(ROOT)}")
        return
    path.write_text(text, encoding="utf-8")
    path.chmod(0o600)
    print(f"Created: {path.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-mode", choices=["api", "demo"], default="api")
    args = parser.parse_args()
    root_env = ROOT / ".env"
    if not root_env.exists():
        template = (ROOT / ".env.example").read_text()
        for field in ("POSTGRES_PASSWORD", "DEV_BUILDER_TOKEN", "DEV_TESTER_TOKEN"):
            template = template.replace(f"{field}=GENERATED_BY_BOOTSTRAP", f"{field}={secrets.token_hex(24)}")
        write_new(root_env, template)
    values = read_env(root_env)
    for key in ("POSTGRES_PASSWORD", "DEV_BUILDER_TOKEN", "DEV_TESTER_TOKEN"):
        if len(values.get(key, "")) < 32 or values[key] == "GENERATED_BY_BOOTSTRAP":
            raise SystemExit(f"Replace the placeholder {key} in .env with a random value of at least 32 characters.")
    url = (f"postgresql+psycopg://{quote(values.get('POSTGRES_USER', 'seekerlab'), safe='')}:"
           f"{quote(values['POSTGRES_PASSWORD'], safe='')}@localhost:{values.get('DB_PORT', '5432')}/"
           f"{quote(values.get('POSTGRES_DB', 'seekerlab'), safe='')}")
    write_new(ROOT / "apps/api/.env", "\n".join([
        "APP_ENV=development", f"DATABASE_URL={url}", "DEV_AUTH_ENABLED=true",
        f"DEV_BUILDER_TOKEN={values['DEV_BUILDER_TOKEN']}",
        f"DEV_TESTER_TOKEN={values['DEV_TESTER_TOKEN']}", "CORS_ORIGINS=[]",
        f"SIWS_DOMAIN={values.get('SIWS_DOMAIN', 'localhost:8000')}",
        f"SIWS_URI={values.get('SIWS_URI', 'http://localhost:8000')}", "",
    ]))
    write_new(ROOT / "apps/mobile/.env", "\n".join([
        f"EXPO_PUBLIC_API_URL=http://10.0.2.2:{values.get('API_PORT', '8000')}",
        f"EXPO_PUBLIC_DATA_MODE={args.data_mode}",
        "EXPO_PUBLIC_WALLET_IDENTITY_URI=", "",
    ]))
    print("Ready. Next: make up, make mobile-install, make android.")


if __name__ == "__main__":
    main()
