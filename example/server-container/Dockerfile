FROM python:3.9

COPY ./requirements.txt /requirements.txt
COPY ./inference.py /inference.py
COPY ./main.py /main.py

RUN pip install -r requirements.txt

EXPOSE 8080:8080

CMD ["python", "main.py"]

