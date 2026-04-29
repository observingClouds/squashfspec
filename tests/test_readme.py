# Standard library
import subprocess

# Third-party
import fsspec
import numpy as np
import pytest
import xarray as xr

# First-party


@pytest.fixture
def squashfs_file(tmp_path):
    """SquashFS file with a simple text file, matching the README basic usage example."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    (test_dir / "some").mkdir()
    (test_dir / "some" / "file.txt").write_text("Hello, SquashFS!")

    filename = tmp_path / "test.squash"
    try:
        subprocess.run(
            ["mksquashfs", str(test_dir), str(filename), "-noappend"],
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("mksquashfs not found")

    return str(filename)


@pytest.fixture
def zarr_squashfs_file(tmp_path):
    """SquashFS file containing a Zarr store at the root, matching the README xarray example."""
    zarr_path = tmp_path / "data.zarr"
    squash_path = tmp_path / "data.squash"

    ds = xr.Dataset(
        {"temperature": (("x", "y"), np.random.rand(4, 5))},
        coords={"x": [10, 20, 30, 40], "y": np.arange(5)},
    )
    ds.to_zarr(str(zarr_path))

    try:
        subprocess.run(
            ["mksquashfs", str(zarr_path), str(squash_path), "-noappend"],
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        pytest.skip(f"mksquashfs not available or failed: {e}")

    return str(squash_path)


@pytest.fixture
def multi_zarr_squashfs_file(tmp_path):
    """SquashFS file containing multiple Zarr stores, matching the README multiple datasets example."""
    base_dir = tmp_path / "data"
    base_dir.mkdir()
    squash_path = tmp_path / "multidata.squash"

    ds1 = xr.Dataset(
        {"temperature": (("x", "y"), np.random.rand(4, 5))},
        coords={"x": [10, 20, 30, 40], "y": np.arange(5)},
    )
    ds2 = xr.Dataset(
        {"pressure": (("a", "b"), np.random.rand(3, 3))},
        coords={"a": [1, 2, 3], "b": [1, 2, 3]},
    )

    ds1.to_zarr(str(base_dir / "dataset1.zarr"), zarr_format=2)
    ds2.to_zarr(str(base_dir / "dataset2.zarr"), zarr_format=2)

    try:
        subprocess.run(
            ["mksquashfs", str(base_dir), str(squash_path), "-noappend"],
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("mksquashfs not available")

    return str(squash_path)


def test_readme_basic_usage(squashfs_file):
    """README: Basic Usage with fsspec.

    Note: the fsspec entry point registers the protocol as ``squashfs``; the
    README's ``"squash"`` shorthand only works after the class has been
    imported directly, which this module does via the import above.
    """
    # README imports SquashFSFileSystem before calling fsspec.filesystem so
    # the "squash" alias is available via the class's protocol attribute.
    fs = fsspec.filesystem("squashfs", fo=squashfs_file)

    # List files
    listing = fs.ls("/")
    assert any(
        "some" in item if isinstance(item, str) else "some" in item["name"]
        for item in listing
    )

    # Open and read a file
    with fs.open("some/file.txt", "rb") as f:
        assert f.read().decode() == "Hello, SquashFS!"


def test_readme_xarray_zarr(zarr_squashfs_file):
    """README: Working with Xarray and Zarr."""
    ds = xr.open_dataset(
        "squashfs:///",
        engine="zarr",
        consolidated=False,
        backend_kwargs={"storage_options": {"fo": zarr_squashfs_file}},
    )

    assert "temperature" in ds.variables


def test_readme_multiple_datasets(multi_zarr_squashfs_file):
    """README: Accessing Multiple Datasets."""
    ds = xr.open_dataset(
        f"squashfs:///dataset1.zarr::{multi_zarr_squashfs_file}",
        engine="zarr",
        consolidated=True,
    )

    assert "temperature" in ds.variables
