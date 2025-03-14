from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, CallbackContext
import random
import json

# Set Bot Token (Replace this with a secure method for production)
BOT_TOKEN = "7233938223:AAHiAiLYLSmGSrelvYGNRG2V_RJY12YwB5o"

# Initialize the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Load user data from JSON
try:
    with open("user_data.json", "r") as f:
        user_data = json.load(f)
except FileNotFoundError:
    user_data = {}

# Save user data to JSON
def save_data():
    with open("user_data.json", "w") as f:
        json.dump(user_data, f, indent=4)

# Pokémon List
POKEMON_LIST = [
    {"name": "Bulbasaur", "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png", "type": "Grass", "level": 5, "hp": 20, "moves": ["Tackle", "Vine Whip"]},
    {"name": "Charmander", "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png", "type": "Fire", "level": 5, "hp": 20, "moves": ["Scratch", "Ember"]},
    {"name": "Squirtle", "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/7.png", "type": "Water", "level": 5, "hp": 20, "moves": ["Tackle", "Water Gun"]}
]

# Command to start the bot
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to the DexTro! Use /starter to choose your first Pokémon.")

# Command to choose a starter Pokémon
async def starter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id in user_data:
        await update.message.reply_text("You have already chosen a starter Pokémon!")
        return
    
    keyboard = [[InlineKeyboardButton(pokemon["name"], callback_data=f"starter_{pokemon['name']}")] for pokemon in POKEMON_LIST]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose your starter Pokémon!", reply_markup=reply_markup)

async def select_starter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    starter_name = query.data.replace("starter_", "")
    
    for pokemon in POKEMON_LIST:
        if pokemon["name"] == starter_name:
            user_data[user_id] = {"pokemon": pokemon.copy(), "currency": 100}
            save_data()
            await query.edit_message_text(f"You chose {starter_name}! Get ready for battles! Use /catch to hunt Pokémon.")
            return

# Command to check inventory
async def myinventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in user_data:
        await update.message.reply_text("You don't have any Pokémon! Use /starter to choose one.")
        return
    
    pokemon = user_data[user_id]["pokemon"]
    money = user_data[user_id]["currency"]
    await update.message.reply_photo(photo=pokemon['image'], caption=f"Your Pokémon: {pokemon['name']}\nType: {pokemon['type']}\nLevel: {pokemon['level']}\nHP: {pokemon['hp']}\nMoves: {', '.join(pokemon['moves'])}\nPokéDollars: {money}")

# Command to catch a wild Pokémon
async def catch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wild_pokemon = random.choice(POKEMON_LIST).copy()
    context.user_data["wild_pokemon"] = wild_pokemon
    await update.message.reply_photo(photo=wild_pokemon['image'], caption=f"A wild {wild_pokemon['name']} has been encountered! Use /battle to fight!")

# Command to battle a wild Pokémon
async def battle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if "wild_pokemon" not in context.user_data:
        await update.message.reply_text("No wild Pokémon to battle! Use /catch first.")
        return
    if user_id not in user_data:
        await update.message.reply_text("You don't have a Pokémon! Choose one using /starter.")
        return
    
    user_pokemon = user_data[user_id]["pokemon"]
    wild_pokemon = context.user_data["wild_pokemon"]
    
    keyboard = [[InlineKeyboardButton(move, callback_data=f"attack_{move}")] for move in user_pokemon["moves"]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Choose a move for {user_pokemon['name']}!", reply_markup=reply_markup)

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    move = query.data.replace("attack_", "")
    
    if "wild_pokemon" not in context.user_data:
        await query.edit_message_text("No wild Pokémon to battle! Use /catch first.")
        return
    
    user_pokemon = user_data[user_id]["pokemon"]
    wild_pokemon = context.user_data["wild_pokemon"]
    
    # Simulating attack
    wild_pokemon["hp"] -= random.randint(5, 10)
    if wild_pokemon["hp"] <= 0:
        await query.edit_message_text(f"{wild_pokemon['name']} fainted! You won the battle!")
        del context.user_data["wild_pokemon"]
        user_data[user_id]["currency"] += 50  # Reward for winning
        save_data()
    else:
        await query.edit_message_text(f"{user_pokemon['name']} used {move}! {wild_pokemon['name']} has {wild_pokemon['hp']} HP left.")

# Add handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("starter", starter))
app.add_handler(CallbackQueryHandler(select_starter, pattern="starter_.*"))
app.add_handler(CommandHandler("myinventory", myinventory))
app.add_handler(CommandHandler("catch", catch))
app.add_handler(CommandHandler("battle", battle))
app.add_handler(CallbackQueryHandler(attack, pattern="attack_.*"))

# Run the bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(app.run_polling())
