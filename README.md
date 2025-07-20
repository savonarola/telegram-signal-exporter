## Signal sticker pack exporter

Import Telegram stickers into Signal.

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/)
- [`signal-cli`](https://github.com/AsamK/signal-cli)
- [`qrencode`](https://github.com/fukuchi/libqrencode)

## Usage

### Link `signal-cli` to your Signal account

Run
```bash
signal-cli link -n "MacBook Air"
```

It will print a `sgnl://...` link.

**Without** stoping the process, in a separate shell run

```bash
qrencode -t utf8 "sgnl://..."
```

with the link printed above.

Link the client with this QR using the phone's app.

After linking on the phone, the `signal-cli link` process will continue and link the client to the account.

To verify that the link was successful, run

```bash
signal-cli listAccounts
```

## Create a Telegram bot and get a token

* Launch the Telegram app on your device.

* Search for BotFather: In the search bar, type "BotFather" and select the verified account with a blue checkmark.

* Start a Chat: Tap on the "Start" button or send the `/start` command to initiate a conversation with BotFather.

* Create a New Bot: Send the `/newbot` command to BotFather to create a new bot.

* Choose a Name: BotFather will ask you to choose a name for your bot, this name does not matter.

* Choose a Username: Next, you’ll need to choose a unique username for your bot. It must end with "bot" (e.g., SampleBot). This name also does not matter for this script.

* Receive the Token: After you provide the username, BotFather will create your bot and send you a message with an HTTP API token. Export this token as `TG_BOT_TOKEN` environment variable.

## Export sticker pack from Telegram

Learn stickers pack's name. E.g., share it to yourself via Telegram and see the link. It should look like `https://t.me/addstickers/STICKER_PACK_NAME`.

Checkout this repo.

Run
```bash
uv sync
uv run main.py --output EXPORT.zip --sticker-set-name STICKER_PACK_NAME
```

## Import sticker pack into Signal

Run
```bash
signal-cli uploadStickerPack EXPORT.zip
```

## License

[MIT](LICENSE)
