"""Output settings shared by the two official Gradio clients."""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path


def _settings_path(profile: str) -> Path:
    return Path(__file__).resolve().parent.parent / f"{profile}_settings.json"


def load_settings(profile: str) -> dict:
    defaults = {"output_folder": profile, "date_subfolder": False, "save_txt": False}
    try:
        saved = json.loads(_settings_path(profile).read_text(encoding="utf-8"))
        if isinstance(saved.get("output_folder"), str) and saved["output_folder"].strip():
            defaults["output_folder"] = saved["output_folder"]
        for key in ("date_subfolder", "save_txt"):
            if isinstance(saved.get(key), bool):
                defaults[key] = saved[key]
    except (OSError, ValueError, AttributeError):
        pass
    return defaults


def save_settings(profile: str, folder: str, dated: bool, txt: bool) -> None:
    if not str(folder).strip():
        return
    path = _settings_path(profile)
    settings = {"output_folder": str(folder).strip(), "date_subfolder": bool(dated), "save_txt": bool(txt)}
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as f:
            temporary = f.name
            json.dump(settings, f, ensure_ascii=False, indent=2)
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def prepare_output_directory(folder: str, dated: bool, now: datetime) -> Path:
    if not str(folder).strip():
        raise ValueError("出力フォルダを指定してください。")
    path = Path(str(folder).strip()).expanduser().resolve()
    if dated:
        path /= now.strftime("%Y-%m-%d")
    path.mkdir(parents=True, exist_ok=True)
    # Detect permission errors before inference starts.
    with tempfile.TemporaryFile(dir=path):
        pass
    return path


def write_metadata(wav_path: str | Path, metadata: dict) -> Path:
    path = Path(wav_path).with_suffix(".txt")
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def choose_folder(current: str) -> str:
    root = None
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.askdirectory(parent=root, initialdir=str(Path(current).expanduser()) if current else None)
        return selected or current
    except Exception as exc:
        import gradio as gr
        gr.Warning(f"フォルダ選択ダイアログを開けません。パスを直接入力してください。({exc})")
        return current
    finally:
        if root is not None:
            root.destroy()
