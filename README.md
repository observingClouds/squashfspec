# SquashFSpec

[![Tests](https://github.com/haukeschulz/squashfspec/actions/workflows/test.yaml/badge.svg)](https://github.com/haukeschulz/squashfspec/actions/workflows/test.yaml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple [fsspec](https://filesystem-spec.readthedocs.io/) driver for reading [SquashFS](https://en.wikipedia.org/wiki/SquashFS) files.

SquashFSpec allows you to treat a SquashFS image as a filesystem, enabling seamless integration with tools like `xarray`, `dask`, and `zarr` without needing to mount the image.

## Installation

You can install `squashfspec` via pip from GitHub:

```bash
pip install git+https://github.com/observingClouds/squashfspec.git
```

Or using [pixi](https://pixi.sh/):

```bash
pixi add squashfspec --git https://github.com/observingClouds/squashfspec.git
```

## Usage

### Basic Usage with fsspec

```python
import fsspec
from squashfspec import SquashFSFileSystem

# Open a SquashFS file
fs = fsspec.filesystem("squash", fo="path/to/your.squash")

# List files
print(fs.ls("/"))

# Open and read a file
with fs.open("some/file.txt", "rb") as f:
    print(f.read().decode())
```

### Working with Xarray and Zarr

If you have a Zarr store inside a SquashFS image, you can open it directly with `xarray`:

```python
import xarray as xr

# Open a Zarr store inside a SquashFS file
ds = xr.open_dataset(
    "squash:///",
    engine="zarr",
    consolidated=False,  # Set to True if your Zarr store is consolidated
    backend_kwargs={
        "storage_options": {"fo": "path/to/data.squash"}
    },
)

print(ds)
```

### Accessing Multiple Datasets

If your SquashFS image contains multiple Zarr stores or datasets, you can access them by specifying the internal path:

```python
import xarray as xr

# Open a specific dataset inside a SquashFS file containing multiple datasets
ds = xr.open_dataset(
    "squash:///path/to/dataset.zarr",
    engine="zarr",
    consolidated=False,
    backend_kwargs={
        "storage_options": {"fo": "path/to/multidata.squash"}
    },
)

print(ds)
```

## Development

This project uses [pixi](https://pixi.sh/) for dependency management and development workflows.

### Setup

```bash
# Install dependencies and setup the dev environment
pixi install -e dev
```

### Running Tests

```bash
# Run core driver tests
pixi run test

# Run xarray integration tests
pixi run test-xarray
```

## License

This project is licensed under the MIT License.
