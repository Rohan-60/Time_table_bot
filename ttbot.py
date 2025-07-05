import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime
import asyncio

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Actual timetable data from SCMS School of Engineering and Technology
TIMETABLE = {
    'CS1': {
        'Monday': ['Math', 'Physics', 'Programming', 'Break', 'Database', 'Network', 'Lab'],
        'Tuesday': ['Database', 'Math', 'OS', 'Break', 'Programming', 'Physics', 'Lab'],
        'Wednesday': ['Network', 'Database', 'Math', 'Break', 'OS', 'Programming', 'Lab'],
        'Thursday': ['Programming', 'Network', 'Physics', 'Break', 'Math', 'Database', 'Lab'],
        'Friday': ['OS', 'Programming', 'Network', 'Break', 'Physics', 'Math', 'Lab'],
        'Saturday': ['Physics', 'OS', 'Database', 'Break', 'Network', 'Programming', 'Lab']
    },
    'CS2': {
        'Monday': ['Database', 'Programming', 'Math', 'Break', 'Physics', 'OS', 'Lab'],
        'Tuesday': ['Math', 'Database', 'Network', 'Break', 'Programming', 'Physics', 'Lab'],
        'Wednesday': ['Programming', 'Math', 'Database', 'Break', 'Network', 'OS', 'Lab'],
        'Thursday': ['Physics', 'Programming', 'Math', 'Break', 'Database', 'Network', 'Lab'],
        'Friday': ['Network', 'Physics', 'OS', 'Break', 'Math', 'Database', 'Lab'],
        'Saturday': ['OS', 'Network', 'Programming', 'Break', 'Physics', 'Math', 'Lab']
    },
    'CS3': {
        'Monday': ['AI', 'Database', 'Programming', 'Break', 'Math', 'Network', 'Lab'],
        'Tuesday': ['Programming', 'AI', 'Math', 'Break', 'Database', 'OS', 'Lab'],
        'Wednesday': ['Math', 'Programming', 'AI', 'Break', 'Network', 'Database', 'Lab'],
        'Thursday': ['Database', 'Math', 'Programming', 'Break', 'AI', 'Network', 'Lab'],
        'Friday': ['Network', 'Database', 'AI', 'Break', 'Programming', 'Math', 'Lab'],
        'Saturday': ['OS', 'Network', 'Database', 'Break', 'AI', 'Programming', 'Lab']
    },
    'CS4': {
        'Monday': ['MPMC', 'SS', 'CN', 'FLAT', 'Lunch Break', 'SS/DMS Lab', 'Lab'],
        'Tuesday': ['MPMC', 'CN', 'DM', 'MPMC', 'Lunch Break', 'SS', 'MSS', 'SS'],
        'Wednesday': ['FLAT', 'MSS', 'FLAT', 'MPMC', 'Lunch Break', 'DM', 'MPMC', 'CN'],
        'Thursday': ['CN', 'SS/DMS Lab', 'Lunch Break', 'FLAT', 'CN', 'DM'],
        'Friday': ['SS', 'MPMC', 'FLAT', 'SS', 'Lunch Break', 'MSS', 'CN', 'FLAT'],
        'Saturday': ['No Classes', 'No Classes', 'No Classes', 'No Classes', 'No Classes', 'No Classes', 'No Classes']
    },
    'AI': {
        'Monday': ['ML', 'Deep Learning', 'Math', 'Break', 'Statistics', 'Programming', 'Lab'],
        'Tuesday': ['Statistics', 'ML', 'Deep Learning', 'Break', 'Math', 'Programming', 'Lab'],
        'Wednesday': ['Programming', 'Statistics', 'ML', 'Break', 'Deep Learning', 'Math', 'Lab'],
        'Thursday': ['Deep Learning', 'Programming', 'Statistics', 'Break', 'ML', 'Math', 'Lab'],
        'Friday': ['Math', 'Deep Learning', 'Programming', 'Break', 'Statistics', 'ML', 'Lab'],
        'Saturday': ['ML', 'Math', 'Deep Learning', 'Break', 'Programming', 'Statistics', 'Lab']
    },
    'DS': {
        'Monday': ['Statistics', 'Data Mining', 'Programming', 'Break', 'Math', 'Visualization', 'Lab'],
        'Tuesday': ['Programming', 'Statistics', 'Data Mining', 'Break', 'Visualization', 'Math', 'Lab'],
        'Wednesday': ['Math', 'Programming', 'Statistics', 'Break', 'Data Mining', 'Visualization', 'Lab'],
        'Thursday': ['Data Mining', 'Math', 'Programming', 'Break', 'Statistics', 'Visualization', 'Lab'],
        'Friday': ['Visualization', 'Data Mining', 'Math', 'Break', 'Programming', 'Statistics', 'Lab'],
        'Saturday': ['Statistics', 'Visualization', 'Data Mining', 'Break', 'Math', 'Programming', 'Lab']
    }
}

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
PERIODS = ['Period 1', 'Period 2', 'Period 3', 'Period 4', 'Lunch Break', 'Period 5', 'Period 6', 'Period 7']

