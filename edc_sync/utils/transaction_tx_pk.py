from edc_sync.models import OutgoingTransaction


def previous_tx_pk_and_next_tx_pk(using='default'):

    first_unconsumed_outgoing = OutgoingTransaction.objects.using(using).filter(
        is_consumed_server=False).first()

    last_consumed_outgoing = OutgoingTransaction.objects.using(using).filter(
        is_consumed_server=True).last()

    previous_tx_pk = None
    if not last_consumed_outgoing:
        previous_tx_pk = first_unconsumed_outgoing.tx_pk
    else:
        previous_tx_pk = last_consumed_outgoing.current_tx_pk

    return (previous_tx_pk, first_unconsumed_outgoing.tx_pk)
