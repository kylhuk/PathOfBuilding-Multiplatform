# Automated upstream releases

The scheduled synchronization workflow checks the upstream Path of Building
release feed every five minutes. It mirrors upstream tags and branches, merges
`upstream/dev` into this repository's `dev` branch, and dispatches the
multi-platform release workflow once for every new stable upstream release.

The release keeps the upstream tag, version, release title, and release notes.
The SimpleGraphic source ref is resolved to an immutable commit before any
build starts. A release is published only after all platform jobs succeed.

## Release assets

The release matrix produces:

- Windows x86, x64, and ARM64 standalone ZIPs and installers
- Linux x86, x64, and ARM64 tarballs, DEB packages, RPM packages, AppImages,
  and standalone Flatpak bundles
- macOS x64 and ARM64 tarballs and DMGs
- SHA-256 checksums for every asset

Homebrew supports Linux and macOS on x64 and ARM64. Homebrew itself does not
support 32-bit x86. Flathub publishes x86_64 and aarch64. Linux x86 remains
available as tar.gz, DEB, RPM, and AppImage assets.

## Homebrew publication

Create a public repository named `kylhuk/homebrew-pathofbuilding` with a
default branch called `main` and a `Formula` directory. Create a fine-grained
GitHub personal access token restricted to that repository with:

- Contents: Read and write
- Metadata: Read

Store the token as `HOMEBREW_TAP_TOKEN` in the PathOfBuilding repository's
Actions secrets. Set the repository variable `HOMEBREW_TAP_REPOSITORY` to
`kylhuk/homebrew-pathofbuilding`.

## Flathub publication

Flathub requires the initial submission PR to be authored and submitted
manually; its rules explicitly prohibit AI-generated initial submissions.
Submit `packaging/flatpak/community.pathofbuilding.PathOfBuilding.yml` yourself
after replacing the local payload source with source-build inputs accepted by
Flathub.

After the app is accepted and Flathub creates
`flathub/community.pathofbuilding.PathOfBuilding`, obtain a token belonging to
an approved maintainer with Contents read/write access to only that repository.
Store it as `FLATHUB_TOKEN` and set `FLATHUB_REPOSITORY` to the repository's
full name. Automated maintenance updates can then update the manifest; the
initial submission cannot be automated.

## Optional macOS signing and notarization

Unsigned DMGs are built without secrets. For warning-free distribution, add:

- `MACOS_CERTIFICATE_P12`: base64-encoded Developer ID Application certificate
- `MACOS_CERTIFICATE_PASSWORD`: P12 password
- `APPLE_ID`: notarization Apple ID
- `APPLE_TEAM_ID`: Apple Developer Team ID
- `APPLE_APP_PASSWORD`: app-specific password

The packaging workflow treats these as an all-or-nothing optional group.
