from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Union
import re


@dataclass(frozen=True)
class Money:
    """Money value object with currency support."""
    
    amount: Decimal
    currency: str = "USD"
    
    SUPPORTED_CURRENCIES = {
        "USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "SEK", "NOK", "DKK"
    }
    
    def __post_init__(self) -> None:
        """Validate money values after initialization."""
        if isinstance(self.amount, (int, float, str)):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        
        # After conversion above, self.amount is always a Decimal
        
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        
        if not self.currency:
            raise ValueError("Currency must be a non-empty string")
        
        currency_upper = self.currency.upper()
        if currency_upper not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {self.currency}")
        
        object.__setattr__(self, 'currency', currency_upper)
        
        # Round to 2 decimal places for most currencies, 0 for JPY
        precision = 0 if currency_upper == "JPY" else 2
        rounded_amount = self.amount.quantize(
            Decimal('0.01') if precision == 2 else Decimal('1'),
            rounding=ROUND_HALF_UP
        )
        object.__setattr__(self, 'amount', rounded_amount)
    
    def __str__(self) -> str:
        """String representation of money."""
        if self.currency == "JPY":
            return f"¥{self.amount:,.0f}"
        elif self.currency == "EUR":
            return f"€{self.amount:,.2f}"
        elif self.currency == "GBP":
            return f"£{self.amount:,.2f}"
        else:
            return f"${self.amount:,.2f}"
    
    def __add__(self, other: 'Money') -> 'Money':
        """Add two money objects (must have same currency)."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: 'Money') -> 'Money':
        """Subtract two money objects (must have same currency)."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {other.currency} from {self.currency}")
        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError("Subtraction would result in negative amount")
        return Money(result_amount, self.currency)
    
    def __mul__(self, factor: Union[int, float, Decimal]) -> 'Money':
        """Multiply money by a factor."""
        if factor < 0:
            raise ValueError("Cannot multiply by negative factor")
        return Money(self.amount * Decimal(str(factor)), self.currency)
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another Money object."""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __lt__(self, other: 'Money') -> bool:
        """Less than comparison (same currency only)."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare {self.currency} and {other.currency}")
        return self.amount < other.amount
    
    def __le__(self, other: 'Money') -> bool:
        """Less than or equal comparison."""
        return self == other or self < other
    
    def __gt__(self, other: 'Money') -> bool:
        """Greater than comparison."""
        return not self <= other
    
    def __ge__(self, other: 'Money') -> bool:
        """Greater than or equal comparison."""
        return not self < other
    
    @classmethod
    def zero(cls, currency: str = "USD") -> 'Money':
        """Create zero money amount."""
        return cls(Decimal('0'), currency)
    
    @classmethod
    def from_string(cls, money_str: str) -> 'Money':
        """Parse money from string like '$100.50' or '100.50 USD'."""
        money_str = money_str.strip()
        
        # Pattern for currency symbol at start
        symbol_pattern = r'^([€£¥$])([0-9,]+\.?[0-9]*)$'
        # Pattern for currency code at end
        code_pattern = r'^([0-9,]+\.?[0-9]*)\s+([A-Z]{3})$'
        # Pattern for just number
        number_pattern = r'^([0-9,]+\.?[0-9]*)$'
        
        symbol_match = re.match(symbol_pattern, money_str)
        if symbol_match:
            symbol, amount_str = symbol_match.groups()
            amount_str = amount_str.replace(',', '')
            currency_map = {'$': 'USD', '€': 'EUR', '£': 'GBP', '¥': 'JPY'}
            currency = currency_map.get(symbol, 'USD')
            return cls(Decimal(amount_str), currency)
        
        code_match = re.match(code_pattern, money_str)
        if code_match:
            amount_str, currency = code_match.groups()
            amount_str = amount_str.replace(',', '')
            return cls(Decimal(amount_str), currency)
        
        number_match = re.match(number_pattern, money_str)
        if number_match:
            amount_str = number_match.group(1).replace(',', '')
            return cls(Decimal(amount_str), 'USD')
        
        raise ValueError(f"Cannot parse money from string: {money_str}")
    
    def to_float(self) -> float:
        """Convert to float (use with caution for display only)."""
        return float(self.amount)
    
    def is_zero(self) -> bool:
        """Check if amount is zero."""
        return self.amount == Decimal('0')
    
    def percentage_of(self, total: 'Money') -> Decimal:
        """Calculate what percentage this amount is of the total."""
        if self.currency != total.currency:
            raise ValueError("Currencies must match")
        if total.is_zero():
            return Decimal('0')
        return (self.amount / total.amount * 100).quantize(Decimal('0.01'))