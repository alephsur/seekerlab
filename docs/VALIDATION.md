# Initial release validation

Date: September 10, 2026.

## Completed

| Check | Result |
| --- | --- |
| npm dependency installation | Completed; `package-lock.json` included |
| TypeScript, `tsc --noEmit` | No errors |
| Compatibility with Expo's bundled versions, offline mode | Correct after adjusting React Native to 0.85.3 |
| Metro Android export | Successful: 854 modules and a generated Hermes bundle |
| Business-rule tests with unittest | 8 tests passed |
| Python syntax compilation | Successful |
| JSON, TOML, and YAML parsing | Successful |
| Initial bootstrap and second run | Generates configuration and preserves existing files |

Resolved npm versions: Expo 56.0.21, React 19.2.3, React Native 0.85.3,
Wallet UI 4.3.0, Solana Kit 7.1.1, Quick Crypto 1.1.7, Quick Base64 3.0.1,
and Nitro Modules 0.37.1. The lockfile preserves the exact dependency tree.

The compatibility check ran without querying remote Expo services: it compares local
versions against the bundled catalog. Metro emitted a resolution warning for
`@noble/hashes/crypto.js` inside a Wallet Standard dependency; it resolved the file and
completed the bundle. No transitive dependencies were modified to hide the warning.

## Pending on the development machine

- Install the Python dependencies: the creation environment could not access PyPI
  and did not have them cached.
- Run the 7 included API tests with `make check-api`.
- Validate migrations, startup, and persistence with PostgreSQL and Docker Compose.
- Run Ruff and the CI workflow in an environment with their dependencies.
- Test real slot concurrency in PostgreSQL; SQLite does not demonstrate this guarantee.
- Build the APK and test the interface and wallet connection on a real Android/Seeker device.

Docker and the Android SDK were not available in the creation environment. A Metro export
**is not a native build or proof that MWA works on a phone**.

The ZIP contains source code and configuration. It does not contain the local credentials
used during validation, installed dependencies, or generated bundles/APKs.
