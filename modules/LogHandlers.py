#!/usr/local/bin/python35
import os
import sys
import os.path as osp
import re
import time
import logging
import traceback

from fcntl import flock,LOCK_EX,LOCK_UN,LOCK_SH,LOCK_NB


ERROR_LOG='error.log'
ERRORS_LOG='errors.log'
TEST_LOG='test.log'
TESTER_LOG='tester.log'

DATE_TIME_FORMAT = '%y%m%d-%H:%M:%S'

EXC_LEVEL = 33
log_level_to_name = {logging.DEBUG    : 'DEBUG',
                     logging.INFO     : 'INFO ',
                     logging.WARNING  : 'WARN ',
                     EXC_LEVEL        : 'EXC**',
                     logging.ERROR    : 'ERROR ',
                     logging.CRITICAL : 'ERR** ',
}


class _FileLock:
    """ Lock a file
    """
    def __init__(self, fh):
        self.fh = fh

    def __enter__(self):
        flock(self.fh.fileno(), LOCK_EX)
        return self.fh

    def __exit__(self, etype, evalue, tb):
        flock(self.fh.fileno(), LOCK_UN)
        return False


def format_message(record):
    if record.args:
        if isinstance(record.args, dict):
            message = record.msg.format(record.args)
        else:
            message = record.msg.format(*record.args)
    else:
        message = record.msg

    if isinstance(message, (str, bytes)):
        return message
    else:
        return str(message)


class STDLogHandler(logging.Handler):
    def __init__(self, cwd, *bares, **keywords):
        super().__init__(*bares, **keywords)
        self.cwd = cwd

    def create_general_header(self, levelno, record):
        return '{} {:5s} {}'.format(
            time.strftime(DATE_TIME_FORMAT, time.localtime(record.created)),
            record.name,
            log_level_to_name[levelno])


    def emit(self, record):
        ''' Takes the logger record and does something with it

        In this case it will first print it to stdout if the level is below
        ERROR or stderr for ERROR and above.
        '''
        # This checks for level equal or above ERROR and prints to stderr,
        # stdout otherwise
        header = self.create_general_header(record.levelno, record)

        for line in format_message(record).splitlines():
            print(header, line, file=sys.stdout, flush=True)

        # This checks for exception, always print to stderr
        if record.exc_info:
            header = self.create_general_header(EXC_LEVEL, record)
            if isinstance(record.exc_info, list):
                lines = record.exc_info
            else:
                lines = "".join(traceback.format_exception(*record.exc_info)).splitlines()

            for line in lines:
                print(header, line, file=sys.stdout, flush=True)




class ErrorLogHandler(STDLogHandler):
    ''' Write to error.log and errors.log

    Writes the same thing to both.   It is up to the caller
    to erase the error.log between calls.
    '''
    def __init__(self, *bares, **kw):
        super().__init__(*bares, **kw)
        # Ensure that ERRORS_LOG remains first for full header output
        self.error_logs = [osp.join(self.cwd, ERRORS_LOG),
                           osp.join(self.cwd, ERROR_LOG)]

    def emit(self, record):
        if record.levelno < logging.ERROR:
            return

        # On the first pass, we will use a verbose header since we are
        ## writing to the raw error log
        for name in self.error_logs:
            header = self.create_general_header(record.levelno, record)
            with open(name, 'a') as fh:
                with _FileLock(fh):
                    fh.seek(0, 2) # goto end of file
                    for line in format_message(record).splitlines():
                        fh.write('{} {}\n'.format(header, line))

                    # This checks for exception, always print to stderr
                    if record.exc_info:
                        header = self.create_general_header(EXC_LEVEL, record)
                        if isinstance(record.exc_info, list):
                            lines = record.exc_info
                        else:
                            lines = "".join(traceback.format_exception(*record.exc_info)).splitlines()

                        for line in lines:
                            fh.write('{} {}\n'.format(header, line))
                    fh.flush()
            # After the first pass, switch to the sparse header


class TestLogHandler(STDLogHandler):
    ''' Write to test.log and tester.log

    Writes the same thing to both.   It is up to the caller
    to erase the test.log between calls.
    '''
    def __init__(self, *bares, **keywords):
        super().__init__(*bares, **keywords)
        # Ensure that RAWTEST_LOG remains first for full header output
        self.test_logs = [open(osp.join(self.cwd, TESTER_LOG), 'a'),
                          open(osp.join(self.cwd, TEST_LOG), 'a')]

    def emit(self, record):
        # On the first pass, we will use a verbose header since we are
        ## writing to the raw test log
        for fh in self.test_logs:
            header = self.create_general_header(record.levelno, record)
            with _FileLock(fh):
                fh.seek(0, 2) # goto end of file
                for line in format_message(record).splitlines():
                    fh.write('{} {}\n'.format(header, line))

                # This checks for exception, always print to stderr
                if record.exc_info:
                    header = self.create_general_header(EXC_LEVEL, record)
                    if isinstance(record.exc_info, list):
                        lines = record.exc_info
                    else:
                        lines = "".join(traceback.format_exception(*record.exc_info)).splitlines()

                    for line in lines:
                        fh.write('{} {}\n'.format(header, line))
                fh.flush()
            # After the first pass, switch to the sparse header


def hook_logging():
    _logger = logging.getLogger()

    # Need to remove any handlers that got auto-added
    for handler in list(_logger.handlers):
        _logger.removeHandler(handler)

    # Always add the STD loggers
    _logger.addHandler(STDLogHandler(cwd='.'))
    _logger.addHandler(ErrorLogHandler(cwd='.'))
    _logger.addHandler(TestLogHandler(cwd='.'))


if __name__ == "__main__":

    logging.basicConfig(style='{', level=logging.DEBUG)
    hook_logging()

    logger = logging.getLogger(__name__)

    logger.info('aaxxxxxxa')