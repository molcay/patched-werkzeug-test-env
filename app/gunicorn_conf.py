import cProfile
import pstats
import io
import logging
import os
import time
from pathlib import Path


PORT = os.environ.get("PORT")
ENV_NAME = os.environ.get("ENV_NAME")
PROFILE_LIMIT = int(os.environ.get("PROFILE_LIMIT", 30))
PROFILER = bool(int(os.environ.get("PROFILER", 1)))


def profiler_enable(worker, req):
    worker.profile = cProfile.Profile()
    worker.profile.enable()
    worker.log.info("PROFILING %d: %s" % (worker.pid, req.uri))


def profiler_summary(worker, req, filename='no-name'):
    s = io.StringIO()
    worker.profile.disable()
    ps = pstats.Stats(worker.profile, stream=s)
    if req and req.path != "/form":
        return

    if req:
        request_full_path = '{}_{}_{}'.format(req.method, req.path, filename.replace(".", "_")).replace('/', '_')
    else:
        request_full_path = 'timeout_requests'

    profiler_folder = '/tmp/profiler/{}'.format(ENV_NAME)
    Path(profiler_folder).mkdir(parents=True, exist_ok=True)
    ps.dump_stats('{}/file_{}.{}.prof'.format(profiler_folder, request_full_path, worker.start_time))
    '''
    ps.sort_stats('time', 'cumulative')
    ps.print_stats(PROFILE_LIMIT)
    '''
    logging.info("\n[%d] [INFO] [%s] URI %s" % (worker.pid, req.method if req else 'NA', req.uri if req else 'NA'))
    logging.info("[%d] [INFO] %s" % (worker.pid, str(s.getvalue())))


def pre_request(worker, req):
    worker.start_time = time.time()
    if PROFILER is True:
        profiler_enable(worker, req)


def post_request(worker, req, environ, response):
    total_time = time.time() - worker.start_time
    logging.info("\n[%d] [INFO] [%s] Load Time: %.3fs\n" % (worker.pid, req.method, total_time))
    filename = 'unknown'
    if response.headers:
        for k, v in response.headers:
            if k == 'filename':
                filename = v
                break
    if PROFILER is True:
        profiler_summary(worker, req, filename)


def worker_abort(worker):
    logging.error(f"Worker {worker.pid} timed out. Request details (if available):")

    from werkzeug.local import LocalProxy
    if hasattr(worker, 'current_request') and isinstance(worker.current_request, LocalProxy):
        try:
            # This is speculative and might not work reliably for a hung worker
            req_method = worker.current_request.method
            req_path = worker.current_request.path
            logging.error(f"  Method: {req_method}, Path: {req_path}")
        except Exception as e:
            logging.error(f"  Could not retrieve request details: {e}")
    if PROFILER is True:
        req = getattr(worker, 'current_request', None)
        profiler_summary(worker, req, filename='no-filename-timeout')


bind = f"0.0.0.0:{PORT}"
workers = 1 # multiprocessing.cpu_count() * 2 + 1
timeout = 180 # 28800
# worker_connections = 1000
# logconfig = 'gunicorn_logging.conf'
# limit_request_field_size = 32768
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s context %({x-request-context}i)s'
