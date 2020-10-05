FROM python:3.8.6 as user
RUN pip install --upgrade pip
RUN pip install pytest
ARG HOST_UID=4000
ARG HOST_USER=nodummy
RUN useradd -ms /bin/bash ${HOST_USER} --create-home
WORKDIR /home/${HOST_USER}
RUN mkdir projects
COPY . projects/sql2gee
RUN cd projects/sql2gee && ls && make install


