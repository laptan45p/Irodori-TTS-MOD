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


def read_metadata(path: str | None) -> dict:
    """Read our UTF-8 JSON sidecar without accessing referenced local files."""
    if not path:
        raise ValueError("生成条件のTXTを選択してください。")
    source = Path(path)
    if source.stat().st_size > 2 * 1024 * 1024:
        raise ValueError("TXTが大きすぎます（上限2 MiB）。")
    try:
        data = json.loads(source.read_text(encoding="utf-8-sig"))
    except (UnicodeError, ValueError) as exc:
        raise ValueError("このMODが保存したJSON形式のTXTを選択してください。") from exc
    if not isinstance(data, dict) or not isinstance(data.get("generation"), dict):
        raise ValueError("generationを含む生成条件TXTではありません。")
    if not isinstance(data.get("runtime", {}), dict):
        raise ValueError("runtimeの形式が不正です。")
    for key, value in data["generation"].items():
        if value is not None and not isinstance(value, (str, int, float, bool, list)):
            raise ValueError(f"生成条件の形式が不正です: {key}")
    return data


def restored_values(data: dict, names: list[str]) -> list[tuple[bool, object]]:
    """Return presence/value pairs, leaving absent fields unchanged."""
    generation = data["generation"]
    runtime = data.get("runtime", {})
    result = []
    for name in names:
        key = name.removesuffix("_raw")
        if name == "checkpoint":
            value = data.get("source_checkpoint", runtime.get("checkpoint"))
            present = value is not None
        elif name == "seed_raw" and "seed_used" in data:
            value, present = data["seed_used"], True
        else:
            present = key in generation
            value = generation.get(key)
        if present:
            if name.endswith("_raw") or name in ("num_steps", "caption"):
                if value is not None and not isinstance(value, (str, int, float)):
                    raise ValueError(f"生成条件の型が不正です: {key}")
                value = "" if value is None else str(value)
            elif name == "context_kv_cache":
                if not isinstance(value, bool):
                    raise ValueError("context_kv_cacheは真偽値で指定してください。")
            elif name in ("checkpoint", "text", "t_schedule_mode", "cfg_guidance_mode"):
                if not isinstance(value, str):
                    raise ValueError(f"生成条件の型が不正です: {key}")
            elif not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"生成条件の型が不正です: {key}")
            if key == "num_candidates" and (not isinstance(value, int) or not 1 <= value <= 32):
                raise ValueError("候補数は1〜32です。")
            if key == "t_schedule_mode" and value not in ("linear", "sway"):
                raise ValueError("t_schedule_modeが不正です。")
            if key == "cfg_guidance_mode" and value not in ("independent", "joint", "alternating"):
                raise ValueError("cfg_guidance_modeが不正です。")
        result.append((present, value))
    return result
