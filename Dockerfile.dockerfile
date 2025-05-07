FROM python:3.9-slim

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

EXPOSE 8000

CMD ["python", "app.py"]
