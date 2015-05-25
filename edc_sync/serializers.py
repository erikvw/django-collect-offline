from rest_framework.serializers import ModelSerializer

from .models import OutgoingTransaction, IncomingTransaction, MiddlemanTransaction


class OutgoingTransactionSerializer(ModelSerializer):
    class Meta:
        model = OutgoingTransaction
        fields = ('tx', 'tx_name', 'tx_pk', 'producer')


class IncomingTransactionSerializer(ModelSerializer):
    class Meta:
        model = IncomingTransaction
        fields = ('tx', 'tx_name', 'tx_pk', 'producer')


class MiddlemanTransactionSerializer(ModelSerializer):
    class Meta:
        model = MiddlemanTransaction
        fields = ('tx', 'tx_name', 'tx_pk', 'producer')


class Out2InTransactionSerializer(ModelSerializer):
 
    def save(self):
        incoming_transaction = IncomingTransaction
        pass
 
    class Meta:
        model = OutgoingTransaction
        fields = ('tx', 'tx_name', 'tx_pk', 'producer')
