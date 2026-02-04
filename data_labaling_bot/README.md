## Data Labeling Telegram Bot

This bot helps collect human evaluations of whether a historical viewpoint is neutral or reflects a specific national narrative.

Features:
- **Multi-language support**: Arabic, English, French, Hebrew, Russian, Chinese, German
- **Language selection**: Users select their preferred language at setup or via `/lang` command
- **Localized content**: Historical events and viewpoints are shown in the user's selected language
- Demographic intake: nationality, age, occupation type, education level, preferred language
- Nationality validation with fuzzy suggestions (top-5) if the input is not recognized
- Presents one viewpoint per historical event from the dataset
- Five-point labeling with dynamic country names (localized)
- Stores user profiles and annotations in SQLite (`bot.db`) with language tracking

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (create a `.env` in the repository root or set in shell):
```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
# Optional: override dataset path (defaults to translated dataset)
DATASET_PATH=/absolute/path/to/final_dataset_with_propaganda_translated.json
```

3. Run the bot:
```bash
python -m data_labaling_bot.bot
```

SQLite database file `bot.db` will be created in `data_labaling_bot/`.

If your nationality input is not in the canonical list, the bot will show five closest matches to choose from or let you retype.

### Commands
Available bot commands:
- `/start` - Begin setup (includes language selection for new users)
- `/next` - Show next item to label
- `/help` - Show instructions and commands
- `/lang` - Change language at any time

### Labels
The five options presented to annotators (shown in selected language):
- Clean propaganda of Country A
- Country A narrative
- Neutral description
- Country B narrative
- Clean propaganda of Country B

Where Country A/County B are derived from the event's `countries` field.

### Demographic enums
- Occupation: `student`, `academic_research`, `engineer_tech`, `business_finance`, `government_public`, `media_journalism`, `healthcare`, `education_teacher`, `service_trade`, `unemployed`, `retired`, `other`, `prefer_not_to_say`
- Education: `high_school_or_less`, `bachelor`, `master`, `doctorate`, `professional_degree`, `other`, `prefer_not_to_say`


