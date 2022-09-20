#!/bin/bash

pip install --target ./package line-bot-sdk --upgrade
cd package
zip -r ../send_to_line_lambda.zip .
cd ..
zip -g send_to_line_lambda.zip lambda_function.py