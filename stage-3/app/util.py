from sqlmodel import Session
from .model import Profile
from .routers.profiles import FilterParams
from sqlmodel import select, col


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
    if filter_params.order is not None:
        statement = statement.order_by(
            col(filter_params.sort_by) * (1 if filter_params.order == "asc" else -1)
        )
    return session.exec(statement).all()
