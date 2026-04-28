import os
import shutil
import subprocess
import numpy as np
import xarray as xr
import pytest
from squashfspec import SquashFSFileSystem
from fsspec import register_implementation

def create_multi_zarr_squash(base_dir, squash_path):
    # 1. Create multiple sample xarray datasets
    ds1 = xr.Dataset(
        {"foo": (("x", "y"), np.random.rand(4, 5))},
        coords={"x": [10, 20, 30, 40], "y": np.arange(5)},
    )
    ds2 = xr.Dataset(
        {"bar": (("a", "b"), np.random.rand(3, 3))},
        coords={"a": [1, 2, 3], "b": [1, 2, 3]},
    )

    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)

    # 2. Save them to Zarr stores in subdirectories
    ds1.to_zarr(os.path.join(base_dir, "ds1.zarr"), zarr_format=2)
    ds2.to_zarr(os.path.join(base_dir, "ds2.zarr"), zarr_format=2)
    
    print(f"Created multiple Zarr stores in {base_dir}")

    # 3. Squash the entire directory
    try:
        subprocess.run(["mksquashfs", base_dir, squash_path, "-noappend"], check=True)
        print(f"Created SquashFS image at {squash_path}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error creating SquashFS: {e}")
        return False

def test_multi_zarr_read():
    base_dir = "test_multi_zarr"
    squash_file = "test_multi.squash"

    try:
        if not create_multi_zarr_squash(base_dir, squash_file):
            pytest.skip("mksquashfs not available")

        # Inspect root
        fs = SquashFSFileSystem(squash_file)
        print(f"Root contents: {fs.ls('')}")
        print(f"ds1.zarr contents: {fs.ls('ds1.zarr')}")

        # Test reading ds1.zarr
        url1 = "squash:///ds1.zarr"
        ds1_read = xr.open_dataset(
            url1,
            engine="zarr",
            consolidated=True,
            backend_kwargs={"storage_options": {"fo": squash_file}},
        )
        assert "foo" in ds1_read.variables
        print("ds1.zarr read successfully from squashfs")

        # Test reading ds2.zarr
        url2 = "squash:///ds2.zarr"
        ds2_read = xr.open_dataset(
            url2,
            engine="zarr",
            consolidated=True,
            backend_kwargs={"storage_options": {"fo": squash_file}},
        )
        assert "bar" in ds2_read.variables
        print("ds2.zarr read successfully from squashfs")

    finally:
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)
        if os.path.exists(squash_file):
            os.remove(squash_file)

if __name__ == "__main__":
    test_multi_zarr_read()
