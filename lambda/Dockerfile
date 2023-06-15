# Use an official Python runtime as the base image
FROM public.ecr.aws/lambda/python:3.10

# Copy the requirements file into the container
COPY lambda/requirements.txt .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Create app directory
RUN mkdir "${LAMBDA_TASK_ROOT}"/app

# Copy config into app directory
COPY config/enchantments.yml .

# Copy the Lambda function code into app directory
COPY lambda/app/* "${LAMBDA_TASK_ROOT}"/app

# Set the command to run your Lambda function
CMD [ "app/lambda.handler" ] 
