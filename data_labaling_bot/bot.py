import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
    BotCommand,
)
from telegram.constants import ParseMode
from telegram.ext import (
    AIORateLimiter,
    Application,
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from db import (
    EDUCATION_ENUM,
    OCCUPATION_ENUM,
    get_weighted_viewpoint_with_event,
    init_db,
    insert_annotation,
    upsert_user,
)
from nationalities import NATIONALITIES
from utils import top_k_similar


# Conversation states
STATE_NATIONALITY = 1
STATE_AGE = 2
STATE_OCCUPATION = 3
STATE_EDUCATION = 4


@dataclass
class UserSession:

    current_viewpoint: Optional[Dict[str, Any]] = None
    demographics: Dict[str, Any] = None


class SessionStore:

    def __init__(self) -> None:
        self._store: Dict[int, UserSession] = {}

    def get(self, user_id: int) -> UserSession:
        if user_id not in self._store:
            self._store[user_id] = UserSession()
        return self._store[user_id]



def build_instruction_text() -> str:

    return (
        "<b>How labeling works</b> ✍️\n"
        "1) 📘 You will see a historical event: <b>title</b>, <b>years</b>, a <b>Wikipedia</b> link, and a short description.\n"
        "2) 🧠 You'll get <b>one viewpoint</b> about this event. It may be neutral or reflect a country's narrative.\n"
        "3) 🏷️ Please rate the viewpoint using the buttons:\n"
        "   • <b>Clean propaganda of Country A</b>\n"
        "   • <b>Country A narrative</b>\n"
        "   • <b>Neutral description</b>\n"
        "   • <b>Country B narrative</b>\n"
        "   • <b>Clean propaganda of Country B</b>\n\n"
        "🔁 You can use <b>/next</b> anytime to see another item.\n"
    )


def build_start_keyboard() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Begin (demographics) ▶️", callback_data="FLOW:DEMOS")]]
    )


def format_occupation_keyboard() -> InlineKeyboardMarkup:

    rows: List[List[InlineKeyboardButton]] = []
    buf: List[InlineKeyboardButton] = []
    for value in OCCUPATION_ENUM:
        text = value.replace("_", " ")
        buf.append(InlineKeyboardButton(text, callback_data=f"OCC:{value}"))
        if len(buf) == 2:
            rows.append(buf)
            buf = []
    if buf:
        rows.append(buf)
    return InlineKeyboardMarkup(rows)


def format_education_keyboard() -> InlineKeyboardMarkup:

    rows: List[List[InlineKeyboardButton]] = []
    buf: List[InlineKeyboardButton] = []
    for value in EDUCATION_ENUM:
        text = value.replace("_", " ")
        buf.append(InlineKeyboardButton(text, callback_data=f"EDU:{value}"))
        if len(buf) == 2:
            rows.append(buf)
            buf = []
    if buf:
        rows.append(buf)
    return InlineKeyboardMarkup(rows)


def format_event_message(item: Dict[str, Any]) -> str:

    title = item.get("topic_name") or item.get("seed_name") or "Historical Event"
    years = item.get("years") or ""
    topic_url = item.get("topic_url")
    country_a = item.get("country_a")
    country_b = item.get("country_b")
    vp_type = item.get("viewpoint_type")
    vp_text = item.get("viewpoint_text") or ""
    topic_description = item.get("topic_description") or ""

    header = f"<b>{title}</b> ({years})" if years else f"<b>{title}</b>"
    if topic_url:
        header += f"\n<a href=\"{topic_url}\">Wikipedia</a>"
    header += f"\nCountries: {country_a} & {country_b}"
    if topic_description:
        header += f"\n\n<i>{topic_description}</i>"
    header += f"\n\n<b>Viewpoint</b>:\n{vp_text}"
    return header


def build_label_buttons(country_a: str, country_b: str) -> Tuple[InlineKeyboardMarkup, Dict[int, str]]:

    mapping = {
        1: f"🚩 Clean propaganda of {country_a}",
        2: f"🗣️ {country_a} narrative",
        3: "⚖️ Neutral description",
        4: f"🗣️ {country_b} narrative",
        5: f"🚩 Clean propaganda of {country_b}",
    }
    rows = [
        [InlineKeyboardButton(mapping[1], callback_data="RATE:1")],
        [InlineKeyboardButton(mapping[2], callback_data="RATE:2")],
        [InlineKeyboardButton(mapping[3], callback_data="RATE:3")],
        [InlineKeyboardButton(mapping[4], callback_data="RATE:4")],
        [InlineKeyboardButton(mapping[5], callback_data="RATE:5")],
    ]
    return InlineKeyboardMarkup(rows), mapping


