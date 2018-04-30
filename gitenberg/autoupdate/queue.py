import boto3

_sqs_queue = None
def queue_resource():
  """Returns the SQS queue to use for queuing book updates.

  This is lazily created when first being called."""

  global _sqs_queue
  if _sqs_queue is None:
    _sqs_queue = boto3.resource('sqs').get_queue_by_name(
        QueueName='gitberg-autoupdate-repositories',
        )
  return _sqs_queue