# Subject codes and their full names for CS4
SUBJECT_INFO = {
    'MPMC': 'Microprocessors and Microcontrollers (CST 307)',
    'SS': 'System Software (CST 305)',
    'CN': 'Computer Networks (CST 303)',
    'FLAT': 'Formal Languages and Automata Theory (CST 301)',
    'MSS': 'Management of Software Systems (CST 309)',
    'DM': 'Disaster Management (MCN301)',
    'SS/DMS Lab': 'System Software and Database Management Systems Lab',
    'No Classes': 'No Classes Scheduled'
}

# Time slots for periods based on actual timetable
TIME_SLOTS = {
    'Period 1': '8:45 - 9:35',
    'Period 2': '9:35 - 10:25',
    'Period 3': '10:35 - 11:30',
    'Period 4': '11:30 - 12:20',
    'Lunch Break': '12:20 - 1:05',
    'Period 5': '1:05 - 1:55',
    'Period 6': '2:05 - 2:55',
    'Period 7': '2:55 - 3:45'
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton("CS1", callback_data='section_CS1')],
        [InlineKeyboardButton("CS2", callback_data='section_CS2')],
        [InlineKeyboardButton("CS3", callback_data='section_CS3')],
        [InlineKeyboardButton("CS4", callback_data='section_CS4')],
        [InlineKeyboardButton("AI", callback_data='section_AI')],
        [InlineKeyboardButton("DS", callback_data='section_DS')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        '🎓 Welcome to Department Timetable Bot!\n\n'
        'Please select your section:',
        reply_markup=reply_markup
    )

