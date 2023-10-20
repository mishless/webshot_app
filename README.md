# Webshot App
A python web app that takes screenshots of websites.

# How to run locally
1. Install poetry
```
python -m pip install poetry
```
2. Install dependencies
```
poetry install
```
3. Run app
```
poetry run uvicorn main:app --host 0.0.0.0 --port 80
```
# How to run with docker
1. Build docker image
```
docker build . -t webshot_app:latest
```
2. Run docker image as a container
```
docker run -d --name webshot_app_container -p 80:80 webshot_app:latest
```
3. Connect to docker container to check logs/db
```
docker exec -it webshot_app_container sh
```

# How to use
1. Healthcheck endpoint
```
http://localhost/isalive
```
2. Swagger docs
```
http://localhost/docs
```