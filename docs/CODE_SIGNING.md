# Code Signing Setup

ClawVoice uses SignPath.io for free open source code signing.

## Setup (one-time, done by maintainer)

1. Create account at https://signpath.io
2. Apply for **Open Source** subscription (free) — https://signpath.io/product/open-source
3. Create a new project with slug `ClawVoice`
4. Create a signing policy with slug `release-signing`
5. Create an artifact configuration with slug `installer` targeting `ClawVoice-Setup.exe`
6. Add secrets to the GitHub repo (`Settings → Secrets and variables → Actions`):
   - `SIGNPATH_API_TOKEN` — your SignPath API token
   - `SIGNPATH_ORG_ID` — your SignPath organization ID

## How it works

Every release build automatically signs `ClawVoice-Setup.exe` via the SignPath GitHub Action before publishing to GitHub Releases.

Users on Windows 11 with Smart App Control enabled can install without warnings once the certificate has built reputation with Microsoft SmartScreen.

## Current status

The signing step is **wired up** in `build.yml` but will only run when `SIGNPATH_API_TOKEN` is set as a repo secret. Unsigned builds still work — users will need to bypass SmartScreen manually (see [README Troubleshooting section](../README.md#troubleshooting)).

## References

- SignPath docs: https://docs.signpath.io/documentation/github-actions
- SignPath open source program: https://signpath.io/product/open-source
- GitHub Action: https://github.com/SignPath/github-action-submit-signing-request
