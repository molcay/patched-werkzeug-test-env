import logging
import timeit

import requests

from contextlib import contextmanager

form_submit_url = "http://localhost:{port}/form"

environments = [
    {
        'version': 'v2.2.3',
        'port': 5000,
    },
    {
        "version": 'v2.3.7',
        'port': 9007,
    },
    {
        "version": 'v2.3.8',
        'port': 9008,
    },
    {
        "version": 'v2.2.5 (patched)',
        'port': 8000,
    },
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname).1s] [%(process)d] - %(message)s",
    filename="logs/run_test.log",
    filemode='a'
)
logger = logging.getLogger()


@contextmanager
def timer(timer_name):
    start = timeit.default_timer()
    try:
        yield 
    finally:
        end = timeit.default_timer()
        logger.info('Function execution time "%s": %f', timer_name, end - start)


def execute(environment, filepath):
    logger.info('Executing the request for "%s" with the file "%s"...', environment.get('version'), filepath)
    url = form_submit_url.format(port=environment.get('port'))
    try:
        with timer('main'):
            logger.info('Reading the file: "%s"...', filepath)
            with open(filepath, "rb") as f:
                with timer('req'):
                    r = requests.post(url, files={'file': f}, verify=False)
    except FileNotFoundError:
        logger.error("The file was not found.")
    except requests.exceptions.RequestException as e:
        logger.exception("There was an exception that occurred while handling your request.", exc_info=e)
    finally:
        logger.info('Executed the request for "%s" with the file "%s"!', environment.get('version'), filepath)


def main():
    prefixes = ['na', 'cr', 'lf', 'crlf', 'lfcr']
    for prefix in prefixes[:]:
        for i in range(7, 9):
            filepath = f'test-files/{prefix}_10chars_{i}.txt'
            for environment in environments:
                for r in range(1, 11):
                    logger.info('Repeat #%d starting...', r)
                    execute(environment, filepath)
                    logger.info('Repeat #%d completed!', r)

if __name__ == '__main__':
    main()
