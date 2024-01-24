FROM public.ecr.aws/lambda/python:3.8

RUN yum install -y gcc python3-devel

COPY requirements.txt ./
RUN pip3 install -r ./requirements.txt
# Copy all files
COPY .codecarbon.config ./
COPY . .

CMD ["lambda_function.handler"]
