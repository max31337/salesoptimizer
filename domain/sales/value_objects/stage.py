from dataclasses import dataclass
from enum import Enum

class StageType(Enum):
    """Sales pipeline stage types."""
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    WON = "won"
    LOST = "lost"


@dataclass(frozen=True)
class Stage:
    """Sales pipeline stage value object."""
    
    name: str
    stage_type: StageType
    order: int
    probability: int  # 0-100
    
    def __post_init__(self) -> None:
        """Validate stage values after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Stage name cannot be empty")
        
        object.__setattr__(self, 'name', self.name.strip())
        
        if self.order < 0:
            raise ValueError("order must be a non-negative integer")
        
        if not (0 <= self.probability <= 100):
            raise ValueError("probability must be an integer between 0 and 100")
        
        # Validate probability ranges for stage types
        if self.stage_type == StageType.WON and self.probability != 100:
            raise ValueError("Won stage must have 100% probability")
        
        if self.stage_type == StageType.LOST and self.probability != 0:
            raise ValueError("Lost stage must have 0% probability")
    
    def __str__(self) -> str:
        """String representation of stage."""
        return f"{self.name} ({self.probability}%)"
    
    def is_active(self) -> bool:
        """Check if stage is active (not won or lost)."""
        return self.stage_type not in {StageType.WON, StageType.LOST}
    
    def is_final(self) -> bool:
        """Check if stage is final (won or lost)."""
        return self.stage_type in {StageType.WON, StageType.LOST}
    
    def is_won(self) -> bool:
        """Check if stage represents a win."""
        return self.stage_type == StageType.WON
    
    def is_lost(self) -> bool:
        """Check if stage represents a loss."""
        return self.stage_type == StageType.LOST
    
    @classmethod
    def prospecting(cls, name: str = "Prospecting", order: int = 1) -> 'Stage':
        """Create prospecting stage."""
        return cls(name, StageType.PROSPECTING, order, 10)
    
    @classmethod
    def qualification(cls, name: str = "Qualification", order: int = 2) -> 'Stage':
        """Create qualification stage."""
        return cls(name, StageType.QUALIFICATION, order, 25)
    
    @classmethod
    def proposal(cls, name: str = "Proposal", order: int = 3) -> 'Stage':
        """Create proposal stage."""
        return cls(name, StageType.PROPOSAL, order, 50)
    
    @classmethod
    def negotiation(cls, name: str = "Negotiation", order: int = 4) -> 'Stage':
        """Create negotiation stage."""
        return cls(name, StageType.NEGOTIATION, order, 75)
    
    @classmethod
    def closing(cls, name: str = "Closing", order: int = 5) -> 'Stage':
        """Create closing stage."""
        return cls(name, StageType.CLOSING, order, 90)
    
    @classmethod
    def won(cls, name: str = "Won", order: int = 6) -> 'Stage':
        """Create won stage."""
        return cls(name, StageType.WON, order, 100)
    
    @classmethod
    def lost(cls, name: str = "Lost", order: int = 7) -> 'Stage':
        """Create lost stage."""
        return cls(name, StageType.LOST, order, 0)
    
    @classmethod
    def default_pipeline(cls) -> list['Stage']:
        """Create default sales pipeline stages."""
        return [
            cls.prospecting(),
            cls.qualification(),
            cls.proposal(),
            cls.negotiation(),
            cls.closing(),
            cls.won(),
            cls.lost(),
        ]