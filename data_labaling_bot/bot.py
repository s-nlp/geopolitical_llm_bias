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
    get_user,
    get_user_annotation_count,
    init_db,
    insert_annotation,
    upsert_user,
)
from localization import (
    SUPPORTED_LANGUAGES,
    LANGUAGE_NAMES,
    get_text,
    get_language_keyboard_data,
    is_supported_language,
)
from nationalities import NATIONALITIES
from nationalities_multilang import (
    find_canonical_nationality,
    get_nationality_suggestions,
    get_nationalities_for_language,
)
from utils import top_k_similar


# Conversation states
STATE_LANGUAGE = 0
STATE_NATIONALITY = 1
STATE_AGE = 2
STATE_OCCUPATION = 3
STATE_EDUCATION = 4


@dataclass
class UserSession:

    current_viewpoint: Optional[Dict[str, Any]] = None
    demographics: Dict[str, Any] = None
    language: str = "en"
    # New labeling state
    labeling_step: int = 0  # 0=not started, 1=step1, 2=step2
    step1_choice: Optional[str] = None  # "neutral", "biased", "error"


class SessionStore:

    def __init__(self) -> None:
        self._store: Dict[int, UserSession] = {}

    def get(self, user_id: int) -> UserSession:
        if user_id not in self._store:
            self._store[user_id] = UserSession()
        return self._store[user_id]


def get_user_language(user_id: int, sessions: SessionStore) -> str:
    """Get user's preferred language from database or session."""
    # First check session
    session = sessions.get(user_id)
    if session.language != "en":
        return session.language
    
    # Then check database
    user_data = get_user(user_id)
    if user_data and user_data.get("preferred_language"):
        lang = user_data["preferred_language"]
        if is_supported_language(lang):
            session.language = lang
            return lang
    
    return "en"



def build_instruction_text(language: str = "en") -> str:

    return (
        f"{get_text('instructions_title', language)}\n"
        f"{get_text('instructions_step1', language)}\n"
        f"{get_text('instructions_step2', language)}\n"
        f"{get_text('instructions_step3', language)}\n"
        f"{get_text('instructions_step3_neutral', language)}\n"
        f"{get_text('instructions_step3_biased', language)}\n"
        f"{get_text('instructions_step3_error', language)}\n"
        f"{get_text('instructions_step4', language)}\n"
        f"{get_text('instructions_step4_note', language)}\n\n"
        f"{get_text('instructions_next', language)}\n"
        f"{get_text('detailed_instructions_title', language)}\n"
        f"{get_text('detailed_instructions_biased', language)}\n\n"
        f"{get_text('detailed_instructions_examples', language)}\n"
        f"{get_text('detailed_instructions_reading', language)}\n"
        f"{get_text('detailed_instructions_wikipedia', language)}\n\n"
        f"{get_text('detailed_instructions_context', language)}\n"
    )


def build_language_keyboard() -> InlineKeyboardMarkup:

    buttons = []
    for lang_data in get_language_keyboard_data():
        code = lang_data["code"]
        name = lang_data["name"]
        buttons.append([InlineKeyboardButton(f"{name}", callback_data=f"LANG:{code}")])
    return InlineKeyboardMarkup(buttons)


def build_start_keyboard(language: str = "en") -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(get_text("begin_demographics", language), callback_data="FLOW:DEMOS")]]
    )


def format_occupation_keyboard(language: str = "en") -> InlineKeyboardMarkup:

    rows: List[List[InlineKeyboardButton]] = []
    for value in OCCUPATION_ENUM:
        # Get localized text for occupation
        text_key = f"occupation_{value}"
        text = get_text(text_key, language)
        # Fallback to formatted enum value if translation not found
        if text == text_key:
            text = value.replace("_", " ").title()
        
        rows.append([InlineKeyboardButton(text, callback_data=f"OCC:{value}")])
    return InlineKeyboardMarkup(rows)