async def section_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle section selection."""
    query = update.callback_query
    await query.answer()
    
    section = query.data.split('_')[1]
    context.user_data['section'] = section
    
    keyboard = [
        [InlineKeyboardButton("📅 Full Week Timetable", callback_data='view_week')],
        [InlineKeyboardButton("📋 Today's Timetable", callback_data='view_today')],
        [InlineKeyboardButton("🕐 Specific Period", callback_data='view_period')],
        [InlineKeyboardButton("🔙 Back to Sections", callback_data='back_to_sections')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f'📚 Section: {section}\n\n'
        'What would you like to view?',
        reply_markup=reply_markup
    )

async def view_week(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show full week timetable."""
    query = update.callback_query
    await query.answer()
    
    section = context.user_data.get('section')
    if not section:
        await query.edit_message_text('Please select a section first.')
        return
    
    message = f'📅 **{section} - Full Week Timetable**\n\n'
    
    for day in DAYS:
        message += f'**{day}:**\n'
        for i, subject in enumerate(TIMETABLE[section][day]):
            period = PERIODS[i] if i < len(PERIODS) else f'Period {i+1}'
            time_slot = TIME_SLOTS.get(period, f'{9+i}:00 - {10+i}:00')
            message += f'  {period} ({time_slot}): {subject}\n'
        message += '\n'
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data=f'section_{section}')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def view_today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show today's timetable."""
    query = update.callback_query
    await query.answer()
    
    section = context.user_data.get('section')
    if not section:
        await query.edit_message_text('Please select a section first.')
        return
    
    today = datetime.now().strftime('%A')
    
    if today not in DAYS:
        message = f'📋 **{section} - {today}**\n\nNo classes today! 🎉'
    else:
        message = f'📋 **{section} - {today}**\n\n'
        for i, subject in enumerate(TIMETABLE[section][today]):
            period = PERIODS[i] if i < len(PERIODS) else f'Period {i+1}'
            time_slot = TIME_SLOTS.get(period, f'{9+i}:00 - {10+i}:00')
            message += f'{period} ({time_slot}): **{subject}**\n'
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data=f'section_{section}')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def view_period(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show period selection."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Period 1", callback_data='period_0')],
        [InlineKeyboardButton("Period 2", callback_data='period_1')],
        [InlineKeyboardButton("Period 3", callback_data='period_2')],
        [InlineKeyboardButton("Period 4", callback_data='period_3')],
        [InlineKeyboardButton("Lunch Break", callback_data='period_4')],
        [InlineKeyboardButton("Period 5", callback_data='period_5')],
        [InlineKeyboardButton("Period 6", callback_data='period_6')],
        [InlineKeyboardButton("Period 7", callback_data='period_7')],
        [InlineKeyboardButton("🔙 Back", callback_data=f'section_{context.user_data.get("section")}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        '🕐 Select a period to view:',
        reply_markup=reply_markup
    )

async def show_period(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show specific period details."""
    query = update.callback_query
    await query.answer()
    
    section = context.user_data.get('section')
    period_index = int(query.data.split('_')[1])
    
    if not section:
        await query.edit_message_text('Please select a section first.')
        return
    
    today = datetime.now().strftime('%A')
    period_name = PERIODS[period_index] if period_index < len(PERIODS) else f'Period {period_index+1}'
    time_slot = TIME_SLOTS.get(period_name, f'{9+period_index}:00 - {10+period_index}:00')
    
    if today not in DAYS:
        subject = 'No classes today!'
    else:
        subjects = TIMETABLE[section][today]
        subject = subjects[period_index] if period_index < len(subjects) else 'No class'
    
    message = f'🕐 **{section} - {period_name}**\n\n'
    message += f'📅 Day: {today}\n'
    message += f'⏰ Time: {time_slot}\n'
    message += f'📚 Subject: **{subject}**\n'
    
    # Add subject details for CS4
    if section == 'CS4' and subject in SUBJECT_INFO:
        message += f'📖 Full Name: {SUBJECT_INFO[subject]}'
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Periods", callback_data='view_period')],
        [InlineKeyboardButton("🏠 Main Menu", callback_data=f'section_{section}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def back_to_sections(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Go back to section selection."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("CS1", callback_data='section_CS1')],
        [InlineKeyboardButton("CS2", callback_data='section_CS2')],
        [InlineKeyboardButton("CS3", callback_data='section_CS3')],
        [InlineKeyboardButton("CS4", callback_data='section_CS4')],
        [InlineKeyboardButton("AI", callback_data='section_AI')],
        [InlineKeyboardButton("DS", callback_data='section_DS')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        '🎓 Welcome to Department Timetable Bot!\n\n'
        'Please select your section:',
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    data = query.data
    
    if data.startswith('section_'):
        await section_selected(update, context)
    elif data == 'view_week':
        await view_week(update, context)
    elif data == 'view_today':
        await view_today(update, context)
    elif data == 'view_period':
        await view_period(update, context)
    elif data.startswith('period_'):
        await show_period(update, context)
    elif data == 'back_to_sections':
        await back_to_sections(update, context)

def main() -> None:
    """Start the bot."""
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token from BotFather
    application = Application.builder().token('8110593551:AAEym3x78ffkKjgVCNzTtCWkpH5Xni9M6-E').build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()