from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import sqlite3

# Connessione al database (crea il file se non esiste)
conn = sqlite3.connect("shop.db", check_same_thread=False)
cursor = conn.cursor()

# Creazione delle tabelle se non esistono
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    points INTEGER
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    price INTEGER
)
""")
conn.commit()

# Inserimento prodotti nel database (se non esistono già)
cursor.execute("SELECT COUNT(*) FROM products")
product_count = cursor.fetchone()[0]
if product_count == 0:  # Controlla se i prodotti sono già presenti
    cursor.execute("INSERT INTO products (name, description, price) VALUES ('Quadrifoglio', 'Aumenta il tuo guadagno', 50)")
    cursor.execute("INSERT INTO products (name, description, price) VALUES ('Acqua x64', 'Acqua che ti disseta', 20)")
    conn.commit()

# Funzione /start per registrare gli utenti
def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    cursor.execute("SELECT * FROM users WHERE id = ?", (user.id,))
    result = cursor.fetchone()
    if result:
        update.message.reply_text(f"Benvenuto di nuovo, {user.username}! Hai {result[2]} punti.")
    else:
        cursor.execute("INSERT INTO users (id, username, points) VALUES (?, ?, ?)", (user.id, user.username, 100))
        conn.commit()
        update.message.reply_text(f"Registrazione completata! Hai 100 punti iniziali, {user.username}!")

# Funzione per mostrare il negozio
def shop(update: Update, context: CallbackContext):
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    buttons = [
        [InlineKeyboardButton(f"{p[1]} - {p[3]} punti", callback_data=f"buy_{p[0]}")]
        for p in products
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text("Ecco il negozio:", reply_markup=reply_markup)

# Funzione per acquistare un prodotto
def buy(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    product_id = int(query.data.split("_")[1])

    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if user[2] >= product[3]:  # Controlla punti
        cursor.execute("UPDATE users SET points = points - ? WHERE id = ?", (product[3], user_id))
        conn.commit()
        query.answer()
        query.edit_message_text(f"Hai comprato {product[1]} per {product[3]} punti! Ti restano {user[2] - product[3]} punti.")
    else:
        query.answer()
        query.edit_message_text("Non hai abbastanza punti per comprare questo prodotto.")

# Funzione principale per avviare il bot
def main():
    # Inserisci il token del tuo bot qui
    updater = Updater("7761794013:AAF4_85KwJl4Bl8gcPNuKkRqhUjtXGljeig")
    dispatcher = updater.dispatcher

    # Aggiungi i comandi
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("shop", shop))
    dispatcher.add_handler(CallbackQueryHandler(buy, pattern="^buy_"))

    # Avvia il bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
