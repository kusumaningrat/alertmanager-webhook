# Start with the official Python base image (change version as needed)
FROM python:3.9-slim

# Set a working directory
WORKDIR /app

# Copy the requirements file into the image (if you have one)
COPY requirements.txt .

# Install any dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the image
COPY . .

EXPOSE 9119

# Specify the command to run your application (change "app.py" to your main script)
CMD ["python", "flaskAlert.py"]