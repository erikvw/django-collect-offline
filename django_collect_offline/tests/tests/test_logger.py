# import logging
# import os
# import tempfile
#
# from django.test.testcases import TestCase
# from django_collect_offline_files.action_handler import ActionHandler, ActionHandlerError
#
# logger = logging.getLogger('django_collect_offline')
#
#
# class TestLogger(TestCase):
#
#     def setUp(self):
#         self.src_path = os.path.join(tempfile.gettempdir(), 'src')
#         if not os.path.exists(self.src_path):
#             os.mkdir(self.src_path)
#         self.dst_path = os.path.join(tempfile.gettempdir(), 'dst')
#         if not os.path.exists(self.dst_path):
#             os.mkdir(self.dst_path)
#         self.archive_path = os.path.join(tempfile.gettempdir(), 'archive')
#         if not os.path.exists(self.archive_path):
#             os.mkdir(self.archive_path)
#
#     def test_action_logging(self):
#         """Asserts an invalid action is logged.
#         """
#         kwargs = dict(
#             using='client',
#             src_path=self.src_path,
#             dst_path=self.dst_path,
#             archive_path=self.archive_path,
#             remote_host='localhost')
#
#         action = 'BLAH'
#
#         action_handler = ActionHandler(**kwargs)
#
#         with self.assertLogs(logger, logging.ERROR) as cm:
#             try:
#                 action_handler.action(label=action)
#             except ActionHandlerError as e:
#                 logger.warn(e)
#                 logger.exception(e)
#         self.assertIn('BLAH', ' '.join(cm.output))
