# How to use

### How to install python tools

With python3 installed, you will need to create a virtual environment to install all of the required packages. To do so please
run the following commands

```bash
    python -m venv .venv/
```

Once this is done please launch the virtual environment. You can refer to [https://docs.python.org/3/library/venv.html](this link) to learn how 
to launch one. You will then need to install the following libraries within the environment.

```bash
    pip install flask ply waitress
```

### How to setup the database

To create the database (or reset it) please run the python script entitled `init_db.py` within the virtual environement

```bash
    python init_db.py
```

### How to run

Again, within the virtual environment, launch the osiris app using the flask command line

```
    flask --app osiris --port 80 --debug
```

This will launch the webserver