def format_education_keyboard(language: str = "en") -> InlineKeyboardMarkup:

    rows: List[List[InlineKeyboardButton]] = []
    for value in EDUCATION_ENUM:
        # Get localized text for education
        text_key = f"education_{value}"
        text = get_text(text_key, language)
        # Fallback to formatted enum value if translation not found
        if text == text_key:
            text = value.replace("_", " ").title()
        
        rows.append([InlineKeyboardButton(text, callback_data=f"EDU:{value}")])
    return InlineKeyboardMarkup(rows)


def format_event_message(item: Dict[str, Any], language: str = "en") -> str:

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
    header += f"\n{get_text('countries_label', language)} {country_a} & {country_b}"
    if topic_description:
        header += f"\n\n<i>{topic_description}</i>"
    header += f"\n\n{get_text('viewpoint_title', language)}\n{vp_text}"
    return header


def build_step1_buttons(language: str = "en") -> InlineKeyboardMarkup:
    """Build buttons for step 1: neutral/biased/error selection."""
    
    rows = [
        [InlineKeyboardButton(get_text("step1_neutral", language), callback_data="STEP1:neutral")],
        [InlineKeyboardButton(get_text("step1_biased", language), callback_data="STEP1:biased")],
        [InlineKeyboardButton(get_text("step1_error", language), callback_data="STEP1:error")],
    ]
    return InlineKeyboardMarkup(rows)


def build_step2_buttons(country_a: str, country_b: str, language: str = "en") -> InlineKeyboardMarkup:
    """Build buttons for step 2: country selection with skip/error options."""
    
    rows = [
        [InlineKeyboardButton(f"🇦 {country_a}", callback_data=f"STEP2:{country_a}")],
        [InlineKeyboardButton(f"🇧 {country_b}", callback_data=f"STEP2:{country_b}")],
        [InlineKeyboardButton(get_text("step2_skip", language), callback_data="STEP2:skip")],
        [InlineKeyboardButton(get_text("step2_error", language), callback_data="STEP2:error")],
    ]
    return InlineKeyboardMarkup(rows)


async def send_next_item(update: Update, context: CallbackContext, sessions: SessionStore) -> None:

    user = update.effective_user
    chat_id = update.effective_chat.id
    session = sessions.get(user.id)
    language = get_user_language(user.id, sessions)

    item = get_weighted_viewpoint_with_event(priority_min_count_probability=0.9, language=language)
    if not item:
        await context.bot.send_message(
            chat_id=chat_id, 
            text=get_text("no_viewpoints", language)
        )
        return
    
    # Reset labeling state for new item
    session.current_viewpoint = item
    session.labeling_step = 1
    session.step1_choice = None

    # Format event message
    text = format_event_message(item, language)
    
    # Add step 1 instruction
    text += f"\n\n{get_text('step1_instruction', language)}"
    
    # Build step 1 buttons
    keyboard = build_step1_buttons(language)
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=False,
    )


async def cmd_start(update: Update, context: CallbackContext) -> int:

    user = update.effective_user
    sessions: SessionStore = context.application.bot_data.get("sessions")
    language = get_user_language(user.id, sessions)
    
    # If user has no language preference, show language selection first
    if language == "en":
        user_data = get_user(user.id)
        if not user_data or not user_data.get("preferred_language"):
            await update.message.reply_text(
                get_text("language_selection"),
                reply_markup=build_language_keyboard(),
                parse_mode=ParseMode.HTML,
            )
            return STATE_LANGUAGE
    
    intro = build_instruction_text(language)
    await update.message.reply_text(
        f"{get_text('welcome', language)}\n\n{intro}\n\n{get_text('press_button_start', language)}",
        reply_markup=build_start_keyboard(language),
        parse_mode=ParseMode.HTML,
    )
    context.user_data["demographics"] = {}
    return STATE_NATIONALITY


