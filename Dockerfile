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
VOLUME /content/assistant
VOLUME /content/scripts

ENV PYTHONPATH "${PYTHONPATH}:/content"

RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
RUN eval "$(ssh-agent -s)"
RUN mkdir /repos

RUN git config --global user.email "test@example.com"
RUN git config --global user.name "Test Testerson"

CMD eval "$(ssh-agent -s)" && ssh-add /keygen/test1 && mkdir -p ~/.ssh && ssh-keyscan git > ~/.ssh/known_hosts && \
    ssh test1@git "init myrepo.git" && cd /repos && git clone ssh://test1@git/~/myrepo.git && cd myrepo && tail -f /dev/null