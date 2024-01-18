# base
#FROM registry.access.redhat.com/ubi8/python-39@sha256:cf0af1732c483d4e6ba708f9f4d5541cb43c98c3c67c604c23b0e55897eebe41
FROM registry.access.redhat.com/ubi8/python-311@sha256:0a00374f1044b037ff03c8d37542adfe749309dcf17d4b73a44823d049c853e0
# set working directory for image
WORKDIR /app

#install requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN python3 -m spacy download en_core_web_sm

# copy files from repo
COPY summarization/ /app


EXPOSE 4000

#start application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "4000"]
