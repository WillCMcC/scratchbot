from scratchbot import ScratchbotConfig


def test_config_defaults(tmp_path):
    cfg = ScratchbotConfig.from_file(tmp_path / ".scratchbot.yml")
    assert cfg.commit_mode == "per_file"
    assert cfg.docs_dir == "docs"
    assert cfg.include == []
    assert cfg.exclude == []
    assert cfg.thresholds == {}


def test_config_parsing(tmp_path):
    cfg_file = tmp_path / ".scratchbot.yml"
    cfg_file.write_text(
        """
commit_mode: batch
docs_dir: documentation
include: ["src/**"]
exclude: ["tests/**"]
thresholds:
  loc: 300
  files: 10
""",
        encoding="utf-8",
    )
    cfg = ScratchbotConfig.from_file(cfg_file)
    assert cfg.commit_mode == "batch"
    assert cfg.docs_dir == "documentation"
    assert cfg.include == ["src/**"]
    assert cfg.exclude == ["tests/**"]
    assert cfg.thresholds == {"loc": 300, "files": 10}
