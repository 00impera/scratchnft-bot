import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN    = os.environ["BOT_TOKEN"]
CONTRACT     = "0x71a8F50008b08cc736E739239faF549a34fD9C8f"
DAPP_URL     = "https://scratchnft.pages.dev/"
RPC_URL      = "https://rpc.monad.xyz"
CHAIN_ID     = 143
EXPLORER     = "https://monadscan.com"

RAW = "https://raw.githubusercontent.com/00impera/scratchnft/Telegram8/images"
LOGO        = f"{RAW}/logo1.png"
USDC_UNSRC  = f"{RAW}/usdc_unscratched.jpg"
USDC_SMALL  = f"{RAW}/usdc_small.jpg"
USDC_BIG    = f"{RAW}/usdc_big.jpg"
USDC_LOSE   = f"{RAW}/usdc_lose.jpg"
ETH_UNSRC   = f"{RAW}/eth_unscratched.jpg"
ETH_LOSE    = f"{RAW}/eth_lose.jpg"
MONAD_UNSRC = f"{RAW}/monad_unscratched.jpg"
MONAD_BIG   = f"{RAW}/monad_big.jpg"
MONAD_LOSE  = f"{RAW}/monad_lose.jpg"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def rpc_call(method, params):
    try:
        r = requests.post(RPC_URL, json={"jsonrpc":"2.0","id":1,"method":method,"params":params}, timeout=8)
        return r.json().get("result")
    except Exception:
        return None

def eth_call(data):
    return rpc_call("eth_call", [{"to": CONTRACT, "data": data}, "latest"])

def decode_uint(hex_str):
    if not hex_str or hex_str == "0x":
        return 0
    return int(hex_str, 16)

def get_total_supply():
    return decode_uint(eth_call("0x18160ddd"))

def get_card_price():
    return decode_uint(eth_call("0xa035b1fe")) / 1e18

def get_prize_pool():
    return decode_uint(rpc_call("eth_getBalance", [CONTRACT, "latest"])) / 1e18

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 SPIN & WIN = BIG!!!", url=DAPP_URL)],
        [InlineKeyboardButton("📊 Live Stats", callback_data="stats"),
         InlineKeyboardButton("💰 Prizes", callback_data="price")],
        [InlineKeyboardButton("🃏 NFT Cards", callback_data="cards"),
         InlineKeyboardButton("🏆 How to Win", callback_data="howtowin")],
        [InlineKeyboardButton("📱 Connect Wallet", callback_data="connect"),
         InlineKeyboardButton("📜 Contract", callback_data="contract")],
        [InlineKeyboardButton("🔗 MonadScan", url=f"{EXPLORER}/address/{CONTRACT}"),
         InlineKeyboardButton("❓ Help", callback_data="help")],
    ])

def back_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🎰 SPIN & WIN = BIG!!!", url=DAPP_URL),
        InlineKeyboardButton("⬅️ Back", callback_data="back")
    ]])

def cards_nav():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏍️ USDC Rider", callback_data="card_usdc"),
         InlineKeyboardButton("⚔️ ETH Warrior", callback_data="card_eth"),
         InlineKeyboardButton("🏎️ Monad Racer", callback_data="card_monad")],
        [InlineKeyboardButton("🎰 SPIN & WIN = BIG!!!", url=DAPP_URL),
         InlineKeyboardButton("⬅️ Back", callback_data="back")]
    ])

WELCOME = """
🎴 *SCRATCHCARD NFT* 🎴
━━━━━━━━━━━━━━━━━━━━
🔥 First on-chain scratch card on *Monad*!

🎡 *SPIN & WIN = BIG!!!*

1️⃣ Pick your NFT series
2️⃣ Spin the wheel for luck
3️⃣ Mint & scratch on-chain
4️⃣ Claim your MON prize instantly!

━━━━━━━━━━━━━━━━━━━━
🏎️ *Monad Racer* — LEGENDARY — 100 MON
⚔️ *ETH Warrior* — EPIC — 500 MON
🏍️ *USDC Rider* — RARE — 1000 MON
━━━━━━━━━━━━━━━━━━━━
🥉 Small Win → *2×*
🥈 Big Win → *10×*
🥇 Jackpot → *100×*
━━━━━━━━━━━━━━━━━━━━
⚡ 100% on-chain · Monad Mainnet
⚠️ Open in MetaMask or Trust Wallet browser!
"""

