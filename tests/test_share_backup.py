"""Persistence-focused tests for the local sharing history."""

from pathlib import Path

from model.file import FileModel
from model.share import FuseSharingModel
from settings import settings


def test_share_backup_round_trip_preserves_existing_path_records(
    tmp_path: Path, monkeypatch
):
    shared_file = tmp_path / "report.txt"
    shared_file.write_text("report", encoding="utf-8")
    monkeypatch.setattr(settings, "BASE_DIR", tmp_path)

    shares = FuseSharingModel()
    shares.append(FileModel(shared_file, "h-report"))
    shares.dump()

    restored = FuseSharingModel.load()

    assert len(restored) == 1
    assert restored[0].targetPath == shared_file
    assert restored[0].rowIndex == 0


def test_share_backup_ignores_missing_paths(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "BASE_DIR", tmp_path)
    backup = tmp_path / "file_sharing_backups.json"
    backup.write_text(
        '[{"path": "missing.txt", "uuid": "h-missing", "share_type": "http"}]',
        encoding="utf-8",
    )

    assert FuseSharingModel.load() == []
