from rest_framework import generics

from .models import OutgoingTransaction, IncomingTransaction, MiddlemanTransaction
from .serializers import OutgoingTransactionSerializer, IncomingTransactionSerializer, MiddlemanTransactionSerializer


class OutgoingTransactionList(generics.ListCreateAPIView):
    queryset = OutgoingTransaction.objects.all()
    serializer_class = OutgoingTransactionSerializer


class OutgoingTransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = OutgoingTransaction.objects.all()
    serializer_class = OutgoingTransactionSerializer


class IncomingTransactionList(generics.ListCreateAPIView):
    queryset = IncomingTransaction.objects.all()
    serializer_class = IncomingTransactionSerializer


class IncomingTransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = IncomingTransaction.objects.all()
    serializer_class = IncomingTransactionSerializer


class MiddlemanTransactionList(generics.ListCreateAPIView):
    queryset = MiddlemanTransaction.objects.all()
    serializer_class = MiddlemanTransactionSerializer


class MiddlemanTransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MiddlemanTransaction.objects.all()
    serializer_class = MiddlemanTransactionSerializer