CONNECT_HELP = """
📱 *HOW TO CONNECT WALLET*
━━━━━━━━━━━━━━━━━━━━
Telegram browser blocks Web3!
Open in a wallet browser:

*🦊 MetaMask Mobile:*
1️⃣ Open MetaMask app
2️⃣ Tap the browser icon
3️⃣ Go to: scratchnft.pages.dev
4️⃣ Connect wallet ✅

*🛡️ Trust Wallet:*
1️⃣ Open Trust Wallet
2️⃣ Tap DApps or Browser
3️⃣ Go to: scratchnft.pages.dev
4️⃣ Connect wallet ✅

*🖥️ Desktop Chrome:*
1️⃣ Install MetaMask extension
2️⃣ Go to: scratchnft.pages.dev
3️⃣ Connect wallet ✅

━━━━━━━━━━━━━━━━━━━━
Network: *Monad Mainnet*
Chain ID: *143*
"""

CARDS_TEXT = """
🃏 *NFT SCRATCH CARD SERIES*
━━━━━━━━━━━━━━━━━━━━

🏎️ *Monad Racer* — LEGENDARY
💎 Price: 100 MON
Speed demon of parallel execution.

⚔️ *ETH Warrior* — EPIC
💎 Price: 500 MON
Battle-hardened gladiator, forged in gas wars.

🏍️ *USDC Rider* — RARE
💎 Price: 1000 MON
Stablecoin street racer, blue-chip DeFi master.

━━━━━━━━━━━━━━━━━━━━
🎡 Spin → Mint → Scratch → Win MON!
"""

HOW_TO_WIN = """
🏆 *HOW TO WIN*
━━━━━━━━━━━━━━━━━━━━

*Step 1* — Connect your wallet
*Step 2* — Choose your NFT series
*Step 3* — 🎡 Spin the wheel for luck
*Step 4* — Mint your scratch card
*Step 5* — Scratch on-chain to reveal
*Step 6* — Claim prize instantly!

━━━━━━━━━━━━━━━━━━━━
🥉 Small Win → *2×* your bet
🥈 Big Win → *10×* your bet
🥇 Jackpot → *100×* your bet
😶 No Prize → better luck next time

━━━━━━━━━━━━━━━━━━━━
🔐 100% on-chain · Provably fair
⚡ Instant payout in MON
"""

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=MONAD_UNSRC,
        caption=WELCOME,
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ *HELP*\n\n🌐 scratchnft.pages.dev\n\nMonad Mainnet Chain ID: 143\n\n/start /stats /price /contract /help",
        parse_mode="Markdown", reply_markup=main_keyboard()
    )

async def stats_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    supply = get_total_supply()
    price  = get_card_price()
    pool   = get_prize_pool()
    await update.message.reply_photo(
        photo=LOGO,
        caption=f"📊 *LIVE STATS*\n━━━━━━━━━━━━━━━━━━━━\n🃏 Cards Minted: `{supply}`\n💎 Card Price: `{price:.4f} MON`\n🏦 Prize Pool: `{pool:.4f} MON`\n━━━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown", reply_markup=main_keyboard()
    )

