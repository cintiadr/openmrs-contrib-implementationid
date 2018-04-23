FROM alpine:3.7

# Update
RUN apk add --update python py-pip py-mysqldb py-flask

# Bundle app source
COPY . /src/

EXPOSE  8000
CMD ["python", "/src/implementationid.py", "-p 8000"]
