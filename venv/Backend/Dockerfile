FROM python:3.9-slim

#set the working directory in the container

WORKDIR /app

#copy the dependencies file to the working directory

COPY requirements.txt .

#install any needed packages specified in requirements.txt 

RUN pip install --no-cashe-dir -r requirements.txt

#Copy the rest of the application code to the working directory 

COPY . .

#Make port 5001 available to the world outside this container

EXPOSE 5001

#define environment variable 

ENV FLASK_APP = app.py

#RUN app.py when the container launches

CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
