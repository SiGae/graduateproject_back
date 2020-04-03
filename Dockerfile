FROM sigae/sigae_graduate_back:18.04
MAINTAINER sigae "sigae@protonmail.com"
RUN cd graduateproject_back
RUN app.py

EXPOSE 5000 5000