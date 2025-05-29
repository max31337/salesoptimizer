from dataclasses import dataclass
from typing import Optional
import re
from domain.organization.value_objects.email import Email


@dataclass(frozen=True)
class PhoneNumber:
    """Phone number value object with validation."""
    
    number: str
    country_code: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate phone number after initialization."""
        if not self.number:
            raise ValueError("Phone number cannot be empty")
        
        # Remove all non-digit characters for validation
        digits_only = re.sub(r'\D', '', self.number)
        
        if not digits_only:
            raise ValueError("Phone number must contain digits")
        
        if len(digits_only) < 7 or len(digits_only) > 15:
            raise ValueError("Phone number must be between 7 and 15 digits")
        
        # Normalize format
        if self.country_code:
            normalized = f"+{self.country_code} {self.number}"
        else:
            normalized = self.number
        
        object.__setattr__(self, 'number', normalized.strip())
    
    def __str__(self) -> str:
        """String representation of phone number."""
        return self.number
    
    @classmethod
    def from_string(cls, phone_str: str, country_code: Optional[str] = None) -> 'PhoneNumber':
        """Create phone number from string."""
        return cls(phone_str.strip(), country_code)
    
    def digits_only(self) -> str:
        """Get only the digits from the phone number."""
        return re.sub(r'\D', '', self.number)


@dataclass(frozen=True)
class ContactInfo:
    """Contact information value object."""
    
    email: Optional[Email] = None
    phone: Optional[PhoneNumber] = None
    linkedin_url: Optional[str] = None
    website: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate contact info after initialization."""
        if not any([self.email, self.phone, self.linkedin_url, self.website]):
            raise ValueError("At least one contact method must be provided")
        
        # Validate LinkedIn URL if provided
        if self.linkedin_url:
            linkedin_pattern = r'^https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9-]+/?$'
            if not re.match(linkedin_pattern, self.linkedin_url):
                raise ValueError("Invalid LinkedIn URL format")
        
        # Validate website URL if provided
        if self.website:
            website_pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
            if not re.match(website_pattern, self.website):
                raise ValueError("Invalid website URL format")
    
    def __str__(self) -> str:
        """String representation of contact info."""
        parts: list[str] = []
        if self.email:
            parts.append(f"Email: {self.email}")
        if self.phone:
            parts.append(f"Phone: {self.phone}")
        if self.linkedin_url:
            parts.append(f"LinkedIn: {self.linkedin_url}")
        if self.website:
            parts.append(f"Website: {self.website}")
        return " | ".join(parts)
    
    def has_email(self) -> bool:
        """Check if email is provided."""
        return self.email is not None
    
    def has_phone(self) -> bool:
        """Check if phone is provided."""
        return self.phone is not None
    
    def has_social_media(self) -> bool:
        """Check if any social media contact is provided."""
        return self.linkedin_url is not None
    
    def has_website(self) -> bool:
        """Check if website is provided."""
        return self.website is not None
    
    @classmethod
    def email_only(cls, email: str) -> 'ContactInfo':
        """Create contact info with email only."""
        return cls(email=Email.from_string(email))
    
    @classmethod
    def phone_only(cls, phone: str, country_code: Optional[str] = None) -> 'ContactInfo':
        """Create contact info with phone only."""
        return cls(phone=PhoneNumber.from_string(phone, country_code))
    
    @classmethod
    def email_and_phone(cls, email: str, phone: str, country_code: Optional[str] = None) -> 'ContactInfo':
        """Create contact info with email and phone."""
        return cls(
            email=Email.from_string(email),
            phone=PhoneNumber.from_string(phone, country_code)
        )