from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

from ..models import OutgoingTransaction, IncomingTransaction
from ..serializers import OutgoingTransactionSerializer, IncomingTransactionSerializer


@api_view(["GET"])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def api_root(request, format=None):
    return Response(
        {
            "outgoingtransaction": reverse(
                "outgoingtransaction-list", request=request, format=format
            ),
            "incomingtransaction": reverse(
                "outgoingtransaction-list", request=request, format=format
            ),
        }
    )


class OutgoingTransactionViewSet(viewsets.ModelViewSet):

    queryset = OutgoingTransaction.objects.all()
    serializer_class = OutgoingTransactionSerializer

    def filter_queryset(self, queryset):
        return self.queryset.filter(is_consumed_server=False).order_by("timestamp")


class IncomingTransactionViewSet(viewsets.ModelViewSet):

    queryset = IncomingTransaction.objects.all()
    serializer_class = IncomingTransactionSerializer

    def filter_queryset(self, queryset):
        return self.queryset.filter(is_consumed=False, is_ignored=False).order_by(
            "timestamp"
        )
