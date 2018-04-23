FROM alpine:3.7
EXPOSE  8000

RUN apk add --update python py-pip py-mysqldb py-flask py-bcrypt py-paramiko py-six py-cffi curl

# Bundle app source
COPY . /src/

CMD ["python", "/src/implementationid.py", "-p 8000"]
