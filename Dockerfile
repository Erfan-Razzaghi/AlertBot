FROM docker.mofid.dev/python:3.12.2-slim-bullseye
WORKDIR /app
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
COPY ./src /app

# Debian adduser(8); this does not have a specific known uid
RUN adduser --system --no-create-home nonroot

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

USER nonroot

EXPOSE 8000

CMD ["python3", "main.py"]
