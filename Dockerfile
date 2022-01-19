FROM python
COPY . /web
WORKDIR /web/api
RUN pip install -r ./requirements.txt
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
