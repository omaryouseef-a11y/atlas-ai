from pathlib import Path

import pytest

from atlas_core.paths import safe_child
from config_manager import ConfigManager


def test_configuration_round_trip(tmp_path):
    manager = ConfigManager(tmp_path / "configs")
    path = manager.create_episode_config(
        "episode-1", "Example", "Counting", ["Sokkar"], num_scenes=1
    )
    assert Path(path).is_file()
    assert manager.load_config("episode-1")["episode"]["title"] == "Example"


@pytest.mark.parametrize("bad_id", ["../outside", "/tmp/outside", "a/b", "", "a..b"])
def test_episode_id_rejects_unsafe_values(tmp_path, bad_id):
    manager = ConfigManager(tmp_path / "configs")
    with pytest.raises(ValueError):
        manager.load_config(bad_id)


def test_safe_child_rejects_symlink_escape(tmp_path):
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (root / "escape").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError):
        safe_child(root, "escape", "file.txt")
