from dataclasses import dataclass
import re
from typing import Dict, List
from enum import Enum


class PasswordStrength(Enum):
    """Password strength levels."""
    
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def description(self) -> str:
        """Get a human-readable description of the password strength."""
        descriptions = {
            self.WEAK: "Weak - Contains only basic characters",
            self.MEDIUM: "Medium - Contains letters and numbers",
            self.STRONG: "Strong - Contains letters, numbers, and symbols",
            self.VERY_STRONG: "Very Strong - Contains mixed case, numbers, symbols, and is long"
        }
        return descriptions[self]
    
    @property
    def minimum_score(self) -> int:
        """Get the minimum score required for this strength level."""
        scores = {
            self.WEAK: 0,
            self.MEDIUM: 3,
            self.STRONG: 5,
            self.VERY_STRONG: 7
        }
        return scores[self]


@dataclass(frozen=True)
class Password:
    """Password value object with validation and strength assessment."""
    
    value: str
    
    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Password cannot be empty")
        
        if len(self.value) < 8:
            raise ValueError("Password must be at least 8 characters long")
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def strength(self) -> PasswordStrength:
        """Calculate and return the password strength."""
        return self._calculate_strength()
    
    def _calculate_strength(self) -> PasswordStrength:
        """Calculate password strength based on various criteria."""
        score = 0
        
        # Length scoring
        if len(self.value) >= 8:
            score += 1
        if len(self.value) >= 12:
            score += 1
        if len(self.value) >= 16:
            score += 1
        
        # Character variety scoring
        if re.search(r'[a-z]', self.value):  # lowercase
            score += 1
        if re.search(r'[A-Z]', self.value):  # uppercase
            score += 1
        if re.search(r'\d', self.value):     # digits
            score += 1
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', self.value):  # special chars
            score += 1
        
        # Additional complexity checks
        if self._has_no_common_patterns():
            score += 1
        if self._has_good_entropy():
            score += 1
        
        # Determine strength based on score
        if score >= 7:
            return PasswordStrength.VERY_STRONG
        elif score >= 5:
            return PasswordStrength.STRONG
        elif score >= 3:
            return PasswordStrength.MEDIUM
        else:
            return PasswordStrength.WEAK
    
    def _has_no_common_patterns(self) -> bool:
        """Check if password avoids common weak patterns."""
        password_lower = self.value.lower()
        
        # Common weak patterns
        weak_patterns = [
            r'123', r'abc', r'qwerty', r'password', r'admin',
            r'000', r'111', r'999', r'aaa', r'zzz'
        ]
        
        for pattern in weak_patterns:
            if re.search(pattern, password_lower):
                return False
        
        # Check for repeated characters (more than 2 in a row)
        if re.search(r'(.)\1{2,}', self.value):
            return False
        
        return True
    
    def _has_good_entropy(self) -> bool:
        """Check if password has good character distribution."""
        # Check for character variety within the password
        char_types = 0
        
        if re.search(r'[a-z]', self.value):
            char_types += 1
        if re.search(r'[A-Z]', self.value):
            char_types += 1        
        if re.search(r'\d', self.value):
            char_types += 1
        if re.search(r'[^a-zA-Z\d]', self.value):
            char_types += 1
        
        # Good entropy requires at least 3 character types and length > 10
        return char_types >= 3 and len(self.value) > 10
    
    def get_strength_feedback(self) -> Dict[str, List[str]]:
        """Get detailed feedback about password strength."""
        suggestions: List[str] = []
        warnings: List[str] = []
        
        if len(self.value) < 12:
            suggestions.append("Use at least 12 characters for better security")
        
        if not re.search(r'[a-z]', self.value):
            suggestions.append("Add lowercase letters")
        
        if not re.search(r'[A-Z]', self.value):
            suggestions.append("Add uppercase letters")
        
        if not re.search(r'\d', self.value):
            suggestions.append("Add numbers")
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', self.value):
            suggestions.append("Add special characters (!@#$%^&*)")
        
        if not self._has_no_common_patterns():
            warnings.append("Avoid common patterns like '123', 'abc', or repeated characters")
        
        if re.search(r'(.)\1{2,}', self.value):
            warnings.append("Avoid repeating the same character multiple times")
        
        return {
            "suggestions": suggestions,
            "warnings": warnings
        }
