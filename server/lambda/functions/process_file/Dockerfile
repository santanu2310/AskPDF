FROM public.ecr.aws/lambda/python:3.13

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY lambda_function.py ./
COPY core/ ./core/

CMD [ "lambda_function.lambda_handler" ]
