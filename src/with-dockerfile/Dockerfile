ARG LANGUAGE_VERSION

FROM public.ecr.aws/lambda/python:${LANGUAGE_VERSION}

COPY . ./

RUN pip install .

CMD ["app.lambda_handler"]
