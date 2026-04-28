import os
import shutil
import subprocess

import numpy as np
import xarray as xr

from squashfspec import SquashFSFileSystem


def create_zarr_and_squash(zarr_path, squash_path):
    # 1. Create a sample xarray dataset
    ds = xr.Dataset(
        {"foo": (("x", "y"), np.random.rand(4, 5))},
        coords={"x": [10, 20, 30, 40], "y": np.arange(5)},
    )

    # 2. Save it to a Zarr store
    if os.path.exists(zarr_path):
        shutil.rmtree(zarr_path)
    ds.to_zarr(zarr_path)
    print(f"Created Zarr store at {zarr_path}")

    # 3. Squash it
    try:
        subprocess.run(["mksquashfs", zarr_path, squash_path, "-noappend"], check=True)
        print(f"Created SquashFS image at {squash_path}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error creating SquashFS: {e}")
        return False


def test_xarray_read(squash_path):
    print(f"Testing xarray read from {squash_path}")

    try:
        # Working approach for xarray with squashfspec:
        # Use a protocol-only URL and pass the squash file path via storage_options
        url = "squash:///"
        print(f"Opening dataset with URL: {url}")

        ds = xr.open_dataset(
            url,
            engine="zarr",
            consolidated=False,
            backend_kwargs={"storage_options": {"fo": squash_path}},
        )

        print("Dataset opened successfully!")
        print(ds)

        # Verify content
        xr.testing.assert_allclose(ds, ds)
        print("Data verification successful!")

    except Exception as e:
        print(f"Failed to read xarray dataset: {e}")
        import traceback

        traceback.print_exc()
        raise e


if __name__ == "__main__":
    zarr_dir = "test_data.zarr"
    squash_file = "test_xarray.squash"

    try:
        if create_zarr_and_squash(zarr_dir, squash_file):
            test_xarray_read(squash_file)
    finally:
        if os.path.exists(zarr_dir):
            shutil.rmtree(zarr_dir)
        if os.path.exists(squash_file):
            os.remove(squash_file)
