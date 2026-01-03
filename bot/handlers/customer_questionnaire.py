"""Customer handlers for filling questionnaires (semi-private plans)."""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.api_client import api_client

logger = logging.getLogger(__name__)


def get_question_keyboard(question: dict, current_answer: str = None, is_multi_choice: bool = False, selected_values: list = None) -> InlineKeyboardMarkup:
    """Generate keyboard for a question based on its type."""
    keyboard = []
    input_type = question.get('input_type', '')
    question_id = question.get('id', '')
    is_required = question.get('is_required', True)
    
    if input_type == 'SINGLE_CHOICE':
        options = question.get('options', [])
        for opt in options:
            value = opt.get('value', '')
            label = opt.get('label_fa', value)
            # Mark selected option
            if current_answer == value:
                label = f"✅ {label}"
            keyboard.append([InlineKeyboardButton(label, callback_data=f"qans_{question_id}_{value}")])
    
    elif input_type == 'MULTI_CHOICE':
        options = question.get('options', [])
        selected = selected_values or []
        for opt in options:
            value = opt.get('value', '')
            label = opt.get('label_fa', value)
            # Mark selected options
            if value in selected:
                label = f"☑️ {label}"
            else:
                label = f"☐ {label}"
            keyboard.append([InlineKeyboardButton(label, callback_data=f"qmulti_{question_id}_{value}")])
        keyboard.append([InlineKeyboardButton("✅ تایید انتخاب‌ها", callback_data=f"qmulti_done_{question_id}")])
    
    elif input_type == 'COLOR_PICKER':
        # Color palette
        colors = [
            ("🔴", "red"), ("🟠", "orange"), ("🟡", "yellow"), ("🟢", "green"),
            ("🔵", "blue"), ("🟣", "purple"), ("🟤", "brown"), ("⚫", "black"),
            ("⚪", "white"), ("🩷", "pink"), ("🩵", "lightblue"), ("🎨", "custom")
        ]
        row = []
        for i, (icon, value) in enumerate(colors):
            row.append(InlineKeyboardButton(icon, callback_data=f"qcolor_{question_id}_{value}"))
            if len(row) == 4:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
    
    elif input_type == 'SCALE':
        # Scale 1-5 or 1-10 based on validation rules
        rules = question.get('validation_rules', {}) or {}
        max_val = rules.get('max_value', 5)
        row = []
        for i in range(1, min(max_val + 1, 11)):
            row.append(InlineKeyboardButton(str(i), callback_data=f"qscale_{question_id}_{i}"))
            if len(row) == 5:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
    
    # Navigation buttons
    nav_row = []
    if not is_required:
        nav_row.append(InlineKeyboardButton("⏭️ رد کردن", callback_data=f"q_skip_{question_id}"))
    nav_row.append(InlineKeyboardButton("🔙 سوال قبلی", callback_data="q_prev"))
    keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")])
    
    return InlineKeyboardMarkup(keyboard)


def format_question_text(question: dict, current_idx: int, total: int, section_title: str = None) -> str:
    """Format question text for display."""
    is_required = question.get('is_required', True)
    required_text = "(اجباری)" if is_required else "(اختیاری)"
    
    text = f"❓ سوال {current_idx} از {total} {required_text}\n\n"
    text += f"📝 {question.get('question_fa', '')}\n"
    
    if question.get('help_text_fa'):
        text += f"\n💡 راهنما: {question.get('help_text_fa')}"
    
    return text


