# GIC image downloader

## Local usage
To run the server, please execute the following from the root directory:

```
python3 -m venv ./.venv
pip3 install -r requirements.txt
uvicorn app.main:app --port 8080 --reload
```
### Interactive API docs
Now go to http://127.0.0.1:8000/docs.

You will see the automatic interactive API documentation (provided by Swagger UI).

### Alternative API docs
And now, go to http://127.0.0.1:8000/redoc.

You will see the alternative automatic documentation (provided by ReDoc).

## Running with Docker

To run the server on a Docker container, please execute the following from the root directory:

```bash
# building the image
docker build -t api .

# starting up a container
docker run -p 8000:8000 api
```