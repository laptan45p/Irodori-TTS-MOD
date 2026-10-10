# Irodori-TTS MOD

[公式Irodori-TTS](https://github.com/Aratako/Irodori-TTS) のGradio UI向け、非公式の差し替えファイルです。このリポジトリには公式ソース全体・モデルの重みを含めていません。

## 追加機能

- 任意の出力フォルダ指定（参照ボタン・パス入力）
- `yyyy-MM-dd`の日付別フォルダ作成をON/OFF
- Text、実際のSeed、モデル・話者指定、生成条件をWAVと同名のUTF-8 TXTに保存（ON/OFF）
- 生成条件TXTを読み込んでText・実際のSeed・モデル・生成パラメータをUIへ復元
- 保存設定を次回起動へ引き継ぎ
- 通常版・VoiceDesign版にMOD表示
- 両UIの既定モデル: `Aratako/Irodori-TTS-v4-Large-Quantized/int8-weight-only`
- Model Precision初期値: CUDAは`bf16`、その他は`fp32`

## 導入

1. [公式リポジトリ](https://github.com/Aratako/Irodori-TTS) の手順で環境を構築してください。
2. 起動中のGradioを終了し、既存の以下2ファイルをバックアップしてください。
3. 本リポジトリから以下3ファイルを取得し、公式Irodori-TTSフォルダに同じ階層で上書き・追加してください。

```text
gradio_app.py
gradio_app_voicedesign.py
irodori_tts/output_settings.py
```

4. 従来どおり起動してください。追加のpipインストールは不要です。

```bash
# 通常版
uv run --no-sync python gradio_app.py
# VoiceDesign版
uv run --no-sync python gradio_app_voicedesign.py
```

対象の公式コミット: `89f9d8fbd4d51ea019867ee1197725ede1df13c5`
旧バージョン・将来のバージョンとの互換性は保証しません。

## 保存設定

Generateの上の「Output Settings / 出力設定」で指定します。初期状態では従来の保存先・両チェックOFFです。
設定はアプリフォルダのJSONに保存され、実行環境の利用者間で共有されます。

- 保存先は実行PC/サーバーのフォルダです。RunPod等ではサーバー上のパスを入力してください。
- 「参照」は実行PCのデスクトップにダイアログを開きます。ヘッドレス・Tkinter未導入環境では直接パス入力を使用してください。
- 日付は実行PC/サーバーのローカル日時です。
- TXTは読みやすいJSON形式です。自動指定のパラメータは`null`として記録します。
- Seedは候補バッチ全体のSeedです。参照音声・話者埋め込み本体は同梱しません。
- 設定保存にはアプリフォルダへの書き込み権限が必要です。
- CUDA以外で`fp32`を初期設定する処理はありますが、量子化モデルの非CUDA動作は未検証です。

## 検証

構文、コールバック配線、任意/日付別フォルダ、日本語TXT、設定保存・再読み込み、既定モデルと精度の分岐を確認済みです。
GPU音声生成とWindowsのフォルダ選択ダイアログはこの環境では未検証です。

## ライセンス

コードはMITライセンスです。元の著作権表示と[LICENSE](LICENSE)を保持しています。
モデルの利用・再配布には[モデルカード](https://huggingface.co/Aratako/Irodori-TTS-v4-Large-Quantized)に記載されたGemma利用規約・追加条件が適用されます。

## 生成条件の読み込み（MOD v1.1）

「Load Generation Settings / 生成条件の読み込み」で、このMODが保存したTXTを選び「生成条件を復元」を押します。
ランダム生成時も実際に使用したSeedを戻します。従来のTXTも対応し、含まれない項目は変更しません。
デバイス・精度・保存先は現在の設定を維持します。参照音声・話者埋め込みは自動読み込みしないため、必要なファイルを再指定してください。
旧TXTのモデル指定は解決済みのローカルパスです。別PCで使用する場合はモデル欄を再指定してください。v1.1以降のTXTには入力したモデル指定も保存します。
同じ音声の再現にはモデル、参照ファイル、環境等も揃える必要があり、TXTだけで完全一致を保証するものではありません。
