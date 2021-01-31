from faker import Faker
from utils.exceptions import NotAllowed

fake_data_generator = Faker()

Faker.seed(0)

faker_functions = {
    "address": fake_data_generator.address,
    "country": fake_data_generator.country,
    "street": fake_data_generator.street_name,
    "color": fake_data_generator.color_name,
    "company": fake_data_generator.company,
    "currency": fake_data_generator.currency,
    "month": fake_data_generator.month_name,
    "time": fake_data_generator.time,
    "year": fake_data_generator.year,
    "date": fake_data_generator.date,
    "email": fake_data_generator.email,
    "url": fake_data_generator.url,
    "job": fake_data_generator.job,
    "text": fake_data_generator.text,
    "password": fake_data_generator.password,
    "name": fake_data_generator.name,
    "phone": fake_data_generator.phone_number,
}


def get_random_value(_key, _type):
    resp = None
    if _type == "boolean":
        resp = fake_data_generator.boolean()
    elif _type == "number":
        try:
            resp = float(fake_data_generator.__getattr__(_key)())
        except (AttributeError, ValueError):
            resp = fake_data_generator.random_int()
    elif _type == "string":
        try:
            resp = str(fake_data_generator.__getattr__(_key)())
        except (AttributeError, ValueError):
            resp = fake_data_generator.word()
    if resp is None:
        raise NotAllowed("Only value of type string, number or boolean is allowed")
    return resp
