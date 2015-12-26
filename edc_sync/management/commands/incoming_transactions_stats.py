from django.db.models import Count
from django.core.management.base import BaseCommand
from edc.subject.lab_tracker.classes import site_lab_tracker
from ...models import IncomingTransaction

site_lab_tracker.autodiscover()


class Command(BaseCommand):

    args = ()
    help = 'Print uncomsumed incoming transactions breakdown by tx_name. '

    def handle(self, *args, **options):
        if not args:
            args = [None]
        stats = self.prepare_stats()
        self.print_stats(stats)

    def prepare_stats(self):
        # d35e5225bcb229a7f2957cc62c1e8070102fa66bd3353bece5ef9ec74c364adb
        return IncomingTransaction.objects.values('tx_name').filter(
            is_consumed=False, is_ignored=False
            ).annotate(
                tx_count=Count('tx_name')
                ).order_by('tx_name')

    def print_stats(self, stats):
        tot = IncomingTransaction.objects.filter(is_consumed=False, is_ignored=False).count()
        print "\nA summary of unconsumed incoming transactions"
        print "\n{0} Incoming transactions\n".format(tot)
        if stats:
            print "Total:\t:Transaction name"
            print "__________________________"

            for stat in stats:
                print "{0}\t:{1}".format(stat['tx_count'], stat['tx_name'])
            print "\t -------------------\t"
