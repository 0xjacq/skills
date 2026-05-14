import filecmp
from pathlib import Path


def test_synced_runtime_matches_internal_source():
    repo_root = Path(__file__).resolve().parents[1]
    internal_root = repo_root / "skills" / "tools" / "_internal" / "python_runtime"
    for skill_name in ["build-or-not", "find-tools"]:
        scripts_root = repo_root / "skills" / "tools" / skill_name / "scripts"
        for package_name in ["diligence", "prebuild_engine"]:
            comparison = filecmp.dircmp(internal_root / package_name, scripts_root / package_name)
            assert comparison.left_only == []
            assert comparison.right_only == []
            assert comparison.diff_files == []
