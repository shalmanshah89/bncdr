import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import json
import os
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_FILE = "providers.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

providers = load_db()
DEFAULT_PROVIDERS = [
    "DataImpulse", "ABCProxy", "ProxySeller", "NodeMaven", "9Proxy", "Bright Data", "Smartproxy", "Oxylabs",
    "Soax", "IPRoyal", "NetNut", "ProxyEmpire", "GeoSurf", "Webshare", "RSocks", "HydraProxy", "Storm Proxies",
    "FineProxy", "ProxyRack", "MyPrivateProxy", "SSLPrivateProxy", "Froxy", "Proxy-Seller", "PacketStream",
    "LimeProxies", "Proxy6", "BuyProxies", "SquidProxies", "ProxyCheap", "HighProxies"
]

for p in DEFAULT_PROVIDERS:
    if p not in providers:
        providers[p] = {"proxies": [], "packages": {}, "formats": []}

save_db(providers)

API_TOKEN = "8679520507:AAGopkKUG1wN0GlxD8OYC4VqQ7wdmJlQkck"
CHANNEL_USERNAME = "@TR_TECH_ZONE"
ADMIN_IDS = [8589946469, 8679520507]

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

banned_users = set()
processed_requests = {}

class AdminState(StatesGroup):
    waiting_user_id = State()

class ProviderState(StatesGroup):
    waiting_provider_name = State()
    waiting_upload_method = State()
    waiting_proxy_text = State()
    waiting_proxy_file = State()
    waiting_gb_amount = State()
    waiting_package_price = State()

class DepositState(StatesGroup):
    waiting_amount = State()
    waiting_confirmation = State()
    waiting_transaction_id = State()
    waiting_screenshot = State()

def main_menu(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🛒 Buy Proxy", "🔑 Buy CD Key")
    kb.add("💰 Deposit", "👛 Balance")
    kb.add("📦 Status", "📞 Support")
    kb.add("📡 Proxy MB Check Bot")
    kb.add("👨‍💻 Developer")
    if user_id in ADMIN_IDS:
        kb.add("⚙️ Admin Panel")
    return kb

def admin_inline_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("➕ Add Balance", callback_data="add_balance"),
        InlineKeyboardButton("➖ Deduct Balance", callback_data="deduct_balance"),
        InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"),
        InlineKeyboardButton("👥 Total Users", callback_data="total_users"),
        InlineKeyboardButton("📊 Bot Status", callback_data="bot_status"),
        InlineKeyboardButton("➕ Add Proxy", callback_data="add_proxy"),
        InlineKeyboardButton("📦 Available Proxy", callback_data="available_proxy"),
        InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
        InlineKeyboardButton("✅ Unban User", callback_data="unban_user"),
    )
    kb.add(InlineKeyboardButton("🔙 Back", callback_data="back_main"))
    return kb

def add_proxy_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("➕ Add Provider", callback_data="ap_add_provider"),
        InlineKeyboardButton("💰 Set Price", callback_data="ap_set_price"),
        InlineKeyboardButton("✏️ Edit Price", callback_data="ap_edit_price"),
        InlineKeyboardButton("⚙️ Set Format", callback_data="ap_set_format"),
        InlineKeyboardButton("📤 Upload Proxy", callback_data="ap_upload_proxy"),
        InlineKeyboardButton("🗑 Delete Provider", callback_data="ap_delete_provider"),
    )
    kb.add(InlineKeyboardButton("🔙 Back", callback_data="ap_back"))
    return kb

def deposit_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Bkash", callback_data="dep_bkash"),
        InlineKeyboardButton("Nagad", callback_data="dep_nagad"),
        InlineKeyboardButton("Rocket", callback_data="dep_rocket"),
        InlineKeyboardButton("Binance", callback_data="dep_binance")
    )
    kb.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel_process"))
    return kb

def cancel_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel_process"))
    return kb

def provider_list_keyboard(action_prefix):
    kb = InlineKeyboardMarkup(row_width=2)
    for name in providers.keys():
        kb.add(InlineKeyboardButton(name, callback_data=f"{action_prefix}_{name}"))
    kb.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel_process"))
    return kb

async def check_join(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message, state: FSMContext):
    await state.finish()
    if message.from_user.id in banned_users:
        return
    joined = await check_join(message.from_user.id)
    if not joined:
        await message.answer("Please join the channel to proceed: https://t.me/TR_TECH_ZONE")
    else:
        await message.answer("Main Menu", reply_markup=main_menu(message.from_user.id))