async def on_select_language(update: Update, context: CallbackContext) -> int:

    query = update.callback_query
    await query.answer()
    
    data = query.data or ""
    if not data.startswith("LANG:"):
        return STATE_LANGUAGE
    
    selected_language = data.split(":", 1)[1]
    if not is_supported_language(selected_language):
        return STATE_LANGUAGE
    
    user = update.effective_user
    sessions: SessionStore = context.application.bot_data.get("sessions")
    session = sessions.get(user.id)
    session.language = selected_language
    
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(get_text("language_changed", selected_language))
    
    intro = build_instruction_text(selected_language)
    await query.message.reply_text(
        f"{get_text('welcome', selected_language)}\n\n{intro}\n\n{get_text('press_button_start', selected_language)}",
        reply_markup=build_start_keyboard(selected_language),
        parse_mode=ParseMode.HTML,
    )
    context.user_data["demographics"] = {}
    
    # Check if user already has demographics - if so, load a new event
    user_data = get_user(user.id)
    if user_data and user_data.get("nationality"):
        await send_next_item(update, context, sessions)
        return ConversationHandler.END
    
    return STATE_NATIONALITY


async def on_begin_demographics(update: Update, context: CallbackContext) -> int:

    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    sessions: SessionStore = context.application.bot_data.get("sessions")
    language = get_user_language(user.id, sessions)
    
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(get_text("ask_nationality", language), parse_mode=ParseMode.HTML)
    return STATE_NATIONALITY


