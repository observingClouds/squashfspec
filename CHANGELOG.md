# CHANGELOG

## Unreleased

### Enhancements

- Add `__del__` and context manager (`__enter__`/`__exit__`) support to `SquashFSFileSystem` to ensure `fo` is properly closed on garbage collection and when used in a `with` statement ([#19](https://github.com/observingClouds/squashfsspec/pull/19))

## v0.1.1 (2026-04-29)

### Tests

- Add tests for README code examples, extracting code blocks directly from `README.md` to keep documentation and tests in sync ([#15](https://github.com/observingClouds/squashfsspec/pull/15))

### Documentation

- Fix protocol name in README: `fsspec.filesystem("squash", ...)` → `fsspec.filesystem("squashfs", ...)` ([#15](https://github.com/observingClouds/squashfsspec/pull/15))
- Fix `consolidated=False` → `consolidated=True` in the *Accessing Multiple Datasets* README example ([#15](https://github.com/observingClouds/squashfsspec/pull/15))
- Remove unused `from squashfsspec import SquashFSFileSystem` import from README usage example ([#16](https://github.com/observingClouds/squashfsspec/pull/16))

### Dependencies

- `[actions/checkout](https://github.com/actions/checkout)`: 4 → 6 ([#3](https://github.com/observingClouds/squashfsspec/pull/3))
- `[peter-evans/create-pull-request](https://github.com/peter-evans/create-pull-request)`: 7 → 8 ([#2](https://github.com/observingClouds/squashfsspec/pull/2))
- `[prefix-dev/setup-pixi](https://github.com/prefix-dev/setup-pixi)`: 0.8.1 → 0.9.5 ([#1](https://github.com/observingClouds/squashfsspec/pull/1))

## v0.1.0 Initial release (2026-04-28)

This is the initial release with the basic functionality implemented to read squashfs files with fsspec.
