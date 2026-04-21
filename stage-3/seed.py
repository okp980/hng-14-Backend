from dependency import get_session
from model import Profile
import seed_data.json


def seed():
    with get_session() as session:
        for profile in seed_data:
            session.add(Profile(**profile))
        session.commit()


if __name__ == "__main__":
    seed()
