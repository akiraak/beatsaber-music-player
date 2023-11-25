import argparse
import glob
import os
import shutil
import zipfile

from pydub import AudioSegment
from pydub.playback import play
import requests


# 一時的なファイルと音楽ファイルの保存先ディレクトリを定義
TEMP_DIR = "./temp"
MUSIC_DIR = "./musics"


# MP3ファイル名を生成（BSR IDと曲名を基に）
def sanitize_mp3_name(bsr_id: str, name: str) -> str:
    return f"{bsr_id}_{name.replace(' ', '_').replace('/', '_')[:20]}.mp3"


# MP3ファイルのパスを取得
def get_mp3_path(bsr_id: str, name: str) -> str:
    return os.path.join(MUSIC_DIR, sanitize_mp3_name(bsr_id, name))


# 既存の音楽ファイルを検索
def find_existing_music(bsr_id: str) -> str:
    print(f"Searching for existing music for BSR ID {bsr_id}")
    pattern = os.path.join(MUSIC_DIR, f"{bsr_id}*.mp3")
    files = glob.glob(pattern)
    return files[0] if files else None


# ファイルをダウンロード
def download_file(url: str, path: str) -> bool:
    print(f"Downloading {url} to {path}")
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, "wb") as file:
            file.write(response.content)
        return True
    return False


# BeatSaverからBSR詳細を取得
def fetch_bsr_details(bsr_id: str) -> dict:
    url = f"https://api.beatsaver.com/maps/id/{bsr_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# BSRのZIPファイルを処理
def process_bsr_zip(bsr_id: str, zip_url: str, music_name: str) -> str:
    print(f"Processing BSR ZIP for BSR ID {bsr_id}")
    bsr_dir = os.path.join(TEMP_DIR, bsr_id)
    os.makedirs(bsr_dir, exist_ok=True)

    zip_path = os.path.join(bsr_dir, f"{bsr_id}.zip")
    if download_file(zip_url, zip_path):
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(bsr_dir)
        egg_files = glob.glob(os.path.join(bsr_dir, "*.egg"))
        if egg_files:
            print(f"Converting {egg_files[0]} to MP3")
            ogg_path = os.path.join(bsr_dir, f"{bsr_id}.ogg")
            os.rename(egg_files[0], ogg_path)
            mp3_path = get_mp3_path(bsr_id, music_name)
            AudioSegment.from_ogg(ogg_path).export(mp3_path, format="mp3")
            return mp3_path
    return None


# BSR IDに基づいて音楽を取得する
def get_bsr_music(bsr_id: str) -> str:
    existing_path = find_existing_music(bsr_id)
    if existing_path:
        return existing_path

    bsr_details = fetch_bsr_details(bsr_id)
    if not bsr_details:
        return None

    mp3_path = process_bsr_zip(
        bsr_id, bsr_details["versions"][0]["downloadURL"], bsr_details["name"]
    )
    shutil.rmtree(os.path.join(TEMP_DIR, bsr_id), ignore_errors=True)
    return mp3_path


# 音楽を再生する
def play_music(bsr_id: str):
    music_path = get_bsr_music(bsr_id)
    if music_path:
        song = AudioSegment.from_mp3(music_path)
        play(song)
    else:
        print(f"Failed to play music for BSR ID {bsr_id}")


# メイン関数
def main():
    # 一時作業ディレクトリと音楽保存ディレクトリを作成
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(MUSIC_DIR, exist_ok=True)

    # コマンドライン引数からbsr IDを取得
    parser = argparse.ArgumentParser(description="BeatSaber Music Player")
    parser.add_argument("--bsr", type=str, required=True, help="bsr ID")
    args = parser.parse_args()

    # 音楽の再生
    play_music(args.bsr)


if __name__ == "__main__":
    main()
