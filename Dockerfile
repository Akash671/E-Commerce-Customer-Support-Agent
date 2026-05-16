# env. image
FROM python:3.11

# set working directory
WORKDIR /app

# copy requirements file
COPY requirements.txt .

# install dependencies

RUN pip install --no-cache-dir -r requirements.txt


# copy the rest of the application code

COPY . .


# expose port

EXPOSE 8000

# command to run the application

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
