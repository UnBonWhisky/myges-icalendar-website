FROM python:3.12

# Installation du fichier requirements.txt
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

CMD ["python3", "main.py"]