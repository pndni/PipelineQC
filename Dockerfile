FROM centos:7.6.1810


RUN yum install -y epel-release && \
    yum install -y wget file bc tar gzip libquadmath which bzip2 libgomp tcsh perl less zlib zlib-devel hostname man-db && \
    yum groupinstall -y "Development Tools"

# python
RUN yum install -y python36 python36-pip python36-devel libstdc++-static
RUN pip3.6 install --upgrade pip==19.2.3

WORKDIR /root/PipelineQC
COPY PipelineQC PipelineQC
COPY doc doc
COPY setup.py .
COPY tests tests
RUN pip3.6 install .[doc]
WORKDIR /root/PipelineQC/doc
RUN make man
RUN cp _build/man/pipelineqc.1 /usr/share/man/man1/
WORKDIR /


ENV LC_ALL=en_US.utf-8

ENTRYPOINT ["PipelineQC"]