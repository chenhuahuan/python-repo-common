
import shutil
import time
from datetime import datetime
import os
import json
import allure_commons
import pickle
from allure_commons.utils import now
from allure_commons.utils import md5
from allure_commons.utils import uuid4
from allure_commons.utils import represent
from allure_commons.logger import AllureFileLogger
from allure_commons.model2 import TestResult as allure_TestResult
from allure_commons.model2 import StatusDetails
from allure_commons.model2 import Parameter
from allure_commons.model2 import Label, Link
from allure_commons.model2 import Status
from allure_commons.reporter import AllureReporter
from allure_commons.types import LabelType

from attr import attrs, attrib
from attr import Factory

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return json.JSONEncoder.default(self, obj)
        except Exception:
            return str(obj)


class AllureTestResult(object):
    @attrs
    class TestSummaryResult(object):
        test_status = attrib(default=None)
        test_name = attrib(default=None)
        test_message = attrib(default=None)
        test_dict = attrib(default=Factory(dict))

    def __init__(self, sum_info_class=None):
        report_root_path = os.path.join(os.getcwd(), "reportsxxxx")
        report_dir_path = os.path.join(report_root_path, datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
        if not os.path.isdir(report_dir_path):
            os.makedirs(report_dir_path)
        for f in os.listdir(report_dir_path):
            f = os.path.join(report_dir_path, f)
            if os.path.isfile(f):
                os.unlink(f)
            elif os.path.isdir(f):
                shutil.rmtree(f)
        self.file_logger = AllureFileLogger(report_dir_path)
        allure_commons.plugin_manager.register(self.file_logger)
        self.allure_logger = AllureReporter()
        self.start_at = time.time()

        self.__sum_info_class = sum_info_class or self.TestSummaryResult

    def _clean_up(self):
        name = allure_commons.plugin_manager.get_name(self.file_logger)
        allure_commons.plugin_manager.unregister(name=name)


    @staticmethod
    def allure_status(status):
        return {'failed': Status.FAILED,
                'broken': Status.BROKEN,
                'passed': Status.PASSED,
                'skipped': Status.SKIPPED}.get(status)

    @staticmethod
    def _get_err_message(err):
        exctype, value, tb = err
        return str(exctype.__name__)

    def _add_result(self, test, trace=None):
        uuid = uuid4()

        test = self.__sum_info_class(**test)
        test_result = allure_TestResult(name=test.test_name, uuid=uuid)
        # test_result.status = self.allure_status(test.test_status)
        test_result.status = self.allure_status(test.test_status)

        test_result.fullName = test_result.name
        test_result.historyId = md5(test_result.fullName)

        test_result.statusDetails = StatusDetails(message=test.test_message, trace=trace)
        self.allure_logger.schedule_test(uuid, test_result)


        self.allure_logger.attach_data(uuid4(), 'aaa', name="request_result",
                                           attachment_type="text/plain", extension="txt")

        self.allure_logger.attach_data(uuid4(), json.dumps(test.test_dict, cls=ComplexEncoder, indent=4, sort_keys=True, ensure_ascii=False), name="case_dict",
                                       attachment_type="application/json", extension="json")


        self.allure_logger.close_test(uuid)




if __name__ == "__main__":

    test_sum_info = {
        "test_status": "passed",
        "test_name": "demo_test_name",
        "test_message": "test_message",
        "test_dict": {"info": 1234}
    }


    a =AllureTestResult.TestSummaryResult(**test_sum_info)
    print(a.test_status)
    print(a.test_dict)

    allure_result = AllureTestResult()
    allure_result._add_result(test_sum_info)