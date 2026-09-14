# SeekerLab working conventions

- This repository is an Android Expo app and a FastAPI modular monolith.
- Read README.md and docs/ARCHITECTURE.md before changing module boundaries.
- Keep business rules in campaigns/domain.py; HTTP validation belongs in schemas/routes.
- Store advertised reward amounts as Decimal strings; actual transfers will use atomic integers.
- Wallet connection is not backend authentication. Do not treat a client-provided address as verified.
- Do not mark an SGT verified or a payment complete without the required server-side checks.
- Keep demo mode explicit. An API failure must remain visible instead of falling back silently.
- Do not commit `.env`, credentials, build signing keys, node_modules or generated native folders.
- Run `make test-domain`, `make check-mobile` and `make check-api` when the environment supports them.
- For native dependency changes, also rebuild Android and document any remaining untested integration.
- The mobile lockfile is committed; a Python lockfile remains a documented setup task.
- Keep all project documentation and source identifiers in English.
