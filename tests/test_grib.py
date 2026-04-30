# Standard library
import shutil
import subprocess

# Third-party
import fsspec
import pytest
import xarray as xr

GRIB_FILENAME = "era5-2mt-2019-03-uk.grib"
GRIB_URL = f"https://github.com/pydata/xarray-data/raw/master/{GRIB_FILENAME}"


@pytest.fixture(scope="session")
def grib_source_file():
    """Download and cache the ERA5 tutorial GRIB file using pooch."""
    pooch = pytest.importorskip("pooch")
    pytest.importorskip("cfgrib")

    try:
        path = pooch.retrieve(
            url=GRIB_URL,
            known_hash=None,
            path=pooch.os_cache("xarray_tutorial_data"),
            fname=GRIB_FILENAME,
        )
    except Exception as e:
        pytest.skip(f"Could not download tutorial GRIB file: {e}")

    return path


@pytest.fixture
def grib_squash(tmp_path, grib_source_file):
    """Pack the tutorial GRIB file into a squashfs archive."""
    grib_dir = tmp_path / "grib_data"
    grib_dir.mkdir()
    shutil.copy2(grib_source_file, grib_dir / GRIB_FILENAME)

    squash_path = tmp_path / "test_grib.squash"
    try:
        subprocess.run(
            ["mksquashfs", str(grib_dir), str(squash_path), "-noappend"],
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        pytest.skip(f"mksquashfs not available or failed: {e}")

    return str(squash_path)


def test_grib_read(grib_squash, grib_source_file, tmp_path):
    """Read a GRIB file stored in squashfs using xarray with cfgrib engine."""
    url = f"squashfs:///{GRIB_FILENAME}::{grib_squash}"
    with fsspec.open(url, "rb") as f:
        data = f.read()

    tmp_grib = tmp_path / GRIB_FILENAME
    tmp_grib.write_bytes(data)

    ds_squash = xr.open_dataset(str(tmp_grib), engine="cfgrib", indexpath="")
    ds_direct = xr.open_dataset(grib_source_file, engine="cfgrib", indexpath="")

    xr.testing.assert_identical(ds_squash, ds_direct)
