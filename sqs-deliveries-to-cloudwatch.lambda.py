#!/usr/bin/env python3
#
#
# ferreira.mv
# 2018-12


import boto3
import json
import re
import datetime as dt
import time

sqs_batch = 10
sqs_queue = 'myorg-cloudtrail-deliveries-dl'
sqs_queue = 'myorg-cloudtrail-deliveries'

sqs     = boto3.client('sqs')
sqs_url = sqs.get_queue_url(QueueName=sqs_queue)['QueueUrl']

trail_region = re.compile('_CloudTrail_(\w*-\w*-\d?)_')

cw_namespace = 'CWTest'
cw = boto3.client('cloudwatch')


def sqs_get_loop():
    counter = 1
    while True:

        print('======================= {}'.format(counter))

        # this is a dict
        sqs_msg = sqs.receive_message( QueueUrl=sqs_url, MaxNumberOfMessages=sqs_batch )

        try:
            for s in sqs_msg['Messages']:

                receipt = s['ReceiptHandle']

                # s['Body'] is a str: make it a dict
                body = json.loads(s['Body'])

                message   = body['Message']
                tms_str   = body['Timestamp']
                timestamp = dt.datetime.strptime( tms_str[:-1], '%Y-%m-%dT%H:%M:%S.%f').timestamp()

                if message == 'CloudTrail validation message.':
                    print('Type: {}'.format(message) )
                    delivery_event = 1

                    print('Info: {}, Event: {}, Files: {}'.format(tms_str,1,0))
                    cw_put_metric_validations( timestamp, 1 )

                else:
                    print('Type: CloudTrail delivery message.')
                    delivery_event = 1

                    s3files = json.loads(message)['s3ObjectKey']
                    delivery_files = len( s3files )
                    print('Info: {}, Event: {}, Files: {}'.format(tms_str,delivery_event,delivery_files))


                    filename = s3files[0].split('/')[-1]
                    delivery_region = trail_region.search(filename).group(1)
                    cw_put_metric_deliveries( timestamp, delivery_region, delivery_files )

                    for f in s3files:
                        print( 'File: {}|{}'.format(delivery_region,f) )

                print('----------------------- ')
                res = sqs.delete_message(QueueUrl=sqs_url, ReceiptHandle=receipt)

        except:
            # No more messages
            if sqs_msg.get('ResponseMetadata'):
                break
            else:
                print('Exception: \n {}'.format( str(sqs_msg)[0:40] ))
                raise

        else:
            counter+=1
#           if counter >= 5: break


    print('END')

# end def

def cw_put_metric_validations( timestamp, qty_ev ):

    metric = [{
        'MetricName': 'Validations',
        'Dimensions': [ { 'Name': 'SNS', 'Value': 'validations' }, ],
        'Timestamp':  timestamp,
        'Value':      qty_ev,
        'Unit':       'Count'
    }]
    res  = cw.put_metric_data(Namespace=cw_namespace, MetricData=metric)
    code = res['ResponseMetadata']['HTTPStatusCode']
    print( '--- Metric: Validations: {}'.format(code) )


# end def

def cw_put_metric_deliveries( timestamp, region, qty_files ):

    metric = [{
        'MetricName': 'Deliveries',
        'Dimensions': [ { 'Name': 'Region', 'Value': region }, ],
        'Timestamp':  timestamp,
        'Value':      qty_files,
        'Unit':       'Count'
    }]
    res  = cw.put_metric_data(Namespace=cw_namespace, MetricData=metric)
    code = res['ResponseMetadata']['HTTPStatusCode']
#   print( '--- Metric: Deliveries: {}'.format(code) )

# end def


# Main
sqs_get_loop()