async def start_questionnaire(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the questionnaire flow after plan selection."""
    query = update.callback_query
    
    plan_id = context.user_data.get('selected_plan_id')
    if not plan_id:
        await query.answer("خطا: پلن انتخاب نشده است", show_alert=True)
        return
    
    # Get sections and questions for the plan
    sections = await api_client.get_sections(plan_id, active_only=True)
    questions = await api_client.get_questions(plan_id, active_only=True)
    
    if not questions:
        await query.message.edit_text("❌ هیچ سوالی برای این پلن تعریف نشده است.")
        return
    
    # Initialize questionnaire state
    context.user_data['questionnaire'] = {
        'plan_id': plan_id,
        'sections': sections or [],
        'questions': questions,
        'current_index': 0,
        'answers': {},  # question_id -> answer
        'multi_choice_temp': {},  # For multi-choice selections in progress
    }
    
    # Get plan info
    plan = await api_client.get_design_plan(plan_id)
    plan_name = plan.get('name_fa', '') if plan else ''
    
    # Calculate section info
    section_count = len(sections) if sections else 0
    section_text = f"تعداد بخش‌ها: {section_count}" if section_count else ""
    
    text = (
        f"📝 پرسشنامه طراحی\n\n"
        f"پلن «{plan_name}» انتخاب شد.\n\n"
        f"برای طراحی سفارشی، لطفا به سوالات زیر پاسخ دهید.\n"
        f"این اطلاعات به طراح کمک می‌کند طرحی مطابق سلیقه شما بسازد.\n"
    )
    
    if sections:
        first_section = sections[0]
        text += f"\n━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📂 بخش ۱ از {section_count}: {first_section.get('title_fa', '')}\n"
        if first_section.get('description_fa'):
            text += f"{first_section.get('description_fa')}\n"
        text += f"━━━━━━━━━━━━━━━━━━━━"
    
    keyboard = [
        [InlineKeyboardButton("▶️ شروع", callback_data="q_start")],
        [InlineKeyboardButton("🔙 انتخاب پلن دیگر", callback_data="order_back_plan")],
        [InlineKeyboardButton("❌ انصراف از سفارش", callback_data="order_cancel")]
    ]
    
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def show_current_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display the current question."""
    query = update.callback_query if update.callback_query else None
    
    q_data = context.user_data.get('questionnaire', {})
    questions = q_data.get('questions', [])
    current_idx = q_data.get('current_index', 0)
    
    if current_idx >= len(questions):
        # All questions answered, show summary
        await show_questionnaire_summary(update, context)
        return
    
    question = questions[current_idx]
    question_id = question.get('id')
    input_type = question.get('input_type', '')
    
    # Get current answer if any
    current_answer = q_data.get('answers', {}).get(question_id)
    multi_selected = q_data.get('multi_choice_temp', {}).get(question_id, [])
    
    # Format question text
    text = format_question_text(question, current_idx + 1, len(questions))
    
    # Add input hint based on type
    if input_type in ['TEXT', 'TEXTAREA']:
        text += "\n\n📲 پاسخ خود را تایپ کنید:"
    elif input_type == 'NUMBER':
        text += "\n\n🔢 یک عدد وارد کنید:"
    elif input_type == 'IMAGE_UPLOAD':
        text += "\n\n📷 یک تصویر ارسال کنید:"
    elif input_type == 'FILE_UPLOAD':
        text += "\n\n📎 یک فایل ارسال کنید:"
    elif input_type == 'SINGLE_CHOICE':
        text += "\n\nیک گزینه انتخاب کنید:"
    elif input_type == 'MULTI_CHOICE':
        if multi_selected:
            text += f"\n\nگزینه‌های انتخاب شده: {', '.join(multi_selected)}"
        else:
            text += "\n\nگزینه‌های مورد نظر را انتخاب کنید:"
    elif input_type == 'COLOR_PICKER':
        text += "\n\nیک رنگ انتخاب کنید:"
    elif input_type == 'DATE_PICKER':
        text += "\n\n📅 تاریخ را وارد کنید (مثلا: 1403/01/15):"
    elif input_type == 'SCALE':
        text += "\n\nیک امتیاز انتخاب کنید:"
    
    keyboard = get_question_keyboard(question, current_answer, input_type == 'MULTI_CHOICE', multi_selected)
    
    if query:
        await query.message.edit_text(text, reply_markup=keyboard)
    else:
        await update.message.reply_text(text, reply_markup=keyboard)


async def handle_question_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries for questions."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    q_data = context.user_data.get('questionnaire', {})
    questions = q_data.get('questions', [])
    current_idx = q_data.get('current_index', 0)
    
    if data == "q_start":
        await show_current_question(update, context)
        return
    
    if data == "q_prev":
        # Go to previous question
        if current_idx > 0:
            context.user_data['questionnaire']['current_index'] = current_idx - 1
        await show_current_question(update, context)
        return
    
    if data.startswith("q_skip_"):
        # Skip optional question
        context.user_data['questionnaire']['current_index'] = current_idx + 1
        await show_current_question(update, context)
        return
    
    if data.startswith("qans_"):
        # Single choice answer
        parts = data.split("_", 2)
        question_id = parts[1]
        value = parts[2]
        
        # Save answer
        if 'answers' not in context.user_data['questionnaire']:
            context.user_data['questionnaire']['answers'] = {}
        context.user_data['questionnaire']['answers'][question_id] = value
        
        # Move to next question
        context.user_data['questionnaire']['current_index'] = current_idx + 1
        await show_current_question(update, context)
        return
    
    if data.startswith("qmulti_"):
        if data.startswith("qmulti_done_"):
            # Finish multi-choice selection
            question_id = data.replace("qmulti_done_", "")
            selected = q_data.get('multi_choice_temp', {}).get(question_id, [])
            
            # Check if required and no selection
            question = questions[current_idx]
            if question.get('is_required') and not selected:
                await query.answer("لطفا حداقل یک گزینه انتخاب کنید", show_alert=True)
                return
            
            # Save answer
            context.user_data['questionnaire']['answers'][question_id] = selected
            # Clear temp
            if question_id in context.user_data['questionnaire'].get('multi_choice_temp', {}):
                del context.user_data['questionnaire']['multi_choice_temp'][question_id]
            
            # Move to next
            context.user_data['questionnaire']['current_index'] = current_idx + 1
            await show_current_question(update, context)
            return
        else:
            # Toggle multi-choice option
            parts = data.split("_", 2)
            question_id = parts[1]
            value = parts[2]
            
            if 'multi_choice_temp' not in context.user_data['questionnaire']:
                context.user_data['questionnaire']['multi_choice_temp'] = {}
            if question_id not in context.user_data['questionnaire']['multi_choice_temp']:
                context.user_data['questionnaire']['multi_choice_temp'][question_id] = []
            
            selected = context.user_data['questionnaire']['multi_choice_temp'][question_id]
            if value in selected:
                selected.remove(value)
            else:
                selected.append(value)
            
            # Refresh the question display
            await show_current_question(update, context)
            return
    
    if data.startswith("qcolor_"):
        # Color picker answer
        parts = data.split("_", 2)
        question_id = parts[1]
        value = parts[2]
        
        if value == "custom":
            # Ask for custom hex color
            context.user_data['awaiting_color_hex'] = question_id
            await query.message.edit_text(
                "🎨 کد رنگ HEX را وارد کنید:\n"
                "مثال: #FF5733",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="q_back_to_question")]
                ])
            )
            return
        
        # Save color answer
        context.user_data['questionnaire']['answers'][question_id] = value
        context.user_data['questionnaire']['current_index'] = current_idx + 1
        await show_current_question(update, context)
        return
    
    if data.startswith("qscale_"):
        # Scale answer
        parts = data.split("_", 2)
        question_id = parts[1]
        value = parts[2]
        
        context.user_data['questionnaire']['answers'][question_id] = value
        context.user_data['questionnaire']['current_index'] = current_idx + 1
        await show_current_question(update, context)
        return
    
    if data == "q_back_to_question":
        # Return to question from custom color input
        context.user_data.pop('awaiting_color_hex', None)
        await show_current_question(update, context)
        return
    
    if data == "q_confirm":
        # Confirm all answers and proceed
        await finalize_questionnaire(update, context)
        return
    
    if data == "q_edit_answers":
        # Go back to first question to edit
        context.user_data['questionnaire']['current_index'] = 0
        await show_current_question(update, context)
        return


