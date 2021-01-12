FROM python:alpine3.8

COPY . /python_code
WORKDIR /python_code
RUN pip install -r requirements.txt

CMD ["python", "main.py"]