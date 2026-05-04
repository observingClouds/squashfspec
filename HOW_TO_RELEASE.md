# How to Release a New Version

This document describes the steps required to publish a new release of `squashfsspec` to [PyPI](https://pypi.org/project/squashfsspec/).

## Prerequisites

- Write access to the [observingClouds/squashfsspec](https://github.com/observingClouds/squashfsspec) repository.
- All intended changes are merged into `main`.

## Steps

### 1. Update the version number

Bump the version in `pyproject.toml` following [Semantic Versioning](https://semver.org/) (e.g. `0.1.4` → `0.1.5`):

```toml
[project]
version = "0.1.5"
```

### 2. Update the CHANGELOG

Add a new section at the top of `CHANGELOG.md` for the release, following the existing format:

```markdown
## v0.1.5 (YYYY-MM-DD)

### Changes
- Description of what changed ([#PR](https://github.com/observingClouds/squashfsspec/pull/PR))

### Fixes
- Description of what was fixed ([#PR](https://github.com/observingClouds/squashfsspec/pull/PR))
```

### 3. Open and merge a pull request

Commit the version bump and CHANGELOG update in a dedicated branch, open a pull request targeting `main`, and merge it after review.

### 4. Create a GitHub Release

1. Go to **Releases** on the [repository page](https://github.com/observingClouds/squashfsspec/releases).
2. Click **Draft a new release**.
3. Create a new tag matching the version (e.g. `v0.1.5`) targeting `main`.
4. Set the release title to the tag name (e.g. `v0.1.5`).
5. Copy the relevant `CHANGELOG.md` section into the release description.
6. Click **Publish release**.

### 5. Verify the PyPI release

Publishing the GitHub release automatically triggers the [Release workflow](.github/workflows/release.yml), which builds and uploads the package to PyPI using `pdm publish`.

After a few minutes, verify that the new version appears on [https://pypi.org/project/squashfsspec/](https://pypi.org/project/squashfsspec/).
