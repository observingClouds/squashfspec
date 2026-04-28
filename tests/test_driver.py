import os
import subprocess
import pytest
from squashfsspec import SquashFSFileSystem


@pytest.fixture
def squashfs_file(tmp_path):
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    subdir = test_dir / "subdir"
    subdir.mkdir()
    
    (test_dir / "file1.txt").write_text("Hello from file 1")
    (subdir / "file2.txt").write_text("Hello from file 2 in subdir")

    filename = tmp_path / "test.squash"
    # Try to find mksquashfs
    try:
        subprocess.run(["mksquashfs", str(test_dir), str(filename), "-noappend"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("mksquashfs not found")
        
    return str(filename)


def test_driver(squashfs_file):
    fs = SquashFSFileSystem(squashfs_file)

    # Listing root
    ls_root = fs.ls("")
    assert any("file1.txt" in item if isinstance(item, str) else "file1.txt" in item["name"] for item in ls_root)

    # Reading file1.txt
    with fs.open("file1.txt", "rb") as f:
        assert f.read().decode() == "Hello from file 1"

    # Reading subdir/file2.txt
    with fs.open("subdir/file2.txt", "rb") as f:
        assert f.read().decode() == "Hello from file 2 in subdir"
