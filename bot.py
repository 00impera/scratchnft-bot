import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN    = os.environ["BOT_TOKEN"]
CONTRACT     = "0x71a8F50008b08cc736E739239faF549a34fD9C8f"
DAPP_URL     = "https://ancient-lab-377a.nelutz2you.workers.dev/"
RPC_URL      = "https://rpc.monad.xyz"
CHAIN_ID     = 143
EXPLORER     = "https://explorer.monad.xyz"

# GitHub raw images
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
        [InlineKeyboardButton("🎰 Open Game", url=DAPP_URL)],
        [InlineKeyboardButton("📊 Stats", callback_data="stats"), InlineKeyboardButton("💰 Price", callback_data="price")],
        [InlineKeyboardButton("🏆 How to Win", callback_data="howtowin"), InlineKeyboardButton("📜 Contract", callback_data="contract")],
        [InlineKeyboardButton("📱 How to Connect", callback_data="connect"), InlineKeyboardButton("🃏 Cards", callback_data="cards")],
        [InlineKeyboardButton("🔗 Explorer", url=f"{EXPLORER}/address/{CONTRACT}"), InlineKeyboardButton("❓ Help", callback_data="help")],
    ])

def back_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🎰 Open Game", url=DAPP_URL),
        InlineKeyboardButton("⬅️ Back", callback_data="back")
    ]])

WELCOME = """
✦ *SCRATCHCARD NFT* ✦
━━━━━━━━━━━━━━━━━━━━
🎰 First on-chain scratch card on *Monad*!

1️⃣ Mint a scratch card NFT
2️⃣ Scratch it on-chain
3️⃣ Win up to *20x your bet* in MON!

🏍️ USDC Rider · ⚔️ ETH Warrior · 🏎️ Monad Racer

🥉 Small Win → 2x
🥈 Big Win → 5x
🥇 Jackpot → 20x
━━━━━━━━━━━━━━━━━━━━
⚠️ Open in MetaMask or Trust Wallet browser!
Ready to scratch? 👇
"""

CONNECT_HELP = """
📱 *HOW TO CONNECT WALLET*
━━━━━━━━━━━━━━━━━━━━

Telegram browser blocks Web3!
You need to open in a wallet browser:

*Option 1 — MetaMask Mobile:*
1️⃣ Open MetaMask app
2️⃣ Tap the browser icon
3️⃣ Go to: ancient-lab-377a.nelutz2you.workers.dev
4️⃣ Connect wallet

*Option 2 — Trust Wallet:*
1️⃣ Open Trust Wallet
2️⃣ Tap DApps or Browser
3️⃣ Go to: ancient-lab-377a.nelutz2you.workers.dev
4️⃣ Connect wallet

*Option 3 — Desktop:*
1️⃣ Open Chrome with MetaMask extension
2️⃣ Go to: ancient-lab-377a.nelutz2you.workers.dev
3️⃣ Connect wallet

━━━━━━━━━━━━━━━━━━━━
"""

CARDS_TEXT = """
🃏 *SCRATCH CARD COLLECTION*
━━━━━━━━━━━━━━━━━━━━

🏍️ *USDC Rider* — RARE
Stablecoin street racer, blue-chip DeFi master.

⚔️ *ETH Warrior* — EPIC  
Battle-hardened gladiator, forged in gas wars.

🏎️ *Monad Racer* — LEGENDARY
Speed demon of parallel execution.

━━━━━━━━━━━━━━━━━━━━
Each card: Mint → Scratch → Win MON instantly!
"""

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # Send logo image + welcome text
    await update.message.reply_photo(
        photo=LOGO,
        caption=WELCOME,
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ *HELP*\n\n🌐 ancient-lab-377a.nelutz2you.workers.dev\n\nMonad Mainnet Chain ID: 143\n\n/start /stats /price /contract /help",
        parse_mode="Markdown", reply_markup=main_keyboard()
    )

