# Use a Python base image
FROM python:3.12-slim

ARG ENV_NAME
ARG PORT

ENV ENV_NAME=${ENV_NAME}
ENV PORT=${PORT}

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY ${ENV_NAME}-requirements.txt ./requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./ .

# Expose the port the app runs on
EXPOSE ${PORT}

# Run the application
# CMD ["python", "app.py"]
CMD ["sh", "-c", "gunicorn app:application -c gunicorn_conf.py"]
