FROM python:3.9


WORKDIR /app

COPY requirements.txt /app

RUN apt-get update && apt-get -y install python3-pip ffmpeg libsm6 libxext6 libfreetype6-dev git cargo rustc
RUN pip3 install --upgrade setuptools
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app
RUN git clone https://git@github.com/IDEA-Research/GroundingDINO
RUN pip install -r requirements.txt
RUN cd GroundingDINO && python setup.py develop
RUN mkdir weights 
WORKDIR /app/GroundingDINO/weights  
RUN wget -q https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth
WORKDIR /app
RUN mkdir images
RUN chmod +x app.py

CMD ["python3", "app.py"]