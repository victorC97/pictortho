FROM python:3.8-slim

COPY . /src/app
WORKDIR /src/app
RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]