async def handle_question_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle text input for questions. Returns True if handled."""
    q_data = context.user_data.get('questionnaire', {})
    if not q_data:
        return False
    
    questions = q_data.get('questions', [])
    current_idx = q_data.get('current_index', 0)
    
    if current_idx >= len(questions):
        return False
    
    question = questions[current_idx]
    question_id = question.get('id')
    input_type = question.get('input_type', '')
    
    # Check if we're awaiting custom color
    if context.user_data.get('awaiting_color_hex'):
        color = update.message.text.strip()
        if not color.startswith('#'):
            color = '#' + color
        
        # Validate
        result = await api_client.validate_answer(question_id, {"answer_text": color})
        if result and not result.get('is_valid'):
            await update.message.reply_text(
                f"❌ {result.get('error_message', 'کد رنگ نامعتبر است')}\n\n"
                "لطفا دوباره وارد کنید:"
            )
            return True
        
        context.user_data['questionnaire']['answers'][question_id] = color
        context.user_data['questionnaire']['current_index'] = current_idx + 1
        context.user_data.pop('awaiting_color_hex', None)
        await show_current_question(update, context)
        return True
    
    # Handle based on input type
    if input_type in ['TEXT', 'TEXTAREA', 'NUMBER', 'DATE_PICKER']:
        text = update.message.text.strip()
        
        # Validate
        result = await api_client.validate_answer(question_id, {"answer_text": text})
        if result and not result.get('is_valid'):
            await update.message.reply_text(
                f"❌ {result.get('error_message', 'پاسخ نامعتبر است')}\n\n"
                "لطفا دوباره وارد کنید:"
            )
            return True
        
        # Save answer
        context.user_data['questionnaire']['answers'][question_id] = text
        context.user_data['questionnaire']['current_index'] = current_idx + 1
        await show_current_question(update, context)
        return True
    
    return False


async def handle_question_photo_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle photo input for IMAGE_UPLOAD questions. Returns True if handled."""
    q_data = context.user_data.get('questionnaire', {})
    if not q_data:
        return False
    
    questions = q_data.get('questions', [])
    current_idx = q_data.get('current_index', 0)
    
    if current_idx >= len(questions):
        return False
    
    question = questions[current_idx]
    question_id = question.get('id')
    input_type = question.get('input_type', '')
    
    if input_type not in ['IMAGE_UPLOAD', 'FILE_UPLOAD']:
        return False
    
    if not update.message.photo and not update.message.document:
        await update.message.reply_text("❌ لطفا یک تصویر یا فایل ارسال کنید.")
        return True
    
    # Get file URL
    if update.message.photo:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
    else:
        file = await context.bot.get_file(update.message.document.file_id)
    
    if file.file_path.startswith("https://"):
        file_url = file.file_path
    else:
        bot_token = context.bot.token
        file_url = f"https://api.telegram.org/file/bot{bot_token}/{file.file_path}"
    
    # Save answer
    context.user_data['questionnaire']['answers'][question_id] = file_url
    context.user_data['questionnaire']['current_index'] = current_idx + 1
    
    await update.message.reply_text("✅ فایل دریافت شد!")
    await show_current_question(update, context)
    return True


