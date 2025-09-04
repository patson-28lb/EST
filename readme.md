## Project Setup
This guide provides the steps to install dependencies, set up the database, and run the FastAPI server and CLI for this project.

### Getting Started
1. Installation
To begin, install all the necessary dependencies from the requirements.txt file.
```
$ pip install -r requirements.txt
```

2. Database Setup
To create the local SQL database and populate it with initial dummy data, run the database.py script.
```
$ python database.py
```

3. Running the API Server
The main.py script is the FastAPI server. To run it, you need to use uvicorn.
To start the server, execute the following command:
```
$ uvicorn app.main:app --reload
```
4. Using the Command-Line Interface (CLI)
The CLI.py file provides a command-line interface for interacting with the application.
To see all available commands and their documentation, use the --help flag:
```
$ python CLI.py --help
```
