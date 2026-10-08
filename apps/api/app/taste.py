"""Shared explicit taste contract for profiles and trip snapshots."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Interest = Literal["cafe", "nature", "photography", "food", "culture", "nightlife"]
INTERESTS = ("cafe", "nature", "photography", "food", "culture", "nightlife")


class TasteAnswers(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interests: list[Interest] = Field(min_length=1, max_length=6)
    pace: Literal["relaxed", "balanced", "active"]
    crowd: Literal["quiet", "neutral", "lively"]
    adventure: Literal["easy", "moderate", "challenging"]
    diet: Literal["unrestricted", "vegetarian", "vegan"]
    exclusions: list[Literal["trekking", "stairs", "alcohol"]] = Field(max_length=3)

    @field_validator("interests", "exclusions")
    @classmethod
    def unique_values(cls, values):
        if len(values) != len(set(values)):
            raise ValueError("Không chọn trùng một lựa chọn.")
        return sorted(values)


def taste_vector(answers: TasteAnswers) -> dict[str, float]:
    # Fixed bounds, no inference about unselected interests or hard constraints.
    return {key: 1.0 if key in answers.interests else 0.0 for key in INTERESTS}
