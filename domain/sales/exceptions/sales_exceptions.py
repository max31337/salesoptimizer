"""Sales domain exceptions."""

from typing import Optional


class SalesDomainError(Exception):
    """Base exception for sales domain errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


# Customer-related exceptions
class CustomerError(SalesDomainError):
    """Base exception for customer-related errors."""
    pass


class CustomerNotFoundError(CustomerError):
    """Raised when customer is not found."""
    
    def __init__(self, identifier: str, identifier_type: str = "ID"):
        self.identifier = identifier
        self.identifier_type = identifier_type
        message = f"Customer with {identifier_type.lower()} '{identifier}' not found"
        super().__init__(message, "CUSTOMER_NOT_FOUND")


class DuplicateCustomerError(CustomerError):
    """Raised when trying to create customer with existing unique field."""
    
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        message = f"Customer with {field} '{value}' already exists"
        super().__init__(message, "DUPLICATE_CUSTOMER")


class InvalidCustomerStatusError(CustomerError):
    """Raised when invalid customer status operation is attempted."""
    
    def __init__(self, current_status: str, attempted_operation: str):
        self.current_status = current_status
        self.attempted_operation = attempted_operation
        message = f"Cannot {attempted_operation} customer with status '{current_status}'"
        super().__init__(message, "INVALID_CUSTOMER_STATUS")


# Opportunity-related exceptions
class OpportunityError(SalesDomainError):
    """Base exception for opportunity-related errors."""
    pass


class OpportunityNotFoundError(OpportunityError):
    """Raised when opportunity is not found."""
    
    def __init__(self, identifier: str, identifier_type: str = "ID"):
        self.identifier = identifier
        self.identifier_type = identifier_type
        message = f"Opportunity with {identifier_type.lower()} '{identifier}' not found"
        super().__init__(message, "OPPORTUNITY_NOT_FOUND")


class InvalidOpportunityStageError(OpportunityError):
    """Raised when invalid stage transition is attempted."""
    
    def __init__(self, from_stage: str, to_stage: str, reason: Optional[str] = None):
        self.from_stage = from_stage
        self.to_stage = to_stage
        self.reason = reason
        message = f"Cannot move opportunity from '{from_stage}' to '{to_stage}'"
        if reason:
            message += f": {reason}"
        super().__init__(message, "INVALID_STAGE_TRANSITION")


class OpportunityAlreadyClosedError(OpportunityError):
    """Raised when trying to modify closed opportunity."""
    
    def __init__(self, opportunity_id: str, stage: str):
        self.opportunity_id = opportunity_id
        self.stage = stage
        message = f"Cannot modify opportunity '{opportunity_id}' - already closed as '{stage}'"
        super().__init__(message, "OPPORTUNITY_ALREADY_CLOSED")


class InvalidOpportunityValueError(OpportunityError):
    """Raised when opportunity value is invalid."""
    
    def __init__(self, value: str, reason: str):
        self.value = value
        self.reason = reason
        message = f"Invalid opportunity value '{value}': {reason}"
        super().__init__(message, "INVALID_OPPORTUNITY_VALUE")


class OpportunityOwnershipError(OpportunityError):
    """Raised when user doesn't have ownership rights to opportunity."""
    
    def __init__(self, user_id: str, opportunity_id: str):
        self.user_id = user_id
        self.opportunity_id = opportunity_id
        message = f"User '{user_id}' does not have ownership rights to opportunity '{opportunity_id}'"
        super().__init__(message, "OPPORTUNITY_OWNERSHIP_ERROR")


# Pipeline-related exceptions
class PipelineError(SalesDomainError):
    """Base exception for pipeline-related errors."""
    pass


class PipelineNotFoundError(PipelineError):
    """Raised when pipeline is not found."""
    
    def __init__(self, identifier: str, identifier_type: str = "ID"):
        self.identifier = identifier
        self.identifier_type = identifier_type
        message = f"Pipeline with {identifier_type.lower()} '{identifier}' not found"
        super().__init__(message, "PIPELINE_NOT_FOUND")


class InvalidPipelineStageError(PipelineError):
    """Raised when invalid pipeline stage is used."""
    
    def __init__(self, stage_name: str, pipeline_id: str):
        self.stage_name = stage_name
        self.pipeline_id = pipeline_id
        message = f"Stage '{stage_name}' does not exist in pipeline '{pipeline_id}'"
        super().__init__(message, "INVALID_PIPELINE_STAGE")