@dp.message_handler(lambda m: m.text == "⚙️ Admin Panel")
async def admin_panel(message: types.Message, state: FSMContext):
    await state.finish()
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Admin Panel", reply_markup=admin_inline_menu())
    else:
        await message.answer("Main Menu", reply_markup=main_menu(message.from_user.id))

@dp.callback_query_handler(state="*")
async def admin_callbacks(callback: types.CallbackQuery, state: FSMContext):
    logger.info(f"Callback data: {callback.data}")
    user_id = callback.from_user.id

    if not (user_id in ADMIN_IDS or callback.data in ["cancel_process", "back_main", "buy_deposit_now", "confirm_deposit"] or callback.data.startswith(("dep_", "appr_", "reje_", "buy_"))):
        if callback.data.startswith(("ap_", "setprice_", "editprice_", "setformat_", "uploadproxy_", "deleteprovider_", "view_", "upload_method_")):
            await callback.answer("Access Denied!")
            return

    if callback.data == "cancel_process":
        await state.finish()
        if user_id in ADMIN_IDS:
            await callback.message.edit_text("❌ Process Canceled.", reply_markup=admin_inline_menu())
        else:
            try:
                await callback.message.delete()
            except:
                pass
            await callback.message.answer("❌ Process Canceled.", reply_markup=main_menu(user_id))
        return

    if callback.data == "back_main":
        await state.finish()
        try:
            await callback.message.delete()
        except:
            pass
        if user_id in ADMIN_IDS:
            await callback.message.answer("🏠 Main Menu", reply_markup=admin_inline_menu())
        else:
            await callback.message.answer("🏠 Main Menu", reply_markup=main_menu(user_id))
        return

    if callback.data == "buy_deposit_now":
        await callback.message.edit_text("🏦 Select your deposit method:", reply_markup=deposit_menu())
        await callback.answer()
        return

    if callback.data.startswith("dep_"):
        method = callback.data.split("_")[1].upper()
        await state.update_data(deposit_method=method)
        rate = 127.0
        text = (
            f"✨ Deposit via {method}\n\n"
            f"💹 Exchange Rate: 1$ = {rate} BDT\n"
            f"⚠️ Min Deposit: 1.0 BDT\n\n"
            f"✍️ Enter Amount you want to add (BDT):"
        )
        await callback.message.edit_text(text, reply_markup=cancel_keyboard())
        await DepositState.waiting_amount.set()
        return

    if callback.data == "confirm_deposit":
        data = await state.get_data()
        method = data.get("deposit_method")
        amount_bdt = data.get("amount_bdt")
        wallet_number = "017XXXXXXXX"
        final_text = (
            f"🚀 Action Required\n\n"
            f"Please send {amount_bdt} BDT to our {method} number: {wallet_number}\n"
            f"📌 Type: Send Money\n\n"
            f"After successful payment, please send your Transaction ID below for verification."
        )
        await callback.message.edit_text(final_text, reply_markup=cancel_keyboard())
        await DepositState.waiting_transaction_id.set()
        return

    if callback.data.startswith(("appr_", "reje_")):
        parts = callback.data.split("_")
        action = parts[0]
        dep_id = parts[1]
        target_user_id = int(parts[2])

        if dep_id in processed_requests:
            await callback.answer(f"⚠️ This request is already {processed_requests[dep_id]}!", show_alert=True)
            return

        user_db = load_db()
        try:
            usd_amount = float(callback.message.caption.split("($")[1].split(")")[0])
        except:
            usd_amount = 0.0

        if action == "appr":
            user_data = user_db.get(str(target_user_id), {"balance": "0.0000"})
            current_bal = float(user_data.get("balance", 0))
            new_bal = current_bal + usd_amount
            user_db[str(target_user_id)] = {"balance": f"{new_bal:.4f}"}
            save_db(user_db)
            processed_requests[dep_id] = "APPROVED"
            try:
                await bot.send_message(target_user_id, f"✅ Deposit Approved!\n\nAmount: ${usd_amount:.4f} added to your account.\nTotal Balance: ${new_bal:.4f}")
            except:
                pass
            status_text = f"✅ Status: APPROVED\n👤 By: @{callback.from_user.username}\n💰 Full Balance: ${new_bal:.4f}"
        else:
            processed_requests[dep_id] = "REJECTED"
            try:
                await bot.send_message(target_user_id, "❌ Deposit Rejected!\nInvalid details. Please contact support.")
            except:
                pass
            status_text = f"❌ Status: REJECTED\n👤 By: @{callback.from_user.username}"

        await callback.message.edit_caption(callback.message.caption + f"\n\n{status_text}", reply_markup=None)
        await callback.answer("✅ Action Completed!")
        return

    if user_id not in ADMIN_IDS:
        return

    if callback.data == "ban_user":
        await AdminState.waiting_user_id.set()
        await callback.message.answer("Send User ID:", reply_markup=cancel_keyboard())
        return

    if callback.data == "add_proxy":
        await callback.message.edit_text("Add Proxy Panel", reply_markup=add_proxy_menu())
        return

    if callback.data == "available_proxy":
        if not providers:
            await callback.message.answer("No Providers Available.")
        else:
            kb = InlineKeyboardMarkup(row_width=1)
            for name in providers.keys():
                kb.add(InlineKeyboardButton(name, callback_data=f"view_{name}"))
            kb.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel_process"))
            await callback.message.answer("Available Providers:", reply_markup=kb)
        return

    if callback.data.startswith("view_"):
        provider_name = callback.data.replace("view_", "")
        await callback.answer(f"Selected: {provider_name}")
        return

    if callback.data == "ap_back":
        await callback.message.edit_text("Admin Panel", reply_markup=admin_inline_menu())
        return

    if callback.data == "ap_add_provider":
        await ProviderState.waiting_provider_name.set()
        await callback.message.answer("Send Provider Name (e.g., Abc Proxy):", reply_markup=cancel_keyboard())
        return

    if callback.data.startswith(("ap_set_price", "ap_edit_price", "ap_set_format", "ap_upload_proxy", "ap_delete_provider")):
        action_map = {
            "ap_set_price": "setprice",
            "ap_edit_price": "editprice",
            "ap_set_format": "setformat",
            "ap_upload_proxy": "uploadproxy",
            "ap_delete_provider": "deleteprovider"
        }
        action_prefix = action_map.get(callback.data)
        title_map = {
            "setprice": "Set Price",
            "editprice": "Edit Price",
            "setformat": "Set Format",
            "uploadproxy": "Upload Proxy",
            "deleteprovider": "Delete Provider"
        }
        title = title_map.get(action_prefix, "")
        await callback.message.edit_text(f"Select Provider to {title}:", reply_markup=provider_list_keyboard(action_prefix))
        return

    if callback.data.startswith(("setprice_", "editprice_", "setformat_", "uploadproxy_", "deleteprovider_")):
        parts = callback.data.split("_", 1)
        action, provider_name = parts[0], parts[1]
        await state.update_data(selected_provider=provider_name)

        if action == "deleteprovider":
            current_db = load_db()
            if provider_name in current_db:
                del current_db[provider_name]
                save_db(current_db)
                await callback.message.edit_text(f"✅ {provider_name} deleted.", reply_markup=admin_inline_menu())
                await state.finish()
        elif action == "editprice":
            await callback.message.edit_text(f"Selected: {provider_name}\nSend new price:", reply_markup=cancel_keyboard())
        elif action == "setprice":
            await callback.message.edit_text(f"Selected: {provider_name}\nHow many GB? (e.g. 1GB):", reply_markup=cancel_keyboard())
            await ProviderState.waiting_gb_amount.set()
        elif action == "uploadproxy":
            kb = InlineKeyboardMarkup(row_width=2)
            kb.add(
                InlineKeyboardButton("📝 Text", callback_data="upload_method_text"),
                InlineKeyboardButton("📁 File", callback_data="upload_method_file"),
                InlineKeyboardButton("✏️ Edit", callback_data="upload_method_edit"),
                InlineKeyboardButton("🗑️ Delete", callback_data="upload_method_delete")
            )
            kb.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel_process"))
            await callback.message.edit_text(f"Upload method for {provider_name}:", reply_markup=kb)
            await ProviderState.waiting_upload_method.set()
        return

    current_state = await state.get_state()
    if current_state == ProviderState.waiting_upload_method.state:
        data = await state.get_data()
        provider = data.get("selected_provider")
        if callback.data == "upload_method_text":
            await ProviderState.waiting_proxy_text.set()
            await callback.message.edit_text(f"Send Proxy Text for {provider}:", reply_markup=cancel_keyboard())
        elif callback.data == "upload_method_file":
            await ProviderState.waiting_proxy_file.set()
            await callback.message.edit_text(f"Upload Proxy File for {provider}:", reply_markup=cancel_keyboard())
        elif callback.data == "upload_method_edit":
            await callback.message.edit_text(f"Editing {provider}...", reply_markup=cancel_keyboard())
        elif callback.data == "upload_method_delete":
            current_db = load_db()
            if provider in current_db:
                del current_db[provider]
                save_db(current_db)
                await callback.message.edit_text(f"✅ {provider} deleted!", reply_markup=admin_inline_menu())
                await state.finish()
        return

