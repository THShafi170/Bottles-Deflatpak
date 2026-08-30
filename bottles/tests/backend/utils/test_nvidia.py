from bottles.backend.utils import nvidia
from bottles.backend.utils.gpu import GPUUtils, GPUVendors


def test_get_nvidia_dll_path_nixos_fallback(monkeypatch, tmp_path):
    monkeypatch.setattr(GPUUtils, "is_gpu", lambda vendor: vendor == GPUVendors.NVIDIA)

    nvngx_dll = "/run/opengl-driver/lib/nvidia/wine/nvngx.dll"

    def fake_isfile(path):
        return path == nvngx_dll

    monkeypatch.setattr(nvidia.os.path, "isfile", fake_isfile)

    assert nvidia.get_nvidia_dll_path() == "/run/opengl-driver/lib/nvidia/wine"
