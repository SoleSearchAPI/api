FROM python:3.12.1

# Set the working directory
WORKDIR /app

# Copy your application code into the container
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app.env /app/app.env
COPY ./db.env /app/db.env
COPY ./src /app/src

# Use uvicorn to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]