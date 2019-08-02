FROM alpine

RUN apk update && apk add --update git python3 openssh-client
RUN python3 -m ensurepip
RUN pip3 install 'pipenv>=8.3.0,<8.4.0'

COPY ["Pipfile.lock", "/tmp/"]

RUN pip3 --version

RUN cd /tmp \
    && pipenv install --ignore-pipfile --dev --system

WORKDIR /content

VOLUME /keygen
VOLUME /git/keys
VOLUME /git/repos
VOLUME /content/assistant
VOLUME /content/scripts

ENV PYTHONPATH "${PYTHONPATH}:/content"

RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
RUN eval "$(ssh-agent -s)"

CMD eval "$(ssh-agent -s)" && ssh-add /keygen/id_rsa && mkdir ~/.ssh && ssh-keyscan git > ~/.ssh/known_hosts && ssh git@git -p 22