"""Sales domain exceptions."""

from .sales_exceptions import (
    # Base exceptions
    SalesDomainError,
    
    # Customer exceptions
    CustomerError,
    CustomerNotFoundError,
    DuplicateCustomerError,
    InvalidCustomerStatusError,
    
    # Opportunity exceptions
    OpportunityError,
    OpportunityNotFoundError,
    InvalidOpportunityStageError,
    OpportunityAlreadyClosedError,
    InvalidOpportunityValueError,
    OpportunityOwnershipError,
    
    # Pipeline exceptions
    PipelineError,
    PipelineNotFoundError,
    InvalidPipelineStageError,
    DuplicatePipelineStageError,
    
    # Interaction exceptions
    InteractionError,
    InteractionNotFoundError,
    InvalidInteractionTypeError,
    InteractionPermissionError,
    
    # Money exceptions
    MoneyError,
    CurrencyMismatchError,
    InvalidCurrencyError,
    NegativeAmountError,
    
    # Contact exceptions
    ContactError,
    InvalidContactInfoError,
    MissingContactInfoError,
    
    # Business rule exceptions
    SalesBusinessRuleError,
    QuotaExceededError,
    ForecastAccuracyError,
    SalesProcessViolationError,
)

__all__ = [
    # Base exceptions
    "SalesDomainError",
    
    # Customer exceptions
    "CustomerError",
    "CustomerNotFoundError",
    "DuplicateCustomerError",
    "InvalidCustomerStatusError",
    
    # Opportunity exceptions
    "OpportunityError",
    "OpportunityNotFoundError",
    "InvalidOpportunityStageError",
    "OpportunityAlreadyClosedError",
    "InvalidOpportunityValueError",
    "OpportunityOwnershipError",
    
    # Pipeline exceptions
    "PipelineError",
    "PipelineNotFoundError",
    "InvalidPipelineStageError",
    "DuplicatePipelineStageError",
    
    # Interaction exceptions
    "InteractionError",
    "InteractionNotFoundError",
    "InvalidInteractionTypeError",
    "InteractionPermissionError",
    
    # Money exceptions
    "MoneyError",
    "CurrencyMismatchError",
    "InvalidCurrencyError",
    "NegativeAmountError",
    
    # Contact exceptions
    "ContactError",
    "InvalidContactInfoError",
    "MissingContactInfoError",
    
    # Business rule exceptions
    "SalesBusinessRuleError",
    "QuotaExceededError",
    "ForecastAccuracyError",
    "SalesProcessViolationError",
]