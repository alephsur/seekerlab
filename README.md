# SeekerLab

Development foundation for an Android app that enables paid testing of Solana dApps.
Monorepo built with React Native + Expo, FastAPI, SQLAlchemy, Alembic, and PostgreSQL.

**This release is a functional starting point for local development, not the complete MVP.**
The sample rewards are not funded. No money is transferred.

## Quick start on Ubuntu

You need Docker with Compose v2.20+, Python 3.12+, Node.js 24 LTS, npm, and `make`.
For the app, you also need Android Studio, Android SDK 36, JDK 17, and either an emulator or an Android device connected over USB.

From this directory:

```bash
make setup
make up
make smoke
make mobile-install
make android
```

`make setup` generates separate **local** credentials for the developer and tester,
along with the `.env` files. It does not overwrite existing configuration.
`make up` starts PostgreSQL, applies migrations, starts the API, and loads three sample campaigns.
The first Android build may take several minutes while Gradle and its dependencies are downloaded.

- API: <http://localhost:8000>
- Swagger: <http://localhost:8000/docs>
- Health: <http://localhost:8000/health/ready>
- In the emulator, the app uses `http://10.0.2.2:8000` to reach the host computer.

**Use a development build with `make android`; Expo Go does not support the native MWA modules.**
After the first installation, `make mobile` starts Metro again.
For physical devices, occupied ports, and development without Docker, see the
[local development guide](docs/LOCAL_DEVELOPMENT.md).

## What is included

| Area | Status |
| --- | --- |
| Campaigns | Listing, details, API creation, and closure by the owner |
| Submissions | Text submission, tester history, and owner review |
| Rules | Validation, one submission per campaign/user, capacity, and closed-campaign blocking |
| Database | Initial migration, indexes, uniqueness, persistent volume, and idempotent seed data |
| Mobile app | Browse, search, read instructions, submit observations, and view history |
| Wallet | MWA connect/disconnect code on devnet; requires a controlled domain and a compatible wallet |
| API authentication | Two local users with development tokens; disabled in production |
| SGT, SIWS, payments, and AI | Integration contracts and tasks defined; implementations pending |
| Attachments and recording | Pending; the initial flow uses text |
| Developer dashboard | Swagger and HTTP examples; a dedicated interface is pending |

The connected wallet is **not yet the identity used for API requests**.
API mode uses `local-tester`. SIWS must replace this access method before onboarding real users.

## Project structure

| Path | Responsibility |
| --- | --- |
| `apps/mobile` | Expo application and npm dependencies locked in `package-lock.json` |
| `apps/mobile/src/features` | Campaigns, submissions, and wallet |
| `apps/api/src/seekerlab/modules/campaigns` | Rules, use cases, repository, models, and schemas |
| `apps/api/src/seekerlab/modules/identity` | Local authentication and the SGT verification port |
| `apps/api/src/seekerlab/modules/analysis` | Contract for future feedback analysis |
| `apps/api/src/seekerlab/modules/payments` | Payment verification contract |
| `apps/api/migrations` | Alembic migration history |
| `apps/api/tests` | Domain and API tests |
| `scripts` | Initial setup and local checks |
| `examples` | Sample HTTP requests and payloads |
| `docs` | Architecture, setup, next sprint, and validation |
| `contracts` | Decisions about a possible future escrow implementation |

## Common commands

```bash
make logs          # Follow the API logs
make down          # Stop services while preserving the PostgreSQL volume
make seed          # Add missing examples without resetting existing ones
make migrate       # Apply new migrations
make test-domain   # Test business rules without installing Python dependencies
make check-api     # Run pytest inside the container
make check-mobile  # TypeScript
```

The API tests use a temporary SQLite database and do not modify your development data.
The included workflow also checks migrations against PostgreSQL.
Read [VALIDATION.md](docs/VALIDATION.md) to distinguish completed checks from pending ones.

## Test without a backend

In `apps/mobile/.env`, set `EXPO_PUBLIC_DATA_MODE=demo` and restart Metro.
The app uses in-memory data and displays a DEMO banner. Submissions are lost after
a full reload. An API failure never enables this mode automatically.

## Enable wallet connection

1. Set `EXPO_PUBLIC_WALLET_IDENTITY_URI` to an HTTPS domain you control.
2. Restart Metro and install an MWA-compatible wallet on the test Android device.
3. Open Wallet → Connect wallet. The network is fixed to **devnet**.

App identity validation may require Digital Asset Links on the domain.
The package name `com.seekerlab.app` is provisional: change it before publishing and
use the corresponding signing certificate. No domain, Expo account, publishing account,
or remote repository has been registered.

## Continue development

The recommended next increment is **complete SIWS and real SGT verification**.
The [initial backlog](docs/BACKLOG.md) defines the acceptance criteria.

Campaign reward amounts are advertised values serialized as decimal strings.
They are not atomic units and do not prove that a budget has been deposited.
Never place private keys, private RPC endpoints, or backend tokens in `EXPO_PUBLIC_*`.
The tester token included there is deliberately public and valid only for local development.

Python dependencies have bounded ranges in `pyproject.toml`. Their lockfile still needs
to be generated and validated in an environment with PyPI access; full backend
reproducibility is not guaranteed until those dependencies and container images are pinned.

## Official references

- [Solana Mobile: MWA installation](https://docs.solanamobile.com/get-started/react-native/installation)
- [Wallet provider](https://docs.solanamobile.com/get-started/react-native/setup)
- [Seeker Genesis Token](https://docs.solanamobile.com/solana-mobile-stack/seeker-genesis-token)
- [Publishing to the dApp Store](https://docs.solanamobile.com/dapp-store/submit-new-app)
- [Expo SDK compatibility](https://docs.expo.dev/versions/latest/)

This foundation does not assign a distribution license. Choose a project license
before sharing the code publicly.
