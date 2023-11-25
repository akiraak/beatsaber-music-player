# BeatSaber 音楽プレイヤー

BeatSaber 音楽プレイヤーは、BeatSaverからBeatSaberの曲をダウンロードし、ローカルで再生するためのPythonスクリプトです。このスクリプトは、BeatSaverのAPIを利用して特定のBSR IDに基づいた音楽ファイルを検索し、ダウンロードしてMP3形式に変換した後、再生します。

## 機能

- BeatSaver APIを利用してBeatSaberの曲の詳細を取得
- 指定されたBSR IDに基づいて音楽ファイルをダウンロード
- ダウンロードしたファイルをMP3形式に変換
- 変換したMP3ファイルをローカルで再生

## 前提条件

- Python 3.x
- `requests` ライブラリ（HTTPリクエスト用）
- `pydub` ライブラリ（音声ファイルの操作用）
- `ffmpeg`（`pydub`のバックエンドとして必要）

## インストール方法

1. 必要なライブラリをインストールします。
   ```
   pip install -r requirements.txt
   ```

2. `ffmpeg`をシステムにインストールします。インストール方法はお使いのOSによって異なります。

## 使用方法

   ```
   python music_player.py --bsr [BSR ID]
   ```
   `[BSR ID]` には、再生したい曲のBSR IDを指定します。
