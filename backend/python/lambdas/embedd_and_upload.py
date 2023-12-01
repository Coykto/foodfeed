import json
import logging
import os
import datetime
import boto3
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info('Event: {}'.format(event))
    logger.info('Context: {}'.format(context))