async def button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "back":
        await q.edit_message_caption(caption=WELCOME, parse_mode="Markdown", reply_markup=main_keyboard())

    elif q.data == "connect":
        await q.edit_message_caption(caption=CONNECT_HELP, parse_mode="Markdown", reply_markup=back_keyboard())

    elif q.data == "cards":
        await q.edit_message_media(
            media=__import__('telegram').InputMediaPhoto(media=USDC_UNSRC, caption=CARDS_TEXT, parse_mode="Markdown"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏍️ USDC", callback_data="card_usdc"),
                 InlineKeyboardButton("⚔️ ETH", callback_data="card_eth"),
                 InlineKeyboardButton("🏎️ Monad", callback_data="card_monad")],
                [InlineKeyboardButton("🎰 Open Game", url=DAPP_URL),
                 InlineKeyboardButton("⬅️ Back", callback_data="back")]
            ])
        )

    elif q.data == "card_usdc":
        await q.edit_message_media(
            media=__import__('telegram').InputMediaPhoto(
                media=USDC_UNSRC,
                caption="🏍️ *USDC RIDER* — RARE\n━━━━━━━━━━━━━━━━━━━━\nElite crypto mercenary riding the stablecoin wave.\n\n🥉 Small Win: 2×\n🥈 Big Win: 5×\n🥇 Jackpot: 20×",
                parse_mode="Markdown"
            ),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎰 Mint USDC Rider", url=DAPP_URL),
                InlineKeyboardButton("⬅️ Back", callback_data="cards")
            ]])
        )

    elif q.data == "card_eth":
        await q.edit_message_media(
            media=__import__('telegram').InputMediaPhoto(
                media=ETH_UNSRC,
                caption="⚔️ *ETH WARRIOR* — EPIC\n━━━━━━━━━━━━━━━━━━━━\nBattle-hardened Ethereum gladiator, forged in gas wars.\n\n🥉 Small Win: 2×\n🥈 Big Win: 5×\n🥇 Jackpot: 20×",
                parse_mode="Markdown"
            ),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎰 Mint ETH Warrior", url=DAPP_URL),
                InlineKeyboardButton("⬅️ Back", callback_data="cards")
            ]])
        )

    elif q.data == "card_monad":
        await q.edit_message_media(
            media=__import__('telegram').InputMediaPhoto(
                media=MONAD_UNSRC,
                caption="🏎️ *MONAD RACER* — LEGENDARY\n━━━━━━━━━━━━━━━━━━━━\nLegendary speed demon of parallel execution.\n\n🥉 Small Win: 2×\n🥈 Big Win: 5×\n🥇 Jackpot: 20×",
                parse_mode="Markdown"
            ),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎰 Mint Monad Racer", url=DAPP_URL),
                InlineKeyboardButton("⬅️ Back", callback_data="cards")
            ]])
        )

    elif q.data == "stats":
        supply = get_total_supply()
        price  = get_card_price()
        pool   = get_prize_pool()
        await q.edit_message_caption(
            caption=f"📊 *LIVE STATS*\n━━━━━━━━━━━━━━━━━━━━\n🃏 Cards Minted: `{supply}`\n💎 Card Price: `{price:.4f} MON`\n🏦 Prize Pool: `{pool:.4f} MON`\n━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown", reply_markup=main_keyboard()
        )

    elif q.data == "price":
        price = get_card_price()
        pool  = get_prize_pool()
        await q.edit_message_caption(
            caption=f"💰 *CARD PRICE*\n━━━━━━━━━━━━━━━━━━━━\n🎟️ Mint: `{price:.4f} MON`\n🥇 Jackpot: `{pool*0.2:.4f} MON`\n🥈 Big Win: `{price*5:.4f} MON`\n🥉 Small: `{price*2:.4f} MON`\n━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown", reply_markup=main_keyboard()
        )

    elif q.data == "howtowin":
        await q.edit_message_caption(
            caption="🏆 *HOW TO WIN*\n━━━━━━━━━━━━━━━━━━━━\nStep 1 — Connect Wallet\nStep 2 — Mint a Card\nStep 3 — Scratch on-chain\nStep 4 — Claim prize instantly!\n━━━━━━━━━━━━━━━━━━━━\n100% on-chain and fair",
            parse_mode="Markdown", reply_markup=back_keyboard()
        )

    elif q.data == "contract":
        await q.edit_message_caption(
            caption=f"📜 *CONTRACT*\n━━━━━━━━━━━━━━━━━━━━\n`{CONTRACT}`\nMonad Chain ID: {CHAIN_ID}\n━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔗 Explorer", url=f"{EXPLORER}/address/{CONTRACT}"),
                InlineKeyboardButton("⬅️ Back", callback_data="back")
            ]])
        )

    elif q.data == "help":
        await q.edit_message_caption(
            caption="❓ *HELP*\n\n🌐 ancient-lab-377a.nelutz2you.workers.dev\nMonad Mainnet Chain ID: 143\n\n/start /stats /price /contract /help",
            parse_mode="Markdown", reply_markup=main_keyboard()
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help",  help_cmd))
    app.add_handler(CallbackQueryHandler(button))
    log.info("ScratchCard Bot started - ancient-lab-377a.nelutz2you.workers.dev")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
