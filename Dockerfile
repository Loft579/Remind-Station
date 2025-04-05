FROM python:3.8

# Install tesseract
#RUN apt install tesseract-ocr -y

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements.txt file into the container
COPY requirements.txt /app/

# Install the dependencies
RUN python3 -m pip install -r requirements.txt

# Copy the rest of your application code
COPY . /app

# Command to run the application
CMD ["python3", "app.py", "--env-file", ".env"]