import httpx
from pprint import pprint


class CustomHTTPException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


def generate_profile(name: str):
    try:
        genderize_response = httpx.get(
            f"https://api.genderize.io?name={name}", timeout=10.0
        )
        genderize_data = genderize_response.json()
        if genderize_data["gender"] is None or genderize_data["count"] == 0:
            raise CustomHTTPException(
                status_code=502, message="Genderize returned an invalid response"
            )
        agify_response = httpx.get(f"https://api.agify.io?name={name}", timeout=10.0)
        agify_data = agify_response.json()
        if agify_data["age"] is None:
            raise CustomHTTPException(
                status_code=502, message="Agify returned an invalid response"
            )
        country_response = httpx.get(
            f"https://api.nationalize.io?name={name}",
            timeout=10.0,
        )
        country_data = country_response.json()
        if country_data["country"] is None:
            raise CustomHTTPException(
                status_code=502, message="Nationalize returned an invalid response"
            )

        pprint(country_data)
        pprint(genderize_data)
        pprint(agify_data)

        country_with_highest_probability = max(
            country_data["country"], key=lambda x: x["probability"]
        )

        return {
            "name": name,
            "gender": genderize_data["gender"],
            "gender_probability": genderize_data["probability"],
            "sample_size": genderize_data["count"],
            "age": agify_data["age"],
            "age_group": "child"
            if agify_data["age"] <= 12
            else "teenager"
            if agify_data["age"] <= 19
            else "adult"
            if agify_data["age"] <= 59
            else "elderly",
            "country_id": country_with_highest_probability["country_id"],
            "country_probability": round(
                country_with_highest_probability["probability"], 2
            ),
        }
    except httpx.RequestError as e:
        print.pprint(e.request.url)
        raise CustomHTTPException(status_code=502, message="Upstream or server failure")
