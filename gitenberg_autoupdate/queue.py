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


_sqs_deadletters = None
def queue_deadletters():
    global _sqs_deadletters
    if _sqs_deadletters is None:
        _sqs_deadletters = boto3.resource('sqs').get_queue_by_name(
            QueueName='gitberg-autoupdate-repositories-deadletter',
        )
    return _sqs_deadletters


def failed_messages():
    while True:
        resp = queue_deadletters().receive_messages(
            AttributeNames=['All'],
            MaxNumberOfMessages=10
        )
        if not resp:
            return
        for message in resp:
            yield message.body
            message.delete()


def fails():
    results = set()
    for fail in failed_messages():
        results.add(fail)
    return results


def queue_from_file(file_path):
    """Useful for resupmitting failed massages."""
    with open(file_path, 'r') as msgfile:
        for message in msgfile:
            queue_resource().send_message(MessageBody=message.strip())
