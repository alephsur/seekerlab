# Local development

## Android on Ubuntu

Install Android Studio and use SDK Manager to install Android SDK Platform 36,
Build Tools 36, Android SDK Platform Tools, and an emulator image. Use JDK 17 and Node.js 24.
Up-to-date installation instructions are available in
[Solana Mobile Development Setup](https://docs.solanamobile.com/get-started/development-setup).

For a standard installation, configure your shell as follows and adjust the paths as needed:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools"
java -version
adb devices
```

If configured, `JAVA_HOME` must point to the installed JDK 17.
Start an emulator before running `make android`. Use an ARM image/build for a physical ARM
device and an x86_64 image for an emulator on an x86 PC.

## Physical device over USB

Enable USB debugging and authorize your computer on the device.

```bash
adb devices
adb reverse tcp:8000 tcp:8000
adb reverse tcp:8081 tcp:8081
```

In `apps/mobile/.env`, set:

```dotenv
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000
```

Then run `make android`. If Metro cannot find the device:

```bash
cd apps/mobile
npm start -- --localhost
```

The ADB tunnel allows the API to remain bound to localhost. If you change the API port,
update both ends of `adb reverse` and the Expo URL.

## Device over Wi-Fi

With the computer and device on the same network, set `API_BIND_HOST=0.0.0.0` in the
root `.env` and `EXPO_PUBLIC_API_URL=http://YOUR_COMPUTER_LOCAL_IP:8000` in the mobile `.env`.
Recreate the API with `docker compose up -d api` and restart Metro.
Use this configuration only on a trusted development network: local access is not
equivalent to the product's final authentication system.

## Backend without a container

Keep PostgreSQL in Docker and run Python in a virtual environment:

```bash
make setup
docker compose up -d db
cd apps/api
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
alembic upgrade head
python -m seekerlab.seed
uvicorn seekerlab.main:app --reload --host 127.0.0.1 --port 8000
```

`apps/api/.env` contains the PostgreSQL URL for localhost. The container uses the
internal URL with the `db` hostname defined in `compose.yaml`.
During local development, migrations are run from `apps/api`.

## New migration

After modifying models:

```bash
cd apps/api
source .venv/bin/activate
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Review the SQL and downgrade path before applying a migration to important data.
When using Docker, rebuild the image after adding migrations or changing dependencies
with `make up`. Changes under `src` are reloaded through the development volume.

## Create campaigns from Swagger

Open `/docs` and select Authorize. Enter the `DEV_BUILDER_TOKEN` value from your `.env`
in the Bearer field to create or close campaigns and review their submissions.
Use `DEV_TESTER_TOKEN` to submit feedback and view local history.
The role is not accepted in the request body.
Complete examples are available in `examples/api.http`.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Network request failed | Run `make smoke`; check the emulator URL `10.0.2.2`, ADB tunnel, or Wi-Fi IP |
| Port 5432/8000 already in use | Change root `DB_PORT`/`API_PORT` and the URLs in the generated `.env` files |
| 401 on submissions | The public tester token must match the API's `DEV_TESTER_TOKEN` |
| 403 when creating a campaign | Use the builder token, not the tester token |
| 409 when submitting | You already submitted to that campaign, it is closed, or no slots remain |
| 503 on private routes | Development authentication is disabled; SIWS is not implemented yet |
| No campaigns | Run `make seed`; the seed does not reopen closed campaigns |
| Wallet not found | Install an MWA-compatible Android wallet and configure your own domain |
| Native module error | Use `make android`; rebuild after changing native dependencies |
| `.env` change not reflected | Restart Metro; if it persists, run `npm start -- --clear` from `apps/mobile` |

If you recreate the PostgreSQL container while preserving the volume, preserve its
password as well: changing it in `.env` does not automatically change the existing user's
password. `make down` preserves data; startup does not run automatic deletion commands.
