# import logging
# from django.db.models import get_model
# from edc.core.bhp_lock.classes import BaseLock
#
# logger = logging.getLogger(__name__)
#
#
# class NullHandler(logging.Handler):
#     def emit(self, record):
#         pass
# nullhandler = logger.addHandler(NullHandler())
#
#
# class SyncLock(BaseLock):
#
#     def __init__(self, db):
#         self.db = db
#         SyncLockModel = get_model('sync', 'SyncLockModel')
#         SyncImportHistoryModel = get_model('sync', 'SyncImportHistoryModel')
#         super(SyncLock, self).__init__(db, SyncLockModel, SyncImportHistoryModel)
