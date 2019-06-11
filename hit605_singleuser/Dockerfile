FROM nvidia/cuda
LABEL maintainer="Lin Xiaotian <sky.linxiaotian@gmail.com>"

ENV SHELL /bin/bash
ENV JUPYTER_ENABLE_LAB true

COPY --chown=root:root ./files_to_copy/bin /usr/local/bin

RUN sed -i 's/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    mkdir /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf  && \
    echo "trusted-host=pypi.tuna.tsinghua.edu.cn" >> /root/.pip/pip.conf && \
    echo "index-url=https://pypi.tuna.tsinghua.edu.cn/simple/" >> /root/.pip/pip.conf

RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y install wget git vim sudo bash-completion build-essential&& \
    apt-get -y install python3 python3-dev python3-pip && \
    apt-get -y install nodejs nodejs-dev npm && \
    apt-get purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install jupyter && \
    pip3 install jupyterlab && \
    pip3 install jupyterhub && \
    jupyter labextension install @jupyterlab/hub-extension

# Add Tini
ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "-g", "--"]

RUN echo "root:1" | chpasswd && useradd -ms /bin/bash -G sudo,adm hit605 && echo "hit605:1" | chpasswd
USER hit605
RUN mkdir -p /home/hit605/.pip && \
    echo "[global]" > /home/hit605/.pip/pip.conf  && \
    echo "trusted-host=pypi.tuna.tsinghua.edu.cn" >> /home/hit605/.pip/pip.conf && \
    echo "index-url=https://pypi.tuna.tsinghua.edu.cn/simple/" >> /home/hit605/.pip/pip.conf
WORKDIR /home/hit605

CMD ["start-notebook.sh"]