class DuplicatePipelineStageError(PipelineError):
    """Raised when trying to add duplicate stage to pipeline."""
    
    def __init__(self, stage_name: str, pipeline_id: str):
        self.stage_name = stage_name
        self.pipeline_id = pipeline_id
        message = f"Stage '{stage_name}' already exists in pipeline '{pipeline_id}'"
        super().__init__(message, "DUPLICATE_PIPELINE_STAGE")


# Interaction-related exceptions
class InteractionError(SalesDomainError):
    """Base exception for interaction-related errors."""
    pass


class InteractionNotFoundError(InteractionError):
    """Raised when interaction is not found."""
    
    def __init__(self, identifier: str):
        self.identifier = identifier
        message = f"Interaction with ID '{identifier}' not found"
        super().__init__(message, "INTERACTION_NOT_FOUND")


class InvalidInteractionTypeError(InteractionError):
    """Raised when invalid interaction type is used."""
    
    def __init__(self, interaction_type: str):
        self.interaction_type = interaction_type
        message = f"Invalid interaction type: '{interaction_type}'"
        super().__init__(message, "INVALID_INTERACTION_TYPE")


class InteractionPermissionError(InteractionError):
    """Raised when user doesn't have permission to access interaction."""
    
    def __init__(self, user_id: str, interaction_id: str):
        self.user_id = user_id
        self.interaction_id = interaction_id
        message = f"User '{user_id}' does not have permission to access interaction '{interaction_id}'"
        super().__init__(message, "INTERACTION_PERMISSION_ERROR")


# Money and value-related exceptions
class MoneyError(SalesDomainError):
    """Base exception for money-related errors."""
    pass


class CurrencyMismatchError(MoneyError):
    """Raised when operations are attempted with different currencies."""
    
    def __init__(self, currency1: str, currency2: str, operation: str):
        self.currency1 = currency1
        self.currency2 = currency2
        self.operation = operation
        message = f"Cannot {operation} {currency1} and {currency2} - currencies must match"
        super().__init__(message, "CURRENCY_MISMATCH")


class InvalidCurrencyError(MoneyError):
    """Raised when invalid currency is used."""
    
    def __init__(self, currency: str):
        self.currency = currency
        message = f"Invalid or unsupported currency: '{currency}'"
        super().__init__(message, "INVALID_CURRENCY")


class NegativeAmountError(MoneyError):
    """Raised when negative amount is not allowed."""
    
    def __init__(self, amount: str, context: str = "operation"):
        self.amount = amount
        self.context = context
        message = f"Negative amount '{amount}' not allowed for {context}"
        super().__init__(message, "NEGATIVE_AMOUNT")


# Contact and communication exceptions
class ContactError(SalesDomainError):
    """Base exception for contact-related errors."""
    pass


class InvalidContactInfoError(ContactError):
    """Raised when contact information is invalid."""
    
    def __init__(self, field: str, value: str, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        message = f"Invalid {field} '{value}': {reason}"
        super().__init__(message, "INVALID_CONTACT_INFO")


class MissingContactInfoError(ContactError):
    """Raised when required contact information is missing."""
    
    def __init__(self, required_fields: list[str]):
        self.required_fields = required_fields
        fields_str = ", ".join(required_fields)
        message = f"Missing required contact information: {fields_str}"
        super().__init__(message, "MISSING_CONTACT_INFO")


# Business rule exceptions
class SalesBusinessRuleError(SalesDomainError):
    """Base exception for sales business rule violations."""
    pass


class QuotaExceededError(SalesBusinessRuleError):
    """Raised when sales quota is exceeded."""
    
    def __init__(self, user_id: str, quota_type: str, limit: str, current: str):
        self.user_id = user_id
        self.quota_type = quota_type
        self.limit = limit
        self.current = current
        message = f"User '{user_id}' has exceeded {quota_type} quota: {current}/{limit}"
        super().__init__(message, "QUOTA_EXCEEDED")


class ForecastAccuracyError(SalesBusinessRuleError):
    """Raised when forecast accuracy requirements are not met."""
    
    def __init__(self, user_id: str, accuracy: float, required_accuracy: float):
        self.user_id = user_id
        self.accuracy = accuracy
        self.required_accuracy = required_accuracy
        message = f"User '{user_id}' forecast accuracy {accuracy:.1%} below required {required_accuracy:.1%}"
        super().__init__(message, "FORECAST_ACCURACY_ERROR")


class SalesProcessViolationError(SalesBusinessRuleError):
    """Raised when sales process rules are violated."""
    
    def __init__(self, rule: str, context: str):
        self.rule = rule
        self.context = context
        message = f"Sales process violation: {rule} (Context: {context})"
        super().__init__(message, "SALES_PROCESS_VIOLATION")