FROM python:3.7-slim

WORKDIR /code

# Install requirements with pip
RUN pip install flask scipy numpy flask-cors numba

# Copy files
COPY app.py /code/app.py
COPY lego_metric_learner.py /code/lego_metric_learner.py

CMD FLASK_ENV=development flask run --host=0.0.0.0
