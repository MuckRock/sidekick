FROM python:3.7-slim

COPY symspell /code/symspell
# COPY Pipfile /code
# COPY Pipfile.lock /code


WORKDIR /code


# RUN apk add py3-numpy
# RUN pip install numpy

RUN apt-get update \
&& apt-get install gcc curl -y \
&& apt-get clean
RUN bash $HOME/.cargo/env


PATH="$HOME/.cargo/bin:$PATH" pip install ./symspell/bindings/Python

RUN pip install numpy scipy cython scikit-learn setuptools-rust

CMD sh

# RUN pip install pipenv
# RUN pipenv install


# WORKDIR /code
# ENV FLASK_APP=app.py
# ENV FLASK_RUN_HOST=0.0.0.0
# RUN apk add --no-cache gcc musl-dev linux-headers
# COPY requirements.txt requirements.txt
# RUN pip install -r requirements.txt
# EXPOSE 5000
# COPY . .
# CMD ["flask", "run"]
