import torch


def test_mps_available():
    assert torch.backends.mps.is_available(), "MPS (Apple M1 GPU) não disponível"


def test_device_is_mps():
    device = torch.device("mps")
    tensor = torch.tensor([1.0]).to(device)
    assert str(tensor.device) == "mps:0"