async def button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    TG = __import__('telegram')

    if q.data == "back":
        await q.edit_message_media(
            media=TG.InputMediaPhoto(media=MONAD_UNSRC, caption=WELCOME, parse_mode="Markdown"),
            reply_markup=main_keyboard()
        )

    elif q.data == "connect":
        await q.edit_message_caption(
            caption=CONNECT_HELP, parse_mode="Markdown", reply_markup=back_keyboard()
        )

    elif q.data == "howtowin":
        await q.edit_message_caption(
            caption=HOW_TO_WIN, parse_mode="Markdown", reply_markup=back_keyboard()
        )

    elif q.data == "cards":
        await q.edit_message_media(
            media=TG.InputMediaPhoto(media=USDC_UNSRC, caption=CARDS_TEXT, parse_mode="Markdown"),
            reply_markup=cards_nav()
        )

    elif q.data == "card_usdc":
        await q.edit_message_media(
            media=TG.InputMediaPhoto(
                media=USDC_UNSRC,
                caption="🏍️ *USDC RIDER* — RARE\n━━━━━━━━━━━━━━━━━━━━\n💎 Price: *1000 MON*\nStablecoin street racer, blue-chip DeFi master.\n\n🥉 Small Win: *2×* = 2000 MON\n🥈 Big Win: *10×* = 10,000 MON\n🥇 Jackpot: *100×* = 100,000 MON\n━━━━━━━━━━━━━━━━━━━━\n🎡 Spin the wheel & mint now!",
                parse_mode="Markdown"
            ),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎰 SPIN & WIN = BIG!!!", url=DAPP_URL),
                InlineKeyboardButton("⬅️ Back", callback_data="cards")
            ]])
        )

    elif q.data == "card_eth":
        await q.edit_message_media(
            media=TG.InputMediaPhoto(
                media=ETH_UNSRC,
                caption="⚔️ *ETH WARRIOR* — EPIC\n━━━━━━━━━━━━━━━━━━━━\n💎 Price: *500 MON*\nBattle-hardened Ethereum gladiator, forged in gas wars.\n\n🥉 Small Win: *2×* = 1000 MON\n🥈 Big Win: *10×* = 5,000 MON\n🥇 Jackpot: *100×* = 50,000 MON\n━━━━━━━━━━━━━━━━━━━━\n🎡 Spin the wheel & mint now!",
                parse_mode="Markdown"
            ),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎰 SPIN & WIN = BIG!!!", url=DAPP_URL),
                InlineKeyboardButton("⬅️ Back", callback_data="cards")
            ]])
        )

    elif q.data == "card_monad":
        await q.edit_message_media(
            media=TG.InputMediaPhoto(
                media=MONAD_UNSRC,
                caption="🏎️ *MONAD RACER* — LEGENDARY\n━━━━━━━━━━━━━━━━━━━━\n💎 Price: *100 MON*\nLegendary speed demon of parallel execution.\n\n🥉 Small Win: *2×* = 200 MON\n🥈 Big Win: *10×* = 1,000 MON\n🥇 Jackpot: *100×* = 10,000 MON\n━━━━━━━━━━━━━━━━━━━━\n🎡 Spin the wheel & mint now!",
                parse_mode="Markdown"
            ),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎰 SPIN & WIN = BIG!!!", url=DAPP_URL),
                InlineKeyboardButton("⬅️ Back", callback_data="cards")
            ]])
        )

    elif q.data == "stats":
        supply = get_total_supply()
        price  = get_card_price()
        pool   = get_prize_pool()
        await q.edit_message_caption(
            caption=f"📊 *LIVE STATS*\n━━━━━━━━━━━━━━━━━━━━\n🃏 Cards Minted: `{supply}`\n💎 Card Price: `{price:.4f} MON`\n🏦 Prize Pool: `{pool:.4f} MON`\n━━━━━━━━━━━━━━━━━━━━\n⚡ Live from Monad Mainnet",
            parse_mode="Markdown", reply_markup=main_keyboard()
        )

    elif q.data == "price":
        price = get_card_price()
        pool  = get_prize_pool()
        await q.edit_message_caption(
            caption=f"💰 *PRIZE TABLE*\n━━━━━━━━━━━━━━━━━━━━\n🏎️ Monad Racer: `100 MON`\n⚔️ ETH Warrior: `500 MON`\n🏍️ USDC Rider: `1000 MON`\n━━━━━━━━━━━━━━━━━━━━\n🥉 Small Win: *2×*\n🥈 Big Win: *10×*\n🥇 Jackpot: *100×*\n━━━━━━━━━━━━━━━━━━━━\n🏦 Prize Pool: `{pool:.4f} MON`",
            parse_mode="Markdown", reply_markup=main_keyboard()
        )

    elif q.data == "contract":
        await q.edit_message_caption(
            caption=f"📜 *CONTRACT*\n━━━━━━━━━━━━━━━━━━━━\n`{CONTRACT}`\n\nMonad Chain ID: `{CHAIN_ID}`\nNetwork: Monad Mainnet\nRPC: rpc.monad.xyz\n━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔗 MonadScan", url=f"{EXPLORER}/address/{CONTRACT}"),
                InlineKeyboardButton("⬅️ Back", callback_data="back")
            ]])
        )

    elif q.data == "help":
        await q.edit_message_caption(
            caption="❓ *HELP*\n\n🌐 scratchnft.pages.dev\nMonad Mainnet Chain ID: 143\n\n/start — Main menu\n/stats — Live stats\n/help — This menu",
            parse_mode="Markdown", reply_markup=main_keyboard()
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("help",   help_cmd))
    app.add_handler(CommandHandler("stats",  stats_cmd))
    app.add_handler(CallbackQueryHandler(button))
    log.info("ScratchNFT Bot started — scratchnft.pages.dev")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
