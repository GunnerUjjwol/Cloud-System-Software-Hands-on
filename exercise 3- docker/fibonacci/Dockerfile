#FROM alpine:3.12
#ENV VAR 5
#COPY fibonacci.sh /usr/app/
#WORKDIR /usr/app
#CMD ./fibonacci.sh

#FROM alpine:3.12
#ENV VAR 5
#WORKDIR /usr/app
#COPY fibonacci.sh .
#CMD ./fibonacci.sh

FROM alpine:3.12
ENV VAR 5
WORKDIR /usr/app
COPY fibonacci.sh .
CMD ["./fibonacci.sh"]