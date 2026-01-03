"""Service for managing questionnaires and validating answers."""

import re
from typing import Optional, List, Dict, Any
from uuid import UUID

from app.models.design_question import DesignQuestion, QuestionInputType
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import (
    ValidationRules,
    ValidateAnswerRequest,
    ValidateAnswerResponse,
    QuestionAnswerCreate,
)


class QuestionnaireService:
    """Service for questionnaire operations and answer validation."""
    
    def __init__(self, repository: CategoryRepository):
        self.repository = repository
    
    # ============== Section Management ==============
    
    async def get_sections_for_plan(self, plan_id: UUID) -> List[dict]:
        """Get all sections with their questions for a plan."""
        sections = await self.repository.get_sections_by_plan(plan_id)
        return [
            {
                "section": section,
                "questions": section.questions,
                "question_count": len(section.questions),
            }
            for section in sections
        ]
    
    async def get_all_questions_grouped(self, plan_id: UUID) -> Dict[str, List[DesignQuestion]]:
        """Get all questions grouped by section."""
        sections = await self.repository.get_sections_by_plan(plan_id)
        questions = await self.repository.get_questions_by_plan(plan_id)
        
        # Group questions
        grouped = {"unsectioned": []}
        for section in sections:
            grouped[str(section.id)] = []
        
        for q in questions:
            if q.section_id:
                key = str(q.section_id)
                if key in grouped:
                    grouped[key].append(q)
            else:
                grouped["unsectioned"].append(q)
        
        return grouped
    
    # ============== Conditional Logic ==============
    
    def should_show_question(
        self,
        question: DesignQuestion,
        answers: Dict[UUID, Any],
    ) -> bool:
        """
        Determine if a question should be shown based on conditional logic.
        
        Args:
            question: The question to evaluate
            answers: Dict of question_id -> answer for previous questions
            
        Returns:
            True if question should be shown
        """
        if not question.depends_on_question_id:
            return True
        
        # Get the answer for the dependent question
        dep_answer = answers.get(question.depends_on_question_id)
        if dep_answer is None:
            return False
        
        # Check if answer matches any of the required values
        depends_on_values = question.depends_on_values or []
        if not depends_on_values:
            # If no values specified, show if any answer exists
            return bool(dep_answer)
        
        # For text/single choice answers
        if isinstance(dep_answer, str):
            return dep_answer in depends_on_values
        
        # For multi-choice answers (list)
        if isinstance(dep_answer, list):
            return any(v in depends_on_values for v in dep_answer)
        
        return False
    
    def filter_visible_questions(
        self,
        questions: List[DesignQuestion],
        answers: Dict[UUID, Any],
    ) -> List[DesignQuestion]:
        """Filter questions to only include those that should be shown."""
        return [q for q in questions if self.should_show_question(q, answers)]
    
    # ============== Validation ==============
    
    def validate_answer(
        self,
        question: DesignQuestion,
        request: ValidateAnswerRequest,
    ) -> ValidateAnswerResponse:
        """
        Validate an answer for a question.
        
        Returns:
            ValidateAnswerResponse with is_valid and optional error_message
        """
        # Check if answer is provided for required questions
        has_answer = bool(
            request.answer_text or 
            request.answer_values or 
            request.answer_file_url
        )
        
        if question.is_required and not has_answer:
            return ValidateAnswerResponse(
                is_valid=False,
                error_message="این سوال اجباری است."
            )
        
        if not has_answer:
            return ValidateAnswerResponse(is_valid=True)
        
        # Get validation rules
        rules = question.validation_rules or {}
        if isinstance(rules, dict):
            rules = ValidationRules(**rules) if rules else ValidationRules()
        
        # Validate based on question type
        input_type = question.input_type
        
        if input_type == QuestionInputType.TEXT:
            return self._validate_text(request.answer_text, rules)
        
        elif input_type == QuestionInputType.TEXTAREA:
            return self._validate_text(request.answer_text, rules)
        
        elif input_type == QuestionInputType.NUMBER:
            return self._validate_number(request.answer_text, rules)
        
        elif input_type == QuestionInputType.SINGLE_CHOICE:
            return self._validate_single_choice(request.answer_text, question)
        
        elif input_type == QuestionInputType.MULTI_CHOICE:
            return self._validate_multi_choice(request.answer_values, question)
        
        elif input_type == QuestionInputType.IMAGE_UPLOAD:
            return self._validate_file(request.answer_file_url, rules, ["jpg", "jpeg", "png", "gif"])
        
        elif input_type == QuestionInputType.FILE_UPLOAD:
            return self._validate_file(request.answer_file_url, rules, None)
        
        elif input_type == QuestionInputType.COLOR_PICKER:
            return self._validate_color(request.answer_text)
        
        elif input_type == QuestionInputType.DATE_PICKER:
            return self._validate_date(request.answer_text)
        
        elif input_type == QuestionInputType.SCALE:
            return self._validate_scale(request.answer_text, rules)
        
        return ValidateAnswerResponse(is_valid=True)
    
    def _validate_text(
        self,
        value: Optional[str],
        rules: ValidationRules,
    ) -> ValidateAnswerResponse:
        """Validate text input."""
        if not value:
            return ValidateAnswerResponse(is_valid=True)
        
        # Check length constraints
        if rules.min_length and len(value) < rules.min_length:
            return ValidateAnswerResponse(
                is_valid=False,
                error_message=rules.error_message_fa or f"حداقل {rules.min_length} کاراکتر وارد کنید."
            )
        
        if rules.max_length and len(value) > rules.max_length:
            return ValidateAnswerResponse(
                is_valid=False,
                error_message=rules.error_message_fa or f"حداکثر {rules.max_length} کاراکتر مجاز است."
            )
        
        # Check regex pattern
        if rules.regex:
            try:
                if not re.match(rules.regex, value):
                    return ValidateAnswerResponse(
                        is_valid=False,
                        error_message=rules.error_message_fa or "فرمت ورودی نامعتبر است."
                    )
            except re.error:
                pass  # Invalid regex, skip validation
        
        return ValidateAnswerResponse(is_valid=True)
    
    def _validate_number(
        self,
        value: Optional[str],
        rules: ValidationRules,
    ) -> ValidateAnswerResponse:
        """Validate number input."""
        if not value:
            return ValidateAnswerResponse(is_valid=True)
        
        try:
            num_value = float(value.replace(',', ''))
        except ValueError:
            return ValidateAnswerResponse(
                is_valid=False,
                error_message="لطفا یک عدد معتبر وارد کنید."
            )
        
        if rules.min_value is not None and num_value < rules.min_value:
            return ValidateAnswerResponse(
                is_valid=False,
                error_message=rules.error_message_fa or f"حداقل مقدار مجاز {rules.min_value} است."
            )
        
        if rules.max_value is not None and num_value > rules.max_value:
            return ValidateAnswerResponse(
                is_valid=False,
                error_message=rules.error_message_fa or f"حداکثر مقدار مجاز {rules.max_value} است."
            )
        
        return ValidateAnswerResponse(is_valid=True)
    
    def _validate_single_choice(
        self,
        value: Optional[str],
        question: DesignQuestion,
    ) -> ValidateAnswerResponse:
        """Validate single choice selection."""
        if not value:
            return ValidateAnswerResponse(is_valid=True)
        
        # Check if value is one of the options
        valid_values = [opt.value for opt in question.options if opt.is_active]
        if value not in valid_values:
            return ValidateAnswerResponse(
                is_valid=False,
                error_message="گزینه انتخاب شده معتبر نیست."
            )
        
        return ValidateAnswerResponse(is_valid=True)
    
    def _validate_multi_choice(
        self,
        values: Optional[List[str]],
        question: DesignQuestion,
    ) -> ValidateAnswerResponse:
        """Validate multi choice selections."""
        if not values:
            return ValidateAnswerResponse(is_valid=True)
        
        valid_values = [opt.value for opt in question.options if opt.is_active]
        invalid = [v for v in values if v not in valid_values]
        
        if invalid:
            return ValidateAnswerResponse(
                is_valid=False,
                error_message="برخی گزینه‌های انتخاب شده معتبر نیستند."
            )
        
        return ValidateAnswerResponse(is_valid=True)
    
    def _validate_file(
        self,
        url: Optional[str],
        rules: ValidationRules,
        allowed_types: Optional[List[str]],
    ) -> ValidateAnswerResponse:
        """Validate file upload."""
        if not url:
            return ValidateAnswerResponse(is_valid=True)
        
        # Check file extension
        file_types = rules.allowed_types or allowed_types
        if file_types:
            ext = url.split('.')[-1].lower() if '.' in url else ''
            if ext not in [t.lower() for t in file_types]:
                return ValidateAnswerResponse(
                    is_valid=False,
                    error_message=f"فرمت فایل باید یکی از این‌ها باشد: {', '.join(file_types)}"
                )
        
        return ValidateAnswerResponse(is_valid=True)
    
    def _validate_color(self, value: Optional[str]) -> ValidateAnswerResponse:
        """Validate color input (HEX format)."""
        if not value:
            return ValidateAnswerResponse(is_valid=True)
        
        # Accept #RGB, #RRGGBB, or color names
        hex_pattern = r'^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$'
        if not re.match(hex_pattern, value):
            return ValidateAnswerResponse(
                is_valid=False,
                error_message="لطفا کد رنگ معتبر وارد کنید (مثلا #FF5733)"
            )
        
        return ValidateAnswerResponse(is_valid=True)
    
    def _validate_date(self, value: Optional[str]) -> ValidateAnswerResponse:
        """Validate date input."""
        if not value:
            return ValidateAnswerResponse(is_valid=True)
        
        # Accept common date formats
        import datetime
        date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y']
        
        for fmt in date_formats:
            try:
                datetime.datetime.strptime(value, fmt)
                return ValidateAnswerResponse(is_valid=True)
            except ValueError:
                continue
        
        return ValidateAnswerResponse(
            is_valid=False,
            error_message="لطفا تاریخ معتبر وارد کنید (مثلا 2024-01-15)"
        )
    
    def _validate_scale(
        self,
        value: Optional[str],
        rules: ValidationRules,
    ) -> ValidateAnswerResponse:
        """Validate scale input (1-5 or 1-10)."""
        if not value:
            return ValidateAnswerResponse(is_valid=True)
        
        try:
            num_value = int(value)
        except ValueError:
            return ValidateAnswerResponse(
                is_valid=False,
                error_message="لطفا یک عدد وارد کنید."
            )
        
        min_val = rules.min_value or 1
        max_val = rules.max_value or 5
        
        if num_value < min_val or num_value > max_val:
            return ValidateAnswerResponse(
                is_valid=False,
                error_message=f"مقدار باید بین {min_val} تا {max_val} باشد."
            )
        
        return ValidateAnswerResponse(is_valid=True)
    
    # ============== Answer Submission ==============
    
    async def validate_all_answers(
        self,
        plan_id: UUID,
        answers: List[QuestionAnswerCreate],
    ) -> Dict[UUID, ValidateAnswerResponse]:
        """
        Validate all answers for a questionnaire.
        
        Returns:
            Dict of question_id -> validation result
        """
        questions = await self.repository.get_questions_by_plan(plan_id)
        question_map = {q.id: q for q in questions}
        
        # Build current answers dict for conditional logic
        current_answers = {}
        for ans in answers:
            current_answers[ans.question_id] = (
                ans.answer_text or ans.answer_values or ans.answer_file_url
            )
        
        results = {}
        for q in questions:
            # Skip if question shouldn't be shown
            if not self.should_show_question(q, current_answers):
                continue
            
            # Find answer for this question
            answer = next((a for a in answers if a.question_id == q.id), None)
            
            if answer:
                request = ValidateAnswerRequest(
                    answer_text=answer.answer_text,
                    answer_values=answer.answer_values,
                    answer_file_url=answer.answer_file_url,
                )
            else:
                request = ValidateAnswerRequest()
            
            results[q.id] = self.validate_answer(q, request)
        
        return results
    
    async def submit_questionnaire(
        self,
        order_id: UUID,
        plan_id: UUID,
        answers: List[QuestionAnswerCreate],
    ) -> Dict[str, Any]:
        """
        Submit all answers for a questionnaire.
        
        Returns:
            Dict with success status and any validation errors
        """
        # Validate all answers
        validation_results = await self.validate_all_answers(plan_id, answers)
        
        # Check for errors
        errors = {
            str(q_id): result.error_message
            for q_id, result in validation_results.items()
            if not result.is_valid
        }
        
        if errors:
            return {
                "success": False,
                "errors": errors,
            }
        
        # Clear existing answers and submit new ones
        await self.repository.delete_answers_by_order(order_id)
        created_answers = await self.repository.submit_answers(order_id, answers)
        
        return {
            "success": True,
            "answer_count": len(created_answers),
        }
    
    # ============== Answer Summary ==============
    
    async def get_answers_summary(self, order_id: UUID) -> List[Dict[str, Any]]:
        """
        Get a summary of all answers for an order.
        
        Returns:
            List of dicts with question and answer info
        """
        answers = await self.repository.get_answers_by_order(order_id)
        
        summary = []
        for ans in answers:
            q = ans.question
            summary.append({
                "question_id": str(q.id),
                "question_fa": q.question_fa,
                "input_type": q.input_type.value,
                "answer_text": ans.answer_text,
                "answer_values": ans.answer_values,
                "answer_file_url": ans.answer_file_url,
                "display_answer": self._format_answer_display(ans, q),
            })
        
        return summary
    
    def _format_answer_display(self, answer, question: DesignQuestion) -> str:
        """Format answer for display to user or admin."""
        if answer.answer_text:
            # For single choice, show the label instead of value
            if question.input_type == QuestionInputType.SINGLE_CHOICE:
                for opt in question.options:
                    if opt.value == answer.answer_text:
                        return opt.label_fa
            return answer.answer_text
        
        if answer.answer_values:
            # For multi choice, show labels
            labels = []
            for val in answer.answer_values:
                for opt in question.options:
                    if opt.value == val:
                        labels.append(opt.label_fa)
                        break
                else:
                    labels.append(val)
            return "، ".join(labels)
        
        if answer.answer_file_url:
            return "[فایل ارسال شده]"
        
        return ""

