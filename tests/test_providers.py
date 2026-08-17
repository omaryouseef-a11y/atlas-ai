import pytest

from atlas_core.settings import api_bind_host
from providers.dry_run import DryRunProvider
from providers.gemini import create_crewai_llm
from video_engine import ProviderUnavailableError, VideoEngine


def test_dry_run_creates_no_output(tmp_path):
    output = tmp_path / "clip.mp4"
    result = DryRunProvider().run("video")
    assert result.status == "DRY_RUN"
    assert result.output_created is False
    assert not output.exists()


def test_video_dry_run_creates_no_fake_media(tmp_path):
    output = tmp_path / "clip.mp4"
    path, cost = VideoEngine(dry_run=True).generate_video("fixture", output)
    assert path is None
    assert cost == 0
    assert not output.exists()


def test_missing_video_provider_fails_clearly(monkeypatch):
    monkeypatch.setattr("video_engine.FAL_API_KEY", None)
    with pytest.raises(ProviderUnavailableError, match="PROVIDER_UNAVAILABLE"):
        VideoEngine().generate_video("fixture", "unused.mp4")


def test_missing_gemini_provider_fails_clearly(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="NOT_CONFIGURED"):
        create_crewai_llm()


def test_api_defaults_to_loopback(monkeypatch):
    monkeypatch.delenv("ATLAS_API_HOST", raising=False)
    assert api_bind_host() == "127.0.0.1"
    monkeypatch.setenv("ATLAS_API_HOST", "0.0.0.0")
    with pytest.raises(ValueError, match="loopback"):
        api_bind_host()
