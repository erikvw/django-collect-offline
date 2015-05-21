from edc.device.sync.models import IncomingTransaction, OutgoingTransaction


def out_to_incoming(self):
    """ Sample code to take outgoing transactions from an external DB and save as incoming to the default DB. """
    instances = []
    for outgoing_transaction in OutgoingTransaction.objects.using('mpp40').filter(is_consumed=False).exclude(tx_name__icontains='bucket'):
        incoming_transaction = IncomingTransaction()
        for field in incoming_transaction._meta.fields:
            if field in outgoing_transaction._meta.fields:
                setattr(incoming_transaction, field.attname, getattr(outgoing_transaction, field.attname))
                instances.append(incoming_transaction)
                if incoming_transaction.tx:
                    incoming_transaction.save()
                    outgoing_transaction.is_consumed = True
                    outgoing_transaction.save()
