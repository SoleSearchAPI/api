# Use a minimal Linux-based image as the base
FROM alpine:latest

# Set environment variables for Pyenv
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PATH"

# Install dependencies
RUN apk update && \
    apk add --no-cache \
    curl \
    git \
    bash \
    build-base \
    zlib-dev \
    bzip2-dev \
    readline-dev \
    sqlite-dev \
    openssl-dev \
    libffi-dev \
    && rm -rf /var/cache/apk/*

# Install pyenv
RUN curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | sh

# Install Python 3.12.1 and set it as the global version
RUN pyenv install 3.12.1 && \
    pyenv global 3.12.1

# Install Pipenv
RUN pip install --no-cache-dir pipenv
RUN pipenv install

# Set the working directory
WORKDIR /app

# Copy your application code into the container
COPY . /app

# Define the entry point for your application, e.g., 'pipenv run your_script.py'
CMD ["pipenv", "run", "your_script.py"]