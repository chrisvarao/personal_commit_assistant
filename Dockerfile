FROM alpine

RUN apk update && apk add --update git python3 python3-dev libffi-dev libressl-dev openssh-client build-base
RUN python3 -m ensurepip
RUN pip3 install 'pipenv>=8.3.0,<8.4.0'

COPY ["Pipfile.lock", "/tmp/"]

RUN pip3 --version

RUN cd /tmp \
    && pipenv install --ignore-pipfile --dev --system

WORKDIR /content

VOLUME /keys
VOLUME /content/assistant
VOLUME /content/scripts
VOLUME /content/tests

ENV PYTHONPATH "${PYTHONPATH}:/content"

RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
RUN eval "$(ssh-agent -s)"
RUN mkdir /content/repos

RUN git config --global user.email "test@example.com"
RUN git config --global user.name "Test Testerson"

ENTRYPOINT ["/content/tests/test_setup.sh"]