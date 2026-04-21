from sqlmodel import Session
from .model import Profile
from sqlmodel import select, col, asc, desc, func
from pydantic import BaseModel, Field
from typing import Literal


class PaginationParams(BaseModel):
    page: int = 1
    limit: int = Field(default=10, ge=10, le=50)


class FilterParams(PaginationParams):
    gender: str | None = None
    age_group: str | None = None
    country_id: str | None = None
    min_age: int | None = None
    max_age: int | None = None
    min_gender_probability: float | None = None
    min_country_probability: float | None = None
    order: Literal["asc", "desc"] = "asc"
    sort_by: Literal["age", "created_at", "gender_probability"] = "created_at"


class SearchParams(PaginationParams):
    query: str


class CustomHTTPException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


def filter_profiles(*, session: Session, filter_params: FilterParams) -> list[Profile]:

    statement = select(Profile)
    if filter_params.gender is not None:
        statement = statement.where(col(Profile.gender) == filter_params.gender.lower())
    if filter_params.country_id is not None:
        statement = statement.where(
            col(Profile.country_id) == filter_params.country_id.upper()
        )
    if filter_params.age_group is not None:
        statement = statement.where(
            col(Profile.age_group) == filter_params.age_group.lower()
        )
    if filter_params.min_age is not None:
        statement = statement.where(col(Profile.age) >= filter_params.min_age)
    if filter_params.max_age is not None:
        statement = statement.where(col(Profile.age) <= filter_params.max_age)
    if filter_params.min_gender_probability is not None:
        statement = statement.where(
            col(Profile.gender_probability) >= filter_params.min_gender_probability
        )
    if filter_params.min_country_probability is not None:
        statement = statement.where(
            col(Profile.country_probability) >= filter_params.min_country_probability
        )
    if filter_params.sort_by == "age":
        statement = statement.order_by(
            asc(col(Profile.age))
            if filter_params.order == "asc"
            else desc(col(Profile.age))
        )
    if filter_params.sort_by == "created_at":
        statement = statement.order_by(
            asc(col(Profile.created_at))
            if filter_params.order == "asc"
            else desc(col(Profile.created_at))
        )
    if filter_params.sort_by == "gender_probability":
        statement = statement.order_by(
            asc(col(Profile.gender_probability))
            if filter_params.order == "asc"
            else desc(col(Profile.gender_probability))
        )

    statement = statement.offset((filter_params.page - 1) * filter_params.limit).limit(
        filter_params.limit
    )
    total_count = session.exec(select(func.count()).select_from(Profile)).one()
    result = {
        "count": total_count,
        "data": session.exec(statement).all(),
    }

    return result
