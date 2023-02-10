FROM animcogn/face_recognition:cpu-latest

WORKDIR /app

EXPOSE 80

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]