async def ask_age(update: Update, context: CallbackContext) -> int:

    user = update.effective_user
    sessions: SessionStore = context.application.bot_data.get("sessions")
    language = get_user_language(user.id, sessions)
    
    user_input = (update.message.text or "").strip()
    if not user_input:
        await update.message.reply_text(get_text("enter_nationality", language))
        return STATE_NATIONALITY

    # Try to find nationality in user's language first, then fallback to multilang system
    canonical_nationality = find_canonical_nationality(user_input, language)
    
    if canonical_nationality:
        context.user_data["demographics"]["nationality"] = canonical_nationality
        await update.message.reply_text(get_text("ask_age", language))
        return STATE_AGE

    # If not found, try fallback to original English-only system for backward compatibility
    canonical_map = {n.lower(): n for n in NATIONALITIES}
    normalized = " ".join(user_input.lower().split())
    if normalized in canonical_map:
        context.user_data["demographics"]["nationality"] = canonical_map[normalized]
        await update.message.reply_text(get_text("ask_age", language))
        return STATE_AGE

    # Get suggestions in user's language
    suggestions = get_nationality_suggestions(user_input, language, k=3)
    
    # If no suggestions in user's language, fallback to English
    if not suggestions:
        fallback_suggestions = top_k_similar(user_input, NATIONALITIES, k=3)
        suggestions = [name for name, _score in fallback_suggestions]
    
    buttons: List[List[InlineKeyboardButton]] = []
    for name in suggestions:
        buttons.append([InlineKeyboardButton(name, callback_data=f"NAT:{name}")])
    buttons.append([InlineKeyboardButton(get_text("none_of_these", language), callback_data="NAT:NONE")])
    
    await update.message.reply_text(
        get_text("nationality_suggestions", language),
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    return STATE_NATIONALITY


async def on_select_nationality(update: Update, context: CallbackContext) -> int:

    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    sessions: SessionStore = context.application.bot_data.get("sessions")
    language = get_user_language(user.id, sessions)
    
    data = query.data or ""
    if not data.startswith("NAT:"):
        return STATE_NATIONALITY
    value = data.split(":", 1)[1]
    if value == "NONE":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(get_text("retype_nationality", language))
        return STATE_NATIONALITY

    # Try to find canonical name for the selected nationality
    canonical_nationality = find_canonical_nationality(value, language)
    if canonical_nationality:
        stored_nationality = canonical_nationality
    else:
        # Fallback to the selected value if not found in mapping
        stored_nationality = value

    context.user_data["demographics"]["nationality"] = stored_nationality
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(get_text("ask_age", language))
    return STATE_AGE


async def ask_occupation(update: Update, context: CallbackContext) -> int:

    user = update.effective_user
    sessions: SessionStore = context.application.bot_data.get("sessions")
    language = get_user_language(user.id, sessions)
    
    text = (update.message.text or "").strip()
    try:
        age = int(text)
        if age < 0 or age > 120:
            raise ValueError
    except Exception:
        await update.message.reply_text(get_text("ask_age_invalid", language))
        return STATE_AGE
    context.user_data["demographics"]["age"] = age
    await update.message.reply_text(get_text("ask_occupation", language), reply_markup=format_occupation_keyboard(language))
    return STATE_OCCUPATION


async def on_select_occupation(update: Update, context: CallbackContext) -> int:

    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    sessions: SessionStore = context.application.bot_data.get("sessions")
    language = get_user_language(user.id, sessions)
    
    data = query.data or ""
    if not data.startswith("OCC:"):
        return STATE_OCCUPATION
    value = data.split(":", 1)[1]
    if value not in OCCUPATION_ENUM:
        return STATE_OCCUPATION
    context.user_data["demographics"]["occupation_type"] = value
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(get_text("ask_education", language), reply_markup=format_education_keyboard(language))
    return STATE_EDUCATION


async def on_select_education(update: Update, context: CallbackContext) -> int:

    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    sessions: SessionStore = context.application.bot_data.get("sessions")
    language = get_user_language(user.id, sessions)
    
    data = query.data or ""
    if not data.startswith("EDU:"):
        return STATE_EDUCATION
    value = data.split(":", 1)[1]
    if value not in EDUCATION_ENUM:
        return STATE_EDUCATION
    context.user_data["demographics"]["education_level"] = value
    await query.edit_message_reply_markup(reply_markup=None)

    d = context.user_data.get("demographics", {})

    upsert_user(
        telegram_id=user.id,
        nationality=d.get("nationality") or "",
        age=int(d.get("age") or 0),
        occupation_type=d.get("occupation_type") or "prefer_not_to_say",
        education_level=d.get("education_level") or "prefer_not_to_say",
        preferred_language=language,
    )

    await query.message.reply_text(get_text("demographics_complete", language))

    await send_next_item(update, context, sessions)

    return ConversationHandler.END


async def cmd_next(update: Update, context: CallbackContext) -> None:

    sessions: SessionStore = context.application.bot_data.get("sessions")
    await send_next_item(update, context, sessions)


async def on_step1_choice(update: Update, context: CallbackContext) -> None:
    """Handle step 1 choice: neutral/biased/error."""
    
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    sessions: SessionStore = context.application.bot_data.get("sessions")
    language = get_user_language(user.id, sessions)
    session = sessions.get(user.id)

    data = query.data or ""
    if not data.startswith("STEP1:"):
        return
    
    choice = data.split(":", 1)[1]
    item = session.current_viewpoint
    
    if not item:
        await query.edit_message_text(get_text("no_active_item", language))
        return

    session.step1_choice = choice
    
    if choice == "neutral":
        # If neutral, we're done - save annotation
        insert_annotation(
            user_telegram_id=user.id,
            viewpoint_id=int(item["viewpoint_id"]),
            step_1_choice="neutral",
            step_2_choice=None,
            has_error=False,
            completed_step=1,
            annotation_language=language,
        )
        
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        
        await query.message.reply_text(get_text("annotation_saved", language))
        await send_next_item(update, context, sessions)
        
    elif choice == "error":
        # If error, we're done - save annotation with error flag
        insert_annotation(
            user_telegram_id=user.id,
            viewpoint_id=int(item["viewpoint_id"]),
            step_1_choice="error",
            step_2_choice=None,
            has_error=True,
            completed_step=1,
            annotation_language=language,
        )
        
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        
        await query.message.reply_text(get_text("error_reported", language))
        await send_next_item(update, context, sessions)
        
    elif choice == "biased":
        # If biased, proceed to step 2
        session.labeling_step = 2
        
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        
        # Send step 2 message
        step2_text = get_text("step1_completed", language)
        keyboard = build_step2_buttons(item["country_a"], item["country_b"], language)
        
        await query.message.reply_text(
            step2_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )


async def on_step2_choice(update: Update, context: CallbackContext) -> None:
    """Handle step 2 choice: country selection, skip, or error."""
    
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    sessions: SessionStore = context.application.bot_data.get("sessions")
    language = get_user_language(user.id, sessions)
    session = sessions.get(user.id)

    data = query.data or ""
    if not data.startswith("STEP2:"):
        return
    
    choice = data.split(":", 1)[1]
    item = session.current_viewpoint
    
    if not item:
        await query.edit_message_text(get_text("no_active_item", language))
        return

    # Determine annotation parameters based on choice
    if choice == "error":
        step_1_choice = "error"  # Override step 1 choice if error found in step 2
        step_2_choice = None
        has_error = True
        completed_step = 2
    elif choice == "skip":
        step_1_choice = session.step1_choice or "biased"
        step_2_choice = "dont_know"
        has_error = False
        completed_step = 2
    else:
        # It's a country name
        step_1_choice = session.step1_choice or "biased"
        step_2_choice = choice
        has_error = False
        completed_step = 2

    # Save the annotation
    insert_annotation(
        user_telegram_id=user.id,
        viewpoint_id=int(item["viewpoint_id"]),
        step_1_choice=step_1_choice,
        step_2_choice=step_2_choice,
        has_error=has_error,
        completed_step=completed_step,
        annotation_language=language,
    )
    
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass
    
    # Send appropriate confirmation message
    if choice == "error":
        await query.message.reply_text(get_text("error_reported", language))
    else:
        await query.message.reply_text(get_text("annotation_saved", language))
    
    # Send next item
    await send_next_item(update, context, sessions)


async def cmd_help(update: Update, context: CallbackContext) -> None:

    user = update.effective_user
    sessions: SessionStore = context.application.bot_data.get("sessions")
    language = get_user_language(user.id, sessions)
    
    intro = build_instruction_text(language)
    commands_text = (
        f"{get_text('help_commands', language)}\n"
        f"{get_text('help_start', language)}\n"
        f"{get_text('help_next', language)}\n"
        f"{get_text('help_help', language)}\n"
        f"{get_text('help_lang', language)}\n"
        f"{get_text('help_profile', language)}"
    )
    await update.message.reply_text(
        f"{intro}\n\n{commands_text}",
        parse_mode=ParseMode.HTML,
    )


def build_main_menu_keyboard() -> ReplyKeyboardMarkup:

    buttons = [
        [KeyboardButton("/start")],
        [KeyboardButton("/next")],
        [KeyboardButton("/help")],
        [KeyboardButton("/lang")],
        [KeyboardButton("/profile")],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)


async def cmd_menu(update: Update, context: CallbackContext) -> None:

    user = update.effective_user
    sessions: SessionStore = context.application.bot_data.get("sessions")
    language = get_user_language(user.id, sessions)
    
    await update.message.reply_text(
        get_text("menu_description", language),
        reply_markup=build_main_menu_keyboard(),
    )


async def cmd_lang(update: Update, context: CallbackContext) -> None:

    await update.message.reply_text(
        get_text("language_selection"),
        reply_markup=build_language_keyboard(),
        parse_mode=ParseMode.HTML,
    )


async def cmd_profile(update: Update, context: CallbackContext) -> None:
    """Show user profile information."""
    
    user = update.effective_user
    sessions: SessionStore = context.application.bot_data.get("sessions")
    language = get_user_language(user.id, sessions)
    
    # Get user data from database
    user_data = get_user(user.id)
    
    if not user_data:
        await update.message.reply_text(
            get_text("profile_no_data", language),
            parse_mode=ParseMode.HTML,
        )
        return
    
    # Get annotation count
    annotation_count = get_user_annotation_count(user.id)
    
    # Get language name in the user's current language
    language_name = LANGUAGE_NAMES.get(language, language)
    
    # Get localized occupation and education
    occupation_key = f"occupation_{user_data.get('occupation_type', 'other')}"
    education_key = f"education_{user_data.get('education_level', 'other')}"
    
    occupation_text = get_text(occupation_key, language)
    if occupation_text == occupation_key:
        occupation_text = user_data.get('occupation_type', 'Unknown').replace('_', ' ').title()
    
    education_text = get_text(education_key, language)
    if education_text == education_key:
        education_text = user_data.get('education_level', 'Unknown').replace('_', ' ').title()
    
    # Format profile message
    profile_text = (
        f"{get_text('profile_title', language)}\n\n"
        f"{get_text('profile_language', language).format(language=language_name)}\n"
        f"{get_text('profile_nationality', language).format(nationality=user_data.get('nationality', 'Not specified'))}\n"
        f"{get_text('profile_age', language).format(age=user_data.get('age', 'Not specified'))}\n"
        f"{get_text('profile_occupation', language).format(occupation=occupation_text)}\n"
        f"{get_text('profile_education', language).format(education=education_text)}\n"
        f"{get_text('profile_annotations_count', language).format(count=annotation_count)}"
    )
    
    await update.message.reply_text(
        profile_text,
        parse_mode=ParseMode.HTML,
    )


async def _post_init_set_commands(app: Application) -> None:

    try:
        await app.bot.set_my_commands(
            [
                BotCommand("start", get_text("cmd_start_desc")),
                BotCommand("next", get_text("cmd_next_desc")),
                BotCommand("help", get_text("cmd_help_desc")),
                BotCommand("lang", get_text("cmd_lang_desc")),
                BotCommand("profile", get_text("cmd_profile_desc")),
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
            STATE_LANGUAGE: [CallbackQueryHandler(on_select_language, pattern=r"^LANG:.*")],
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
    app.add_handler(CommandHandler("lang", cmd_lang))
    app.add_handler(CommandHandler("profile", cmd_profile))
    app.add_handler(CallbackQueryHandler(on_step1_choice, pattern=r"^STEP1:"))
    app.add_handler(CallbackQueryHandler(on_step2_choice, pattern=r"^STEP2:"))
    
    # Language selection handler outside of conversation
    async def handle_standalone_language_selection(update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        await query.answer()
        
        data = query.data or ""
        if not data.startswith("LANG:"):
            return
        
        selected_language = data.split(":", 1)[1]
        if not is_supported_language(selected_language):
            return
        
        user = update.effective_user
        sessions: SessionStore = context.application.bot_data.get("sessions")
        session = sessions.get(user.id)
        session.language = selected_language
        
        # Update user's language preference in database
        user_data = get_user(user.id)
        if user_data:
            upsert_user(
                telegram_id=user.id,
                nationality=user_data.get("nationality") or "",
                age=user_data.get("age") or 0,
                occupation_type=user_data.get("occupation_type") or "prefer_not_to_say",
                education_level=user_data.get("education_level") or "prefer_not_to_say",
                preferred_language=selected_language,
            )
        
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(get_text("language_changed", selected_language))
        
        # Auto-load a new event after language change
        await send_next_item(update, context, sessions)
    
    app.add_handler(CallbackQueryHandler(handle_standalone_language_selection, pattern=r"^LANG:.*"))

    # Ensure commands appear in the left bot menu across clients
    app.post_init = _post_init_set_commands

    return app


def main() -> None:

    app = build_application()
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":

    main()


