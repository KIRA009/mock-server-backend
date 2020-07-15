# Mock Server backend
The backend for [Mock Server](https://github.com/KIRA009/mock-server), a lightweight web app that helps you to quickly design your application aspects, without having to worry about the data source

The client is hosted [here](https://github.com/KIRA009/mock-server-client/)
# Installation
- Ensure that you have python3 and pip installed
- Create a virtual environment and activate it
	```
	python3 -m venv /path/to/new/virtual/environment
	source /path/to/new/virtual/environment/bin/activate
	```
- Install the required packages
		`pip3 install -r requirements.txt`
- Run the migrations
	```
	python3 manage.py makemigrations
	python3 manage.py migrate
	```
- Start the server
	`python3 manage.py runserver`
# Contributing
When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change. 
Please note we have a code of conduct, please follow it in all your interactions with the project.
## Pull Request Process
1.  Ensure that the pr does not fail any tests
2. Write tests for any new user facing feature
3.  Update the README with details of changes to the interface, this includes new environment variables, changes in design patterns, etc.
# Contributors
- [Shohan](https://github.com/KIRA009/)
