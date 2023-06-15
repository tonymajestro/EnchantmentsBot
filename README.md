# Enchantments Bot
This is a bot for finding available spots in the Enchantments zones of Alpine Lakes, WA.
This project is just for fun. Please do not use this bot for nefarious purposes.

## Bot Code
Most bot code can be found in the [lambda directory](https://github.com/tonymajestro/EnchantmentsBot/tree/main/lambda). It uses python3, [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) for making calls to AWS DynamoDB and AWS SNS, and [requests](https://pypi.org/project/requests/) for making requests to the enchantments API.

It also uses python's [unittest library](https://docs.python.org/3/library/unittest.html) for [unit tests](https://github.com/tonymajestro/EnchantmentsBot/tree/main/lambda/test).

## Infrastructure code
The AWS Lambda, DynamoDB tables, and SNS topics are created using Typescript and CDK. Resources can be found in the [lib directory](https://github.com/tonymajestro/EnchantmentsBot/blob/main/lib/v2-stack.ts).
