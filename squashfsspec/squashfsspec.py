# Third-party
import fsspec
from dissect.squashfs import SquashFS
from fsspec.spec import AbstractFileSystem


class SquashFSFileSystem(AbstractFileSystem):
    protocol = "squash"

    def __init__(self, fo=None, offset=0, **kwargs):
        super().__init__(**kwargs)
        if fo is None:
            # Try to get fo from kwargs if passed there
            fo = kwargs.get("fo")

        if fo is None:
            raise ValueError(
                "SquashFSFileSystem requires 'fo' (file-like object or path)"
            )

        if isinstance(fo, str):
            self.fo = fsspec.open(fo, "rb").open()
        else:
            self.fo = fo
        self.offset = offset
        # SquashFS in dissect can take a file-like object
        # We might need to wrap it if it has an offset
        if self.offset != 0:
            # Simple wrapper to handle offset if dissect doesn't
            self.sfs = SquashFS(OffsetWrapper(self.fo, self.offset))
        else:
            self.sfs = SquashFS(self.fo)

    @classmethod
    def _strip_protocol(cls, path):
        path = super()._strip_protocol(path)

        # If the protocol is still there, it's often because
        # fsspec's split_protocol didn't match it or it's nested.
        for proto in ["squashfs://", "squashfs:"]:
            if path.startswith(proto):
                path = path[len(proto) :]
                break

        if "://" in path:
            # Handle cases like some_path://inner_path
            path = path.split("://", 1)[1]

        if not path.startswith("/"):
            path = "/" + path
        return path

    def ls(self, path, detail=True, **kwargs):
        path = self._strip_protocol(path)

        try:
            entry = self.sfs.get(path)
        except Exception:
            raise FileNotFoundError(path)

        if entry.is_dir():
            out = []
            for name, child in entry.listdir().items():
                child_path = (path.rstrip("/") + "/" + name).lstrip("/")
                if detail:
                    out.append(
                        {
                            "name": child_path,
                            "size": child.size if not child.is_dir() else 0,
                            "type": "directory" if child.is_dir() else "file",
                        }
                    )
                else:
                    out.append(child_path)
            return out
        else:
            if detail:
                return [
                    {
                        "name": path.lstrip("/"),
                        "size": entry.size,
                        "type": "file",
                    }
                ]
            return [path.lstrip("/")]

    def info(self, path, **kwargs):
        path = self._strip_protocol(path)
        try:
            entry = self.sfs.get(path)
        except Exception:
            raise FileNotFoundError(path)

        return {
            "name": path.lstrip("/"),
            "size": entry.size if not entry.is_dir() else 0,
            "type": "directory" if entry.is_dir() else "file",
        }

    def exists(self, path, **kwargs):
        path = self._strip_protocol(path)
        try:
            self.sfs.get(path)
            return True
        except Exception:
            return False

    def isdir(self, path):
        path = self._strip_protocol(path)
        try:
            return self.sfs.get(path).is_dir()
        except Exception:
            return False

    def isfile(self, path):
        path = self._strip_protocol(path)
        try:
            return not self.sfs.get(path).is_dir()
        except Exception:
            return False

    def __del__(self):
        if hasattr(self, "fo") and not self.fo.closed:
            self.fo.close()

    def _open(self, path, mode="rb", **kwargs):
        if mode != "rb":
            raise ValueError("ReadOnly filesystem")
        path = self._strip_protocol(path)
        entry = self.sfs.get(path)
        return entry.open()


class OffsetWrapper:
    def __init__(self, fo, offset):
        self.fo = fo
        self.offset = offset

    def seek(self, offset, whence=0):
        if whence == 0:
            return self.fo.seek(self.offset + offset)
        return self.fo.seek(offset, whence)

    def read(self, size=-1):
        return self.fo.read(size)

    def tell(self):
        return self.fo.tell() - self.offset

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        return self.fo.close()
