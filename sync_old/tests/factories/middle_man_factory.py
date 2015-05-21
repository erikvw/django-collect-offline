from ...models import MiddleManTransaction
from .base_transaction_factory import BaseTransactionFactory


class MiddleManTransactionFactory(BaseTransactionFactory):
    FACTORY_FOR = MiddleManTransaction
    
    is_consumed_middleman = False
    is_consumed_server = False