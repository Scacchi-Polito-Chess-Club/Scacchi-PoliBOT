"""Tournament models."""

from pydantic import BaseModel, Field
from typing import Literal, Dict, Any


class TournamentType(BaseModel):
    """Tournament configuration model."""

    name: str = Field(description="Display name (e.g., '1+0 Bullet')")
    cmd: str = Field(description="Telegram command (e.g., '/bullet')")
    time: int = Field(ge=1, description="Clock time in minutes")
    increment: int = Field(ge=0, description="Clock increment in seconds")
    variant: Literal["standard", "chess960", "antichess", "fromPosition"] = Field(
        description="Chess variant"
    )
    full_name: str = Field(description="Full tournament name on Lichess")


class TournamentPayload(BaseModel):
    """Payload for Lichess tournament creation API."""

    name: str
    clock_time: int = Field(ge=1, le=180)
    clock_increment: int = Field(ge=0, le=180)
    variant: str
    minutes: int = Field(ge=30, le=3600)
    team_id: str
    start_date: int = Field(description="Start time in milliseconds")

    model_config = {"populate_by_name": True}

    def to_lichess_payload(self) -> Dict[str, Any]:
        """Convert to Lichess API format."""
        return {
            "name": self.name,
            "clockTime": self.clock_time,
            "clockIncrement": self.clock_increment,
            "variant": self.variant,
            "minutes": self.minutes,
            "conditions.teamMember.teamId": self.team_id,
            "startDate": self.start_date,
        }
