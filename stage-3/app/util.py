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


def filter_profiles(*, session: Session, filter_params: FilterParams) -> dict:

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


def filter_search_profiles(*, session: Session, search_params: SearchParams) -> dict:
    male = [
        "male",
        "males",
        "man",
        "men",
        "guy",
        "guys",
        "boy",
        "boys",
        "gentleman",
        "gentlemen",
    ]
    female = [
        "female",
        "females",
        "women",
        "woman",
        "lady",
        "ladies",
        "girl",
        "girlsgentlewomen",
    ]
    teenager = ["teen", "teenager", "teenagers", "teenage"]
    adult = ["adult", "adults", "adulthood"]
    old = ["old", "elder", "elderly", "senior", "seniors"]

    gender: list[str] = []
    age: int | None = None
    min_age: int | None = None
    max_age: int | None = None
    age_group: str | None = None
    country_name: str | None = None
    word_list = search_params.query.strip().lower().split()
    for index, word in enumerate(word_list):
        if word in male:
            gender.append("male")
        if word in female:
            gender.append("female")
        if word == "young":
            min_age = 16
            max_age = 24
        if word.isdigit():
            age = int(word)
        if word == "above":
            min_age = int(word_list[index + 1])
        if word == "below":
            max_age = int(word_list[index + 1])
        if word in teenager:
            age_group = "teenager"
        if word in adult:
            age_group = "adult"
        if word in old:
            age_group = "senior"
        if word == "from" or word == "in":
            country_name = word_list[index + 1]

    statement = select(Profile)
    if len(gender) == 1:
        statement = statement.where(col(Profile.gender) == gender[0])
    elif len(gender) > 1:
        statement = statement.where(col(Profile.gender).in_(gender))
    if min_age is not None:
        statement = statement.where(col(Profile.age) >= min_age)
    if max_age is not None:
        statement = statement.where(col(Profile.age) <= max_age)
    if age is not None and min_age is None and max_age is None:
        statement = statement.where(col(Profile.age) == age)
    if age_group is not None:
        statement = statement.where(col(Profile.age_group) == age_group)
    if country_name is not None:
        statement = statement.where(col(Profile.country_name).ilike(country_name))
    total_count = session.exec(select(func.count()).select_from(statement)).one()

    statement = statement.offset((search_params.page - 1) * search_params.limit).limit(
        search_params.limit
    )
    is_not_interpreted = (
        len(gender) == 0 and age is None and age_group is None and country_name is None
    )

    if is_not_interpreted and len(word_list) > 0:
        raise CustomHTTPException(status_code=400, message="Unable to interpret query")
    if len(session.exec(statement).all()) == 0:
        raise CustomHTTPException(status_code=404, message="No profiles found")
    result = {
        "count": total_count,
        "data": session.exec(statement).all(),
    }
    return result
