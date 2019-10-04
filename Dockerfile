FROM centos:7.6.1810


RUN yum install -y epel-release && \
    yum install -y wget file bc tar gzip libquadmath which bzip2 libgomp tcsh perl less zlib zlib-devel hostname man-db && \
    yum groupinstall -y "Development Tools"

# python
RUN yum install -y python36 python36-pip python36-devel libstdc++-static
RUN pip3.6 install --upgrade pip==19.2.3
COPY docker_reqs.txt docker_reqs.txt
RUN pip3.6 install --requirement docker_reqs.txt && \
    pip3.6 install git+https://github.com/pndni/pndniworkflows.git@e2cd6965019e11c5670cee25573407a94c232a69

WORKDIR /root/PipelineQC
COPY PipelineQC PipelineQC
COPY doc doc
COPY setup.py .
COPY tests tests
RUN pip3.6 install --no-deps .
WORKDIR /root/PipelineQC/doc
RUN make man
RUN cp _build/man/pipelineqc.1 /usr/share/man/man1/
WORKDIR /


ENV LC_ALL=en_US.utf-8

LABEL org.opencontainers.image.title=PipelineQC \
      org.opencontainers.image.documentation=file:///usr/share/man/man1/pipelineqc.1 \
      org.opencontainers.image.vcs-url=https://github.com/pndni/PipelineQC

ENTRYPOINT ["PipelineQC"]