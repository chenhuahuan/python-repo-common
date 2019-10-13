import sys
import subprocess
import logging
import errno


logger = logging.getLogger(__name__)


def runproc(args, log_stdout=logging.DEBUG, log_stderr=True, **keywords):
    """!  Run a command and return the results

    @param args     Same as subprocess run parameter [https://docs.python.org/3/library/subprocess.html#subprocess.run]
    @param password If the command does an 'ssh-style' prompt for password, the given password will be used
    @param timeout  If not None the command will be killed after the given number of seconds if still running
    @param log_stdout Defaults to logging.DEBUG. Set to a logging Level described in Logging.py to log output to tester.log
                      Output will always be logged if logging.setLevel is lowered to logging.DEBUG.
    @param log_stderr Defaults to True. Set to False to avoid saving the
                      stderr to log.
    @param **keywords  Additional keywords are passed as-is to
                       subprocess.run [https://docs.python.org/3/library/subprocess.html#subprocess.Popen]

    @b NOTE the stderr=stdout=subprocess.PIPE is set by default.
    If you don't like this behavior call with stdout=None, stderr=None

    @return subprocess.CompletedProcess
    """
    if not log_stdout:
        log_stdout = logging.DEBUG

    assert logging.DEBUG <= log_stdout <= logging.CRITICAL, '`log_stdout` level must be in between DEBUG and CRITICAL'

    logger.log(logging.INFO, 'Running command: {!r}'.format(' '.join(args)))
    if 'stdout' not in keywords:
        keywords['stdout'] = subprocess.PIPE

    if 'stderr' not in keywords:
        keywords['stderr'] = subprocess.PIPE

    cmd = args.split(None,1)[0] if isinstance(args, str) else args[0]

    try:
        proc = subprocess.run(args, **keywords)
    except subprocess.SubprocessError as e:
        # Make sure we log the stdout, error
        if hasattr(e, 'stdout') and e.stdout and log_stdout:
            if not keywords.get('universal_newlines', False):
                output = e.stdout.decode(errors='replace')
            else:
                output = e.stdout

            for l in output.splitlines():
                logger.log(log_stdout, '<{}> {}'.format(cmd, l))

        if hasattr(e, 'stderr') and e.stderr and log_stderr:
            if not keywords.get('universal_newlines', False):
                errput = e.stderr.decode(errors='replace')
            else:
                errput = e.stderr

            for l in errput.splitlines():
                logger.error('<{}> {}'.format(cmd, l))
        # now re-raise
        raise
    except OSError as e:
        if e.errno == errno.ENOEXEC:
            logger.error('subprocess.run cannot execute the command\n{}'.format(args))
            logger.error('This is likely due to a problem with the executable format')
            logger.error('Most often, a script with no #! at the beginning can cause this error')
            logger.error("Try adding 'bash' or 'sh' as first arg to fix this problem")
        raise

    except:
        logger.error('subprocess.run has raised an unexpected error for command')
        logger.error(args)
        raise

    if proc.stdout and log_stdout:
        if not keywords.get('universal_newlines', False):
            output = proc.stdout.decode(errors='replace')
        else:
            output = proc.stdout

        for l in output.splitlines():
            logger.log(log_stdout, '<{}> {}'.format(cmd, l))

    if proc.stderr and log_stderr:
        if not keywords.get('universal_newlines', False):
            errput = proc.stderr.decode(errors='replace')
        else:
            errput = proc.stderr

        for l in errput.splitlines():
            logger.error('<{}> {}'.format(cmd, l))

    logger.log(log_stdout, '{!r} ReturnCode={}'.format(' '.join(args), proc.returncode))
    return proc


def runproc_check(args, log_stdout=logging.DEBUG, log_stderr=True, **keywords):
    try:
        proc = runproc(args, log_stdout=logging.DEBUG, log_stderr=True, **keywords)
        if proc.returncode != 0:
            logger.error(proc.stdout.decode())
            logger.error(proc.stderr.decode())
            sys.exit(-1)
    except Exception as e:
        logger.exception("Exception Captured:")
        sys.exit(-1)


if __name__ == "__main__":
    import LogHandlers
    logging.basicConfig(style='{', level=logging.DEBUG)
    LogHandlers.hook_logging()

    proc = runproc_check(['python3', 'LogHandlers.py'])