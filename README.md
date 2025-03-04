# [Minesweeper](https://minesweeper-273296218879.europe-central2.run.app/)
A simple Minesweeper game website. Click the header to play!


## Try it locally:
- **Create a .env file** — you can copy and rename .env.sample to make it easier. HOST should be, most likely, localhost or 0.0.0.0, and PORT — 8000, 8080 or 80, whichever's available.

### With Docker
- **Build a container**: `docker build -t minesweeper`
- **Run the container** with colourful logging: `docker run -it -e "TERM=xterm-256color" -p PORT:PORT minesweeper` (don't forget to specify your desired port)
- **OR build and run** with `docker compose up --build`

### Without Docker (reliable on Python 3.11)
- **Create a virtual environment**: `python -m venv venv`
- **Install dependencies**: `pip install -r requirements.txt`
- **Run the app**: `python -m app.main`


## About the project
This project was a final task for CS50’s Introduction to Computer Science course. My main goal for the course was to catch up on CS basics that I have probably missed.

I have chosen this specific idea because I just love Minesweeper. :) However, I have always been intrigued by how to implement some algorithms for game mechanics — like calculating cell values, checking a cell with flood fill, and so on.

Also, this course is the first place I learnt about Python frameworks like Flask and FastAPI being able to integrate really easily with HTML templates. So I, as a person that only understands frontend development in theory, want to try a bit of that, too. And to deploy on a new for me platform, that is Google Cloud Run.

The languages, frameworks and tools I used are:
- Python via FastAPI with Uvicorn and Starlette WebSockets for backend
- HTML with JavaScript, CSS and Bootstrap framework for frontend
- Google Cloud Run for deployment
- Some Photoshop for drawing the game graphics

I think the project still requires some refactoring — I want the code to look better; and also, it lacks great mobile support that I haven't managed to implement.


## Main files in /app
### `/routers/main.py`
Handles the main page functionality — choosing a game mode.

### `/routers/game.py`
Handles the in-game functionality — accepts and processes user input from the frontend. Heavily utilises the FieldService (should be refactored to be less verbose)

### `/schemas/field.py`
Determines Pydantic schemas (custom data types) needed in the game, with their specific behaviour.
- `Cell` schema functions like a 2-sized tuple (immutable) that can be created from a Sequence (e.g. a tuple or a list) and also supports addition (mainly for finding neighbours)
- `CellCollection` schema is a `RootModel` that functions like a `defaultdict[list]` thanks to custom  `__getitem__` and `__setitem__`. Can also give all of the `Cell`s as a list. Used to collect and return information about affected cells' contents
- `GameResponse` wraps `CellCollection` to also provide a corresponding game status for the frontend

### `/services/field.py`
Implements the main functionality needed for the game. All functions have docstrings that explain them in detail.

The most interesting function, for me, is `flood_neighbouring_cells`. It implements a recursive flood-fill algorithm that was very interesting to work with. It utilises the mutable data types that are passed by reference. It checks every neighbouring cell of a starting one, takes note of what cells were visited already, and then checks their neighbours, too, and so on until it meets a non-empty cell or a cell that has been visited before. It turned out to be a very simple algorithm — but it was hard to wrap my head around it at first.

It was also engaging and sometimes baffling to work at a very abstract level of just.. a matrix of a field? It made debugging pretty hard. Once I was stuck at my fields not working in non-square fields for a very long time before realising I just mixed height and width in one of the calculations. Nevertheless, it was rewarding and stimulating to work at such a low (for me) level compared to the usual tasks I have at work.

### `/static/script_index.js`
Processes user input for choosing a game mode. Default modes don't require extra handling, but the custom option requires, first of all, the functionality for syncing values on range selectors (for easy and fast input) and number fields (for accurate, specific input) that was done via some basic event listeners.

Secondly, it requires validating mode input — it should be impossible to create a game with more mines than cells, and even better — there should be some adequate restraints for safe-to-mined cell proportions. I have read up on that and found out the ideal proportions are around 20% of mined cells, with 10% being the low boundary for an easy game and 30% — the high one for a hard game. At around 50% it becomes more of a guessing game and that's not ideal.

### `/templates`
Includes HTML templates.

### `main.py`
Puts everything together :)

[Video overview](https://youtu.be/YRXLj5Yc27M)
