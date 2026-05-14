import filecmp
from pathlib import Path


def assert_matching_trees(left: Path, right: Path) -> None:
    comparison = filecmp.dircmp(left, right)
    assert comparison.left_only == []
    assert comparison.right_only == []
    assert comparison.diff_files == []
    assert comparison.funny_files == []

    for common_dir in comparison.common_dirs:
        assert_matching_trees(left / common_dir, right / common_dir)


def test_synced_runtime_matches_internal_source():
    repo_root = Path(__file__).resolve().parents[1]
    internal_root = repo_root / "skills" / "tools" / "_internal" / "python_runtime"
    for skill_name in ["build-or-not", "find-tools"]:
        scripts_root = repo_root / "skills" / "tools" / skill_name / "scripts"
        for package_name in ["diligence", "prebuild_engine"]:
            assert_matching_trees(internal_root / package_name, scripts_root / package_name)
