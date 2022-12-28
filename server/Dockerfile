FROM python:3
WORKDIR /usr/src/app
RUN apt-get update && apt-get upgrade -y && pip3 install --upgrade pip
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]