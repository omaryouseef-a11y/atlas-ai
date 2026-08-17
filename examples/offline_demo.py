"""Run a deterministic Atlas core demonstration without network access."""

from pathlib import Path
import tempfile

from atlas_core.asset_vault import AssetVault
from atlas_core.job_manager import AtlasJobManager
from atlas_core.qa_gate import QualityGate
from providers.dry_run import DryRunProvider


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="atlas-legacy-") as directory:
        db_path = Path(directory) / "atlas.db"
        manager = AtlasJobManager(db_path)
        manager.create_episode("offline-counting-001", "Offline Counting Example", 1.0)
        prompt = "Friends count in a magical green forest, 3D animated and child-safe."
        approved, message = QualityGate(db_path).review_video_prompt(
            "offline-counting-001", prompt
        )
        job_id = manager.start_job(
            "offline-counting-001", "Example", "plan", prompt
        )
        result = DryRunProvider().run("plan")
        manager.complete_job(job_id, "offline-counting-001", result.status)
        AssetVault(db_path).register_asset(
            "story-fixture", "story", "Offline story", "examples/story.md"
        )
        print(f"QA: {approved} ({message})")
        print(f"Provider: {result.status}; output created: {result.output_created}")
        print(f"Completed jobs: {manager.get_episode_stats('offline-counting-001')['completed_jobs']}")


if __name__ == "__main__":
    main()
