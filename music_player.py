import argparse
import glob
import os
import shutil
import zipfile

from pydub import AudioSegment
from pydub.playback import play

import requests


TEMP_DIR = "./temp"
MUSIC_DIR = "./musics"


def mp3_sanitized_name(bsr_id: str, name: str):
    return f"{bsr_id}_{name.replace(' ', '_').replace('/', '_')[:20]}.mp3"


def mp3_path(bsr_id: str, name: str):
    return os.path.join(MUSIC_DIR, mp3_sanitized_name(bsr_id, name))


def check_if_music_exists(bsr_id: str):
    search_pattern = os.path.join(MUSIC_DIR, f"{bsr_id}*.mp3")
    matching_files = glob.glob(search_pattern)
    return matching_files[0] if matching_files else None


def get_bsr_music(bsr_id: str):
    mp3_file_path = check_if_music_exists(bsr_id=bsr_id)
    if mp3_file_path:
        print(f"Found already {bsr_id}: {mp3_file_path}")
        return mp3_file_path

    bsr_url = f"https://api.beatsaver.com/maps/id/{bsr_id}"

    response = requests.get(bsr_url)
    if not response.status_code == 200:
        print(f"! Failed to download {bsr_id} from {bsr_url}")
        return None

    bsr = response.json()
    print(f"Fetched {bsr_id}: {bsr['name']}")

    mp3_file_name = mp3_sanitized_name(bsr_id=bsr_id, name=bsr["name"])
    mp3_file_path = mp3_path(bsr_id=bsr_id, name=bsr["name"])

    # bsr用の一時作業ディレクトリを作成
    bsr_dir = os.path.join(TEMP_DIR, bsr_id)
    if not os.path.exists(bsr_dir):
        os.makedirs(bsr_dir)

    zip_file_path = os.path.join(bsr_dir, f"{bsr_id}.zip")
    zip_url = bsr["versions"][0]["downloadURL"]

    # zipファイルをダウンロード
    response = requests.get(zip_url)
    if response.status_code == 200:
        # zipファイルを保存
        with open(zip_file_path, 'wb') as file:
            file.write(response.content)
        print(f"  Downloaded {bsr_id} to {zip_file_path}")

        # zipファイルを解凍
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(bsr_dir)
        print(f"  Extracted {bsr_id} in {bsr_dir}")

        egg_files = glob.glob(os.path.join(bsr_dir, "*.egg"))
        if egg_files:
            #　eggファイルをoggファイルにリネーム
            ogg_file_path = os.path.join(bsr_dir, f"{bsr_id}.ogg")
            os.rename(egg_files[0], ogg_file_path)
            print(f"  Renamed {egg_files[0]} to {bsr_id}.ogg")

            # oggファイルをmp3ファイルに変換
            AudioSegment.from_ogg(ogg_file_path).export(mp3_file_path, format="mp3")
            print(f"  Converted {bsr_id}.ogg to {mp3_file_name} and moved to {MUSIC_DIR}")
    else:
        print(f"! Failed to download {bsr_id} from {zip_url}")

    # 一時作業ディレクトリを削除
    shutil.rmtree(bsr_dir)
    print(f"  Removed directory and contents: {bsr_dir}")

    return mp3_file_path


def bsr_music_play(bsr_id: str):
    print("Playing music with bsr_id: {}".format(bsr_id))

    music_path = get_bsr_music(bsr_id=bsr_id)
    print(f"  music_path: {music_path}")

    if music_path:
        # Load the audio file
        song = AudioSegment.from_mp3(music_path)
        # Play the audio file
        play(song)
    else:
        print("Failed to play music")


def main():
    # 一時作業ディレクトリを作成
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    # 音楽ファイルを保存するディレクトリを作成
    if not os.path.exists(MUSIC_DIR):
        os.makedirs(MUSIC_DIR)

    parser = argparse.ArgumentParser(description="BeatSaber Music Player")
    parser.add_argument("--bsr", type=str, help="bsr ID")
    args = parser.parse_args()

    if args.bsr:
        bsr_music_play(bsr_id=args.bsr)
    else:
        print("Please provide a bsr ID")

if __name__ == "__main__":
    main()