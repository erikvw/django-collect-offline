from django.apps import apps as django_apps
from django.core.management.base import BaseCommand
from django_collect_offline_files.transaction import FileArchiver

from ...transaction import TransactionDeserializer, TransactionDeserializerError
from ...models import IncomingTransaction


class CustomTransactionDeserializer(TransactionDeserializer):

    file_archiver_cls = FileArchiver

    def __init__(self, order_by=None, model=None, batch=None, producer=None, **kwargs):
        super().__init__(**kwargs)
        """ Find how inherit parent properties.
        """
        filters = {}
        if model:
            filters.update(tx_name=model)
        if batch:
            filters.update(batch_id=batch)
        if producer:
            filters.update(producer=producer)
        if filters:
            try:
                transactions = IncomingTransaction.objects.filter(**filters).order_by(
                    *order_by.split(",")
                )
                self.deserialize_transactions(transactions=transactions)
            except TransactionDeserializerError as e:
                raise TransactionDeserializerError(e) from e
            else:
                app_config = django_apps.get_app_config("django_collect_offline")
                obj = self.file_archiver_cls(
                    src_path=app_config.pending_folder,
                    dst_path=app_config.archive_folder,
                )
                obj.archive(filename=f"{batch}.json")


class Command(BaseCommand):
    """Usage:
        python manage.py deserialize --batch=9835201711152020
            --model=label_lower --order_by=created,producer
    """

    help = "Deserializes transactions manually using " "different filter options."

    def add_arguments(self, parser):
        parser.add_argument(
            "--model",
            dest="model",
            default=None,
            help=("Specify the model name/tx name."),
        )

        parser.add_argument(
            "--batch", dest="batch", default=None, help=("Specify batch.")
        )

        parser.add_argument(
            "--order_by",
            dest="order_by",
            default="created",
            help=("Specify a field to order by e.g timestamp or created."),
        )

        parser.add_argument(
            "--producer",
            dest="producer",
            default=None,
            help=("Specify a producer/client machine. e.g bcpp010"),
        )

    def handle(self, *args, **options):
        CustomTransactionDeserializer(**options)
