FROM python:3.7

WORKDIR /usr/src/slack-status-dashboard

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python","slack-status-dashboard.py"]

