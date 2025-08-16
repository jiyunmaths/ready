"""Python utilities for working with OpenCL via PyOpenCL.

This module translates a subset of the C++ implementation found in
``src/readybase/OpenCL_utils.{hpp,cpp}``.
"""

from __future__ import annotations


def IsOpenCLAvailable() -> bool:
    """Return ``True`` if at least one OpenCL device is available.

    The function attempts to enumerate OpenCL platforms and their devices
    using :mod:`pyopencl`.  Any import or runtime errors are treated as
    the absence of OpenCL support.
    """
    try:
        import pyopencl as cl  # type: ignore
    except Exception:
        return False
    try:
        platforms = cl.get_platforms()
    except Exception:
        return False
    for platform in platforms:
        try:
            devices = platform.get_devices()
        except Exception:
            continue
        if devices:
            return True
    return False


def throwOnError(ret: int, message: str) -> None:
    """Raise ``RuntimeError`` if ``ret`` represents an OpenCL error."""
    if ret == 0:
        return
    err_str = str(ret)
    try:
        import pyopencl as cl  # type: ignore
        try:
            err_str = cl.status_code.to_string(ret)  # type: ignore[attr-defined]
        except Exception:
            err_str = str(ret)
    except Exception:
        pass
    raise RuntimeError(f"{message}{err_str}")


def GetOpenCLDiagnostics() -> str:
    """Return a human readable description of the available OpenCL devices."""
    try:
        import pyopencl as cl  # type: ignore
    except Exception as e:
        return f"Failed to import PyOpenCL: {e}"
    try:
        platforms = cl.get_platforms()
    except Exception as e:
        return f"Failed to get OpenCL platforms: {e}"
    if not platforms:
        return "No OpenCL platforms available"
    lines = [f"Found {len(platforms)} platform(s):"]
    for idx, platform in enumerate(platforms, 1):
        name = getattr(platform, "name", "Unknown")
        lines.append(f"Platform {idx}: {name}")
        try:
            devices = platform.get_devices()
        except Exception as e:
            lines.append(f"  Failed to get devices: {e}")
            continue
        if not devices:
            lines.append("  No devices")
            continue
        for jdx, device in enumerate(devices, 1):
            dname = getattr(device, "name", "Unknown")
            lines.append(f"  Device {jdx}: {dname}")
    return "\n".join(lines)
