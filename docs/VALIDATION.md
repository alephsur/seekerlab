# Initial release validation

Date: September 14, 2026.

## Completed

| Check | Result |
| --- | --- |
| npm dependency installation | Completed; `package-lock.json` included |
| TypeScript, `tsc --noEmit` | No errors |
| Compatibility with Expo's bundled versions, offline mode | Correct after adjusting React Native to 0.85.3 |
| Metro Android export | Successful: 858 modules and a generated Hermes bundle |
| Business-rule tests with unittest | 8 tests passed |
| Python syntax compilation | Successful |
| JSON, TOML, and YAML parsing | Successful |
| Initial bootstrap and second run | Generates configuration and preserves existing files |
| Locked Python environment | `uv.lock` resolves 42 packages; CI and Docker use locked installs |
| API and SIWS tests | 23 tests and 9 subtests passed; 2 PostgreSQL-only tests are conditionally selected |
| Ruff | No errors across source, tests, and migrations |
| SIWS security cases | Valid signature, invalid signature, reused/expired nonce, wallet change, rotation, and revocation |
| Android debug build | Successful with Expo SecureStore and MWA; debug APK generated locally |

Resolved npm versions: Expo 56.0.21, React 19.2.3, React Native 0.85.3,
Wallet UI 4.3.0, Solana Kit 7.1.1, Quick Crypto 1.1.7, Quick Base64 3.0.1,
Secure Store 56.0.4, and Nitro Modules 0.37.1. The lockfile preserves the exact
dependency tree.

The compatibility check ran without querying remote Expo services: it compares local
versions against the bundled catalog. Metro emitted a resolution warning for
`@noble/hashes/crypto.js` inside a Wallet Standard dependency; it resolved the file and
completed the bundle. No transitive dependencies were modified to hide the warning.

## Pending on the development machine

- Validate migrations, startup, persistence, one-slot concurrency, and atomic nonce
  consumption with PostgreSQL. The tests and CI configuration are included, but the local
  Docker socket was not accessible during this validation.
- Install the generated debug APK and exercise wallet selection and SIWS against a
  controlled HTTPS domain on a real Android/Seeker device.

The Android native build completed. A successful build is still **not proof that MWA and
SIWS work with a particular wallet on a phone**.

The ZIP contains source code and configuration. It does not contain the local credentials
used during validation, installed dependencies, or generated bundles/APKs.
