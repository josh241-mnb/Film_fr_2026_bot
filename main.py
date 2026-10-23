import requests, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TELEGRAM_TOKEN = "8827167789:AAHlk12_nVgpMjUjesbzVHtty-5M7keVEfM"
TMDB_API_KEY = "8d6d2e0b8c1a2b3c4d5e6f7a8b9c0d1e2"
BASE = "https://api.themoviedb.org/3"

def search_film(q):
    r = requests.get(f"{BASE}/search/movie", params={"api_key": TMDB_API_KEY, "query": q, "language": "fr-FR"}, timeout=15)
    return r.json().get("results", [])[:8]

def details_film(mid):
    r = requests.get(f"{BASE}/movie/{mid}", params={"api_key": TMDB_API_KEY, "language": "fr-FR", "append_to_response": "videos,credits"}, timeout=15)
    return r.json()

async def start(update, context):
    await update.message.reply_text("🎬 Salut! Bot Film FR\nEnvoie un film: Avatar, Dune, Inception")

async def handle(update, context):
    films = search_film(update.message.text)
    if not films:
        await update.message.reply_text("Pas trouvé 😕")
        return
    keys = [[InlineKeyboardButton(f"{f['title']} ({f.get('release_date','')[:4]})", callback_data=f"d_{f['id']}")] for f in films]
    await update.message.reply_text(f"Résultats:", reply_markup=InlineKeyboardMarkup(keys))

async def btn(update, context):
    q = update.callback_query
    await q.answer()
    m = details_film(q.data.split("_")[1])
    txt = f"🎬 *{m['title']}* ({m.get('release_date','')[:4]})\n⭐ {m.get('vote_average',0)}/10\n\n{m.get('overview','')[:700]}"
    vids = m.get('videos',{}).get('results',[])
    trail = next((v for v in vids if v['type']=='Trailer'), None)
    kb = [[InlineKeyboardButton("▶️ Bande-annonce", url=f"https://youtube.com/watch?v={trail['key']}")]] if trail else None
    await q.message.reply_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb) if kb else None)

app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.add_handler(CallbackQueryHandler(btn))
print("Bot lance")
app.run_polling()
