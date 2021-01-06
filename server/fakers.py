from faker import Faker
from utils.exceptions import NotAllowed

fake_data_generator = Faker()

Faker.seed(0)

faker_functions = {
	'address': fake_data_generator.address,
	'country': fake_data_generator.country,
	'street': fake_data_generator.street_name,
	'color': fake_data_generator.color_name,
	'company': fake_data_generator.company,
	'currency': fake_data_generator.currency,
	'month': fake_data_generator.month_name,
	'time': fake_data_generator.time,
	'year': fake_data_generator.year,
	'date': fake_data_generator.date,
	'email': fake_data_generator.email,
	'url': fake_data_generator.url,
	'job': fake_data_generator.job,
	'text': fake_data_generator.text,
	'password': fake_data_generator.password,
	'name': fake_data_generator.name,
	'phone': fake_data_generator.phone_number
}

def get_random_value(_key, _type):
	if _type == 'boolean':
		return fake_data_generator.boolean()
	if _type == 'number':
		return fake_data_generator.random_int()
	if _type == 'string':
		if _key.lower() in faker_functions:
			return faker_functions[_key.lower()]()
		return fake_data_generator.word()
	raise NotAllowed('Only value of type string, number or boolean is allowed')