import argparse
import asyncio
import json
import os
import shutil
import tempfile
from zipfile import ZipFile

import httpx
import telegram.request
import tqdm
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
MAX_TG_DOWNLOAD_TASKS = 10

async def download_sticker(semaphore, bot, sticker, output_dir, n):
    async with semaphore:
        emoji = sticker.emoji
        file = await bot.get_file(sticker.file_id)
        file_name = get_file_name(file)
        save_file_path = os.path.join(output_dir, file_name)
        await file.download_to_drive(save_file_path)
        return (emoji, file_name)

def get_file_name(file):
    file_url = file.file_path
    file_ext = file_url.split(".")[-1]
    file_name = str2hex(file.file_unique_id)[2:]
    return f"{file_name}.{file_ext}"

def str2hex(s):
    return "".join(f"{ord(c):02x}" for c in s)

async def main():

    if not TG_BOT_TOKEN:
        raise ValueError("TG_BOT_TOKEN is not set")

    parser = argparse.ArgumentParser(
        description="Get stickers from a Telegram sticker set"
    )
    parser.add_argument(
        "--sticker-set-name",
        type=str,
        required=True,
        help="The name of the sticker set to get stickers from",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Zip file to save the sticker package to",
    )
    args = parser.parse_args()

    output_dir = os.path.dirname(args.output)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    download_dir = tempfile.mkdtemp()

    try:
        await run(args, download_dir)
    finally:
        shutil.rmtree(download_dir)

async def run(args, download_dir):
    base_request = telegram.request.HTTPXRequest(
        connection_pool_size=MAX_TG_DOWNLOAD_TASKS * 3,
    )

    bot = Bot(token=TG_BOT_TOKEN, request=base_request)
    sticker_set = await bot.get_sticker_set(name=args.sticker_set_name)

    ## Download stickers
    stickers = sticker_set.stickers

    semaphore = asyncio.Semaphore(MAX_TG_DOWNLOAD_TASKS)

    tasks = [
        asyncio.create_task(download_sticker(semaphore, bot, sticker, download_dir, n))
        for n, sticker in enumerate(stickers)
    ]
    print(f"Downloading stickers...")

    downloaded_stickers = []
    for task in tqdm.tqdm(tasks):
        emoji, file_name = await task
        downloaded_stickers.append((emoji, file_name))

    ## Download cover
    if sticker_set.thumbnail:
        cover_file = await bot.get_file(sticker_set.thumbnail.file_id)
        cover_file_url = cover_file.file_path
        cover_file_ext = cover_file_url.split(".")[-1]
        cover_file_name = f"cover.{cover_file_ext}"
        cover_save_file_path = os.path.join(download_dir, cover_file_name)
        await cover_file.download_to_drive(cover_save_file_path)
    else:
        _, first_file_name = downloaded_stickers[0]
        cover_file_name = first_file_name

    ## Create manifest.json
    manifest = {
        "title": sticker_set.title,
        "author": sticker_set.title,
        "cover": {
            "file": cover_file_name,
        },
        "stickers": [
            {
                "emoji": emoji,
                "file": file_name,
            }
            for emoji, file_name in downloaded_stickers
        ],
    }

    print(f"Creating zip file {args.output}...")

    with ZipFile(args.output, "w") as zip_file:
        for _, file_name in tqdm.tqdm(downloaded_stickers):
            zip_file.write(os.path.join(download_dir, file_name), file_name)
        zip_file.write(os.path.join(download_dir, cover_file_name), cover_file_name)
        zip_file.writestr("manifest.json", json.dumps(manifest))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Terminating...")
