import os
import subprocess

from squashfspec import SquashFSFileSystem


def create_test_squashfs(filename):
    os.makedirs("test_dir/subdir", exist_ok=True)
    with open("test_dir/file1.txt", "w") as f:
        f.write("Hello from file 1")
    with open("test_dir/subdir/file2.txt", "w") as f:
        f.write("Hello from file 2 in subdir")

    # Try to find mksquashfs
    try:
        subprocess.run(["mksquashfs", "test_dir", filename, "-noappend"], check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("mksquashfs not found, skipping SquashFS creation")
        return False


def test_driver(filename):
    print(f"Testing SquashFS driver with {filename}")
    fs = SquashFSFileSystem(filename)

    print("Listing root:")
    print(fs.ls(""))

    print("\nReading file1.txt:")
    with fs.open("file1.txt", "rb") as f:
        print(f.read().decode())

    print("\nReading subdir/file2.txt:")
    with fs.open("subdir/file2.txt", "rb") as f:
        print(f.read().decode())


if __name__ == "__main__":
    test_file = "test.squash"
    if create_test_squashfs(test_file):
        try:
            test_driver(test_file)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
            import shutil

            if os.path.exists("test_dir"):
                shutil.rmtree("test_dir")