async def show_questionnaire_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show summary of all answers before confirmation."""
    query = update.callback_query if update.callback_query else None
    
    q_data = context.user_data.get('questionnaire', {})
    questions = q_data.get('questions', [])
    answers = q_data.get('answers', {})
    sections = q_data.get('sections', [])
    
    text = "✅ پرسشنامه تکمیل شد!\n\n📋 خلاصه پاسخ‌های شما:\n"
    
    # Group by section if available
    current_section = None
    for i, q in enumerate(questions):
        q_id = q.get('id')
        section_id = q.get('section_id')
        
        # Find section title
        if section_id and section_id != current_section:
            for s in sections:
                if s.get('id') == section_id:
                    text += f"\n━━━ {s.get('title_fa', '')} ━━━\n"
                    current_section = section_id
                    break
        
        # Get answer
        answer = answers.get(q_id)
        if answer:
            if isinstance(answer, list):
                answer_text = "، ".join(answer)
            elif answer.startswith("http"):
                answer_text = "✅ ارسال شده"
            else:
                # Get label for single choice
                options = q.get('options', [])
                for opt in options:
                    if opt.get('value') == answer:
                        answer_text = opt.get('label_fa', answer)
                        break
                else:
                    answer_text = answer
        else:
            answer_text = "—"
        
        q_text = q.get('question_fa', '')[:40]
        text += f"• {q_text}: {answer_text}\n"
    
    text += "\nآیا پاسخ‌ها را تایید می‌کنید؟"
    
    keyboard = [
        [InlineKeyboardButton("✅ تایید و ادامه", callback_data="q_confirm")],
        [InlineKeyboardButton("✏️ ویرایش پاسخ‌ها", callback_data="q_edit_answers")],
        [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")]
    ]
    
    if query:
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def finalize_questionnaire(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Submit all answers and proceed to next step."""
    query = update.callback_query
    await query.answer()
    
    q_data = context.user_data.get('questionnaire', {})
    questions = q_data.get('questions', [])
    answers = q_data.get('answers', {})
    
    # Format answers for API
    formatted_answers = []
    for q in questions:
        q_id = q.get('id')
        answer = answers.get(q_id)
        if answer:
            answer_data = {"question_id": q_id}
            if isinstance(answer, list):
                answer_data["answer_values"] = answer
            elif answer.startswith("http"):
                answer_data["answer_file_url"] = answer
            else:
                answer_data["answer_text"] = answer
            formatted_answers.append(answer_data)
    
    # Store answers for order creation
    context.user_data['questionnaire_answers'] = formatted_answers
    
    # Clear questionnaire state
    context.user_data.pop('questionnaire', None)
    
    await query.message.edit_text(
        "✅ پرسشنامه با موفقیت ثبت شد!\n\n"
        "در حال پردازش سفارش...",
    )
    
    # Trigger next step in order flow
    # This should continue to attribute selection or order confirmation
    from handlers.dynamic_order import continue_after_questionnaire
    await continue_after_questionnaire(update, context)

