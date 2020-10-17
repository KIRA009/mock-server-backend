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

# Documentation
The api docs can be found in the <a href="https://github.com/KIRA009/mock-server-backend/wiki">wiki</a>