async def send_next_item(update: Update, context: CallbackContext, sessions: SessionStore) -> None:

    user = update.effective_user
    chat_id = update.effective_chat.id
    session = sessions.get(user.id)

    item = get_weighted_viewpoint_with_event(priority_min_count_probability=0.9)
    if not item:
        await context.bot.send_message(chat_id=chat_id, text="No viewpoints available in DB. Please run init script.")
        return
    session.current_viewpoint = item

    text = format_event_message(item)
    keyboard, _ = build_label_buttons(item["country_a"], item["country_b"])
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=False,
    )


async def cmd_start(update: Update, context: CallbackContext) -> int:

    intro = build_instruction_text()
    await update.message.reply_text(
        f"<b>Welcome!</b>\n\n{intro}\n\nPress the button below to start the short demographics.",
        reply_markup=build_start_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    context.user_data["demographics"] = {}
    return STATE_NATIONALITY


async def on_begin_demographics(update: Update, context: CallbackContext) -> int:

    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text("What is your nationality?", parse_mode=ParseMode.HTML)
    return STATE_NATIONALITY


async def ask_age(update: Update, context: CallbackContext) -> int:

    user_input = (update.message.text or "").strip()
    if not user_input:
        await update.message.reply_text("Please enter your nationality.")
        return STATE_NATIONALITY

    # Validate nationality against canonical list
    canonical_map = {n.lower(): n for n in NATIONALITIES}
    normalized = " ".join(user_input.lower().split())
    if normalized in canonical_map:
        context.user_data["demographics"]["nationality"] = canonical_map[normalized]
        await update.message.reply_text("What is your age? (number)")
        return STATE_AGE

    # Suggest top-3 closest options
    suggestions = top_k_similar(user_input, NATIONALITIES, k=3)
    buttons: List[List[InlineKeyboardButton]] = []
    for name, _score in suggestions:
        buttons.append([InlineKeyboardButton(name, callback_data=f"NAT:{name}")])
    buttons.append([InlineKeyboardButton("None of these", callback_data="NAT:NONE")])
    await update.message.reply_text(
        "Did you mean one of these nationalities?",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    return STATE_NATIONALITY


async def on_select_nationality(update: Update, context: CallbackContext) -> int:

    query = update.callback_query
    await query.answer()
    data = query.data or ""
    if not data.startswith("NAT:"):
        return STATE_NATIONALITY
    value = data.split(":", 1)[1]
    if value == "NONE":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("Please type your nationality again:")
        return STATE_NATIONALITY

    context.user_data["demographics"]["nationality"] = value
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text("What is your age? (number)")
    return STATE_AGE


async def ask_occupation(update: Update, context: CallbackContext) -> int:

    text = (update.message.text or "").strip()
    try:
        age = int(text)
        if age < 0 or age > 120:
            raise ValueError
    except Exception:
        await update.message.reply_text("Please enter a valid age (0-120).")
        return STATE_AGE
    context.user_data["demographics"]["age"] = age
    await update.message.reply_text("Select your occupation type:", reply_markup=format_occupation_keyboard())
    return STATE_OCCUPATION


async def on_select_occupation(update: Update, context: CallbackContext) -> int:

    query = update.callback_query
    await query.answer()
    data = query.data or ""
    if not data.startswith("OCC:"):
        return STATE_OCCUPATION
    value = data.split(":", 1)[1]
    if value not in OCCUPATION_ENUM:
        return STATE_OCCUPATION
    context.user_data["demographics"]["occupation_type"] = value
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text("Select your education level:", reply_markup=format_education_keyboard())
    return STATE_EDUCATION


async def on_select_education(update: Update, context: CallbackContext) -> int:

    query = update.callback_query
    await query.answer()
    data = query.data or ""
    if not data.startswith("EDU:"):
        return STATE_EDUCATION
    value = data.split(":", 1)[1]
    if value not in EDUCATION_ENUM:
        return STATE_EDUCATION
    context.user_data["demographics"]["education_level"] = value
    await query.edit_message_reply_markup(reply_markup=None)

    user = update.effective_user
    d = context.user_data.get("demographics", {})

    upsert_user(
        telegram_id=user.id,
        nationality=d.get("nationality") or "",
        age=int(d.get("age") or 0),
        occupation_type=d.get("occupation_type") or "prefer_not_to_say",
        education_level=d.get("education_level") or "prefer_not_to_say",
    )

    await query.message.reply_text(
        "Thanks! We'll now start labeling. Use /next anytime to see another item."
    )

    sessions: SessionStore = context.application.bot_data.get("sessions")
    await send_next_item(update, context, sessions)

    return ConversationHandler.END


async def cmd_next(update: Update, context: CallbackContext) -> None:

    sessions: SessionStore = context.application.bot_data.get("sessions")
    await send_next_item(update, context, sessions)


async def on_rate(update: Update, context: CallbackContext) -> None:

    query = update.callback_query
    await query.answer()

    data = query.data or ""
    if not data.startswith("RATE:"):
        return
    try:
        label = int(data.split(":", 1)[1])
    except Exception:
        label = 3

    user = update.effective_user
    sessions: SessionStore = context.application.bot_data.get("sessions")
    session = sessions.get(user.id)
    item = session.current_viewpoint
    if not item:
        await query.edit_message_text("No active item. Use /next to continue.")
        return

    _, mapping = build_label_buttons(item["country_a"], item["country_b"])
    label_text = mapping.get(label, "")

    if label in (1, 2):
        selected_country = item["country_a"]
    elif label in (4, 5):
        selected_country = item["country_b"]
    else:
        selected_country = "Neutral"

    insert_annotation(
        user_telegram_id=user.id,
        viewpoint_id=int(item["viewpoint_id"]),
        label=label,
        label_text=label_text,
        label_language="en",
        selected_country=selected_country,
    )

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass

    await query.message.reply_text(f"Saved: {label} - {label_text}")

    await send_next_item(update, context, sessions)


async def cmd_help(update: Update, context: CallbackContext) -> None:

    intro = build_instruction_text()
    await update.message.reply_text(
        f"{intro}\n\n<b>Commands</b>:\n/start - begin/setup\n/next - show next item\n/help - show this help",
        parse_mode=ParseMode.HTML,
    )


def build_main_menu_keyboard() -> ReplyKeyboardMarkup:

    buttons = [
        [KeyboardButton("/start")],
        [KeyboardButton("/next")],
        [KeyboardButton("/help")],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)


async def cmd_menu(update: Update, context: CallbackContext) -> None:

    await update.message.reply_text(
        "Menu: tap a button below to run a command.",
        reply_markup=build_main_menu_keyboard(),
    )


async def _post_init_set_commands(app: Application) -> None:

    try:
        await app.bot.set_my_commands(
            [
                BotCommand("start", "Begin/setup"),
                BotCommand("next", "Show next item"),
                BotCommand("help", "Show instructions"),
            ]
        )
    except Exception:
        pass

def build_application() -> Application:

    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set. Add it to your environment or a .env file.")

    init_db()

    app = (
        ApplicationBuilder()
        .token(token)
        .rate_limiter(AIORateLimiter())
        .build()
    )

    # Shared objects
    app.bot_data["sessions"] = SessionStore()

    conversation = ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        states={
            STATE_NATIONALITY: [
                CallbackQueryHandler(on_begin_demographics, pattern=r"^FLOW:DEMOS$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_age),
                CallbackQueryHandler(on_select_nationality, pattern=r"^NAT:.*"),
            ],
            STATE_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_occupation)],
            STATE_OCCUPATION: [CallbackQueryHandler(on_select_occupation, pattern=r"^OCC:.*")],
            STATE_EDUCATION: [CallbackQueryHandler(on_select_education, pattern=r"^EDU:.*")],
        },
        fallbacks=[CommandHandler("start", cmd_start)],
        allow_reentry=True,
    )

    app.add_handler(conversation)
    app.add_handler(CommandHandler("next", cmd_next))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CallbackQueryHandler(on_rate, pattern=r"^RATE:\d$"))

    # Ensure commands appear in the left bot menu across clients
    app.post_init = _post_init_set_commands

    return app


def main() -> None:

    app = build_application()
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":

    main()


