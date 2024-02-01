FROM python:3.12.1

# Set the working directory
WORKDIR /app

# Copy the requirements file in
COPY ./requirements.txt /app/requirements.txt

# Forward system SSH key to allow pip to install from private repos
RUN mkdir -p -m 0600 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts
RUN --mount=type=ssh pip install --no-cache-dir -r /app/requirements.txt 

# Copy the rest of the application code in
COPY ./app.env /app/app.env
COPY ./db.env /app/db.env
COPY ./src /app/src

# Use uvicorn to run the application
CMD ["uvicorn", "src.main:app"]