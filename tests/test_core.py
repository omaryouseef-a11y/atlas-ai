from atlas_core.asset_vault import AssetVault
from atlas_core.job_manager import AtlasJobManager
from atlas_core.qa_gate import QualityGate
from examples.offline_demo import main as offline_main


def test_job_lifecycle_and_duplicate_prevention(tmp_path):
    manager = AtlasJobManager(tmp_path / "atlas.db")
    manager.create_episode("episode-1", "Example", 5.0)
    job_id = manager.start_job("episode-1", "Video", "plan", "same input")
    assert manager.check_job_exists("episode-1", "Video", "plan", "same input") is None
    manager.complete_job(job_id, "episode-1", "DRY_RUN", cost=0.0)
    assert manager.check_job_exists("episode-1", "Video", "plan", "same input") == "DRY_RUN"
    stats = manager.get_episode_stats("episode-1")
    assert stats["completed_jobs"] == 1
    assert stats["failed_jobs"] == 0


def test_qa_gate_and_budget(tmp_path):
    db_path = tmp_path / "atlas.db"
    manager = AtlasJobManager(db_path)
    manager.create_episode("episode-1", "Example", 1.0)
    gate = QualityGate(db_path)
    accepted, _ = gate.review_video_prompt(
        "episode-1", "A magical green forest scene, 3D animated and child-safe"
    )
    rejected, _ = gate.review_video_prompt("episode-1", "A generic scene")
    assert accepted is True
    assert rejected is False


def test_asset_registry(tmp_path):
    vault = AssetVault(tmp_path / "atlas.db")
    assert vault.register_asset("story-1", "story", "Fixture", "examples/story.md")
    assert vault.get_asset("story-1")[2] == "Fixture"
    assert len(vault.list_assets("story")) == 1


def test_offline_example(capsys):
    offline_main()
    output = capsys.readouterr().out
    assert "Provider: DRY_RUN" in output
    assert "output created: False" in output