@dp.message_handler(lambda m: m.text == "👛 Balance")
async def balance_handler(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = load_db()
    balance = user_data.get(user_id, {}).get("balance", "0.0000")
    balance_text = (
        "💳 Your Wallet\n"
        "━━━━━━━━━━━━━━\n"
        f"💰 Balance: ${balance}\n"
        "━━━━━━━━━━━━━━\n"
        "To add funds, press Deposit below."
    )
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("💰 Deposit", callback_data="buy_deposit_now"))
    await message.answer(balance_text, reply_markup=kb)

@dp.message_handler(lambda m: m.text == "💰 Deposit")
async def deposit_handler(message: types.Message):
    if message.from_user.id in banned_users:
        return
    await message.answer("🏦 Select your deposit method:", reply_markup=deposit_menu())

@dp.message_handler(state=DepositState.waiting_amount)
async def deposit_amount_received(message: types.Message, state: FSMContext):
    if not message.text.replace('.', '', 1).isdigit():
        await message.answer("❌ Invalid input! Please send numbers only.")
        return

    amount_bdt = float(message.text)
    rate = 127.0
    amount_usd = amount_bdt / rate

    data = await state.get_data()
    method = data.get("deposit_method")
    wallet_number = "017XXXXXXXX"

    await state.update_data(amount_bdt=amount_bdt, amount_usd=amount_usd)

    preview_text = (
        f"📝 Deposit Summary\n"
        f"━━━━━━━━━━━━━━\n"
        f"🏦 Method: {method}\n"
        f"📞 Wallet: {wallet_number}\n"
        f"💵 Payable: {amount_bdt} BDT\n"
        f"💎 Credits: ${amount_usd:.4f}\n"
        f"━━━━━━━━━━━━━━\n"
        f"📢 Note: Send Money to the number above and click confirm."
    )

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("✅ Confirm & Pay", callback_data="confirm_deposit"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_process")
    )

    await message.answer(preview_text, reply_markup=kb)
    await DepositState.waiting_confirmation.set()

