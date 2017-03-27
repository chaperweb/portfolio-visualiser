from ubuntu:16.04
RUN apt-get update && apt-get install -y firefox xvfb python
RUN apt-get install -y python3 python3-pip 
RUN pip3 install virtualenv
RUN mkdir /app
RUN cd /app; virtualenv -p /usr/bin/python3 venv
COPY requirements.txt /app
COPY package.json /app
RUN cd /app; . venv/bin/activate; pip3 install --upgrade pip; pip3 install -r requirements.txt && nodeenv -p
RUN cd /app; . venv/bin/activate; npm install --only=dev
COPY portfolio_manager /app/portfolio_manager
COPY visualizer /app/visualizer
COPY manage.py /app
COPY docker/run_tests.sh /app
RUN chmod 755 /app/run_tests.sh
