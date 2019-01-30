import socket

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import OutgoingTransaction, IncomingTransaction


class TransactionCountView(APIView):
    """
    A view that returns the count  of transactions.
    """

    renderer_classes = (JSONRenderer,)

    def get(self, request):
        outgoingtransaction_count = OutgoingTransaction.objects.filter(
            is_consumed_server=False
        ).count()
        outgoingtransaction_middleman_count = OutgoingTransaction.objects.filter(
            is_consumed_server=False, is_consumed_middleman=False
        ).count()
        incomingtransaction_count = IncomingTransaction.objects.filter(
            is_consumed=False, is_ignored=False
        ).count()
        content = {
            "outgoingtransaction_count": outgoingtransaction_count,
            "outgoingtransaction_middleman_count": outgoingtransaction_middleman_count,
            "incomingtransaction_count": incomingtransaction_count,
            "hostname": socket.gethostname(),
        }
        return Response(content, status=status.HTTP_200_OK)