@dp.message_handler(state=DepositState.waiting_transaction_id)
async def process_txid_step(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount_bdt = data.get("amount_bdt")
    amount_usd = data.get("amount_usd")
    method = data.get("deposit_method")
    txid = message.text.strip()

    await state.update_data(txid=txid)
    await DepositState.waiting_screenshot.set()

    await message.answer("📸 Now please send a Screenshot of your payment.", reply_markup=cancel_keyboard())

    for admin_id in ADMIN_IDS:
        try:
            admin_msg = (
                f"🔔 New Deposit Request!\n\n"
                f"👤 User: {message.from_user.full_name}\n"
                f"🆔 User ID: {message.from_user.id}\n"
                f"💰 Amount: {amount_bdt} BDT (${amount_usd:.4f})\n"
                f"🏦 Method: {method}\n"
                f"🔢 TXID: {txid}"
            )
            await bot.send_message(admin_id, admin_msg)
        except:
            pass

@dp.message_handler(content_types=['photo'], state=DepositState.waiting_screenshot)
async def process_screenshot(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount_bdt = data.get("amount_bdt")
    amount_usd = data.get("amount_usd")
    method = data.get("deposit_method")
    txid = data.get("txid")

    dep_id = str(uuid.uuid4())[:8]

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Approve", callback_data=f"appr_{dep_id}_{message.from_user.id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reje_{dep_id}_{message.from_user.id}")
    )

    admin_msg = (
        f"🔔 New Deposit Request!\n\n"
        f"👤 User: {message.from_user.full_name}\n"
        f"🆔 User ID: {message.from_user.id}\n"
        f"💰 Amount: {amount_bdt} BDT (${amount_usd:.4f})\n"
        f"🏦 Method: {method}\n"
        f"🔢 TXID: {txid}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_photo(admin_id, message.photo[-1].file_id, caption=admin_msg, reply_markup=kb)
        except:
            pass

    await state.finish()
    await message.answer("✅ Submission Complete!\nAdmin will review your payment soon.", reply_markup=main_menu(message.from_user.id))

@dp.message_handler(state=ProviderState.waiting_provider_name)
async def process_add_provider(message: types.Message, state: FSMContext):
    provider_name = message.text.strip()
    current_db = load_db()

    if provider_name not in current_db:
        current_db[provider_name] = {"proxies": [], "packages": {}, "formats": []}
        save_db(current_db)
        await state.finish()
        await message.answer(f"✅ Provider '{provider_name}' added successfully!", reply_markup=admin_inline_menu())
    else:
        await message.answer("❌ This provider already exists.", reply_markup=cancel_keyboard())

@dp.message_handler(state=ProviderState.waiting_gb_amount)
async def process_gb_amount(message: types.Message, state: FSMContext):
    gb_text = message.text.strip()
    await state.update_data(current_gb=gb_text)
    data = await state.get_data()
    provider = data.get("selected_provider")

    await ProviderState.waiting_package_price.set()
    await message.answer(
        f"For {provider} {gb_text} proxy, how much price do you want to set?\nExample: $1, $5",
        reply_markup=cancel_keyboard()
    )

@dp.message_handler(state=ProviderState.waiting_package_price)
async def process_package_price(message: types.Message, state: FSMContext):
    price_text = message.text.strip()
    data = await state.get_data()
    provider = data.get("selected_provider")
    gb = data.get("current_gb")

    current_db = load_db()
    if provider not in current_db:
        current_db[provider] = {"proxies": [], "packages": {}, "formats": []}

    current_db[provider]["packages"][gb] = price_text
    save_db(current_db)

    await state.finish()
    await message.answer(
        f"✅ Package Saved!\nProvider: {provider}\nSize: {gb}\nPrice: {price_text}",
        reply_markup=admin_inline_menu()
    )

def is_valid_format(proxy_line):
    parts = proxy_line.split(':')
    return len(parts) == 4

@dp.message_handler(state=ProviderState.waiting_proxy_text)
async def process_proxy_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    provider = data.get("selected_provider")
    proxy_list = message.text.splitlines()

    current_db = load_db()
    if provider not in current_db:
        current_db[provider] = {"proxies": [], "packages": {}, "formats": []}
    if "proxies" not in current_db[provider]:
        current_db[provider]["proxies"] = []

    valid_count = 0
    for line in proxy_list:
        line = line.strip()
        if is_valid_format(line):
            p = line.split(':')
            proxy_data = {"ip": p[0], "port": p[1], "user": p[2], "pass": p[3]}
            current_db[provider]["proxies"].append(proxy_data)
            valid_count += 1

    if valid_count > 0:
        save_db(current_db)
        await state.finish()
        await message.answer(f"✅ {valid_count} Proxies added to {provider}!", reply_markup=admin_inline_menu())
    else:
        await message.answer("❌ Invalid Format! Please use IP:PORT:USER:PASS")

@dp.message_handler(content_types=['document'], state=ProviderState.waiting_proxy_file)
async def process_proxy_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    provider = data.get("selected_provider")

    file_info = await bot.get_file(message.document.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    content = downloaded_file.read().decode('utf-8')

    proxy_list = content.splitlines()
    valid_proxies = []

    for line in proxy_list:
        line = line.strip()
        if is_valid_format(line):
            p = line.split(':')
            proxy_data = {"ip": p[0], "port": p[1], "user": p[2], "pass": p[3]}
            valid_proxies.append(proxy_data)

    if not valid_proxies:
        await message.answer("❌ File contains no valid format proxies!", reply_markup=cancel_keyboard())
        return

    current_db = load_db()
    if provider not in current_db:
        current_db[provider] = {"proxies": [], "packages": {}, "formats": []}
    if "proxies" not in current_db[provider]:
        current_db[provider]["proxies"] = []

    current_db[provider]["proxies"].extend(valid_proxies)
    save_db(current_db)

    await state.finish()
    await message.answer(f"✅ {len(valid_proxies)} Proxies added from file to {provider}!", reply_markup=admin_inline_menu())

@dp.message_handler(lambda m: m.text == "🛒 Buy Proxy")
async def buy_proxy_handler(message: types.Message):
    current_db = load_db()
    kb = InlineKeyboardMarkup(row_width=1)
    
    # We look for providers inside the "providers" key or the root
    data_source = current_db.get("providers", current_db)
    
    found = False
    for name, data in data_source.items():
        if name == "users": continue # Skip the user balance section
        
        packages = data.get("packages", {})
        proxies = data.get("proxies", [])
        
        if proxies and packages:
            for gb, price in packages.items():
                # Clean the price string (e.g., "$1" -> "1")
                btn_text = f"{name} {gb} ({price})"
                kb.add(InlineKeyboardButton(btn_text, callback_data=f"askbuy_{name}_{gb}"))
                found = True
    
    if not found:
        await message.answer("❌ No proxies available in stock.")
    else:
        await message.answer("📡 **Available Proxies:**", reply_markup=kb, parse_mode="Markdown")

# Step 1: Show Confirmation
@dp.callback_query_handler(lambda c: c.data.startswith("askbuy_"), state="*")
async def confirm_purchase_prompt(callback: types.CallbackQuery):
    _, provider, gb = callback.data.split("_")
    
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Confirm Buy", callback_data=f"procbuy_{provider}_{gb}"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_purchase")
    )
    
    await callback.message.edit_text(
        f"⚠️ **Confirm Purchase**\n\nPackage: {provider} {gb}\n\nDo you want to proceed?",
        reply_markup=kb, parse_mode="Markdown"
    )
    await callback.answer()

# Step 2: Deduct Balance and Send Proxy
@dp.callback_query_handler(lambda c: c.data.startswith("procbuy_"), state="*")
async def process_proxy_purchase(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    _, provider, gb = callback.data.split("_")
    
    db = load_db()
    
    # Locate user and provider safely
    users_section = db.get("users", db)
    providers_section = db.get("providers", db)
    
    user_data = users_section.get(user_id, {"balance": "0.0000"})
    provider_data = providers_section.get(provider, {})
    
    # Get Price
    price_str = provider_data.get("packages", {}).get(gb, "0").replace("$", "")
    price = float(price_str)
    balance = float(user_data.get("balance", 0))

    if balance < price:
        await callback.message.edit_text(f"❌ **Insufficient Balance!**\nPrice: ${price}\nYour Balance: ${balance}")
        return

    # Get Proxy
    proxies = provider_data.get("proxies", [])
    if not proxies:
        await callback.message.edit_text("❌ **Out of Stock!**")
        return

    # Take first proxy and update DB
    selected_proxy = proxies.pop(0) 
    new_balance = balance - price

    # Save back to database
    if "users" in db:
        db["users"][user_id]["balance"] = f"{new_balance:.4f}"
    else:
        db[user_id]["balance"] = f"{new_balance:.4f}"
        
    if "providers" in db:
        db["providers"][provider]["proxies"] = proxies
    else:
        db[provider]["proxies"] = proxies
        
    save_db(db)

    # Output Format: IP:PORT:USER:PASS
    if isinstance(selected_proxy, dict):
        p_out = f"{selected_proxy['ip']}:{selected_proxy['port']}:{selected_proxy['user']}:{selected_proxy['pass']}"
    else:
        p_out = str(selected_proxy)

    await callback.message.edit_text(
        f"✅ **Purchase Successful!**\n\n"
        f"🚀 **Your Proxy:**\n`{p_out}`\n\n"
        f"💰 Remaining Balance: ${new_balance:.4f}",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "cancel_purchase", state="*")
async def cancel_purchase_logic(callback: types.CallbackQuery):
    await callback.message.edit_text("❌ Purchase cancelled.")
    await callback.answer()

@dp.message_handler(lambda m: m.text == "📦 Status")
async def status_handler(message: types.Message):
    status_text = "📦 Bot Status: Online\nAll services running smoothly."
    await message.answer(status_text)

@dp.message_handler(lambda m: m.text == "📞 Support")
async def support_handler(message: types.Message):
    support_text = "📞 Contact Support\nEmail: support@example.com\nTelegram: @support_bot"
    await message.answer(support_text)

@dp.message_handler(lambda m: m.text == "📡 Proxy MB Check Bot")
async def proxy_check_handler(message: types.Message):
    check_text = "📡 Proxy MB Check Bot\nStart checking your proxies: @proxy_check_bot"
    await message.answer(check_text)

@dp.message_handler(lambda m: m.text == "👨‍💻 Developer")
async def developer_handler(message: types.Message):
    dev_text = "👨‍💻 Developer\nDeveloped by: Your Name\nContact: @developer_username"
    await message.answer(dev_text)

@dp.message_handler(lambda m: m.text == "🔑 Buy CD Key")
async def buy_cdkey_handler(message: types.Message):
    cdkey_text = "🔑 CD Key Store\nNo CD Keys available at the moment."
    await message.answer(cdkey_text)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
