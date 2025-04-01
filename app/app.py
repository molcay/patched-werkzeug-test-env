import logging
import os
import time

from importlib import metadata

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.utils import redirect
from werkzeug.formparser import parse_form_data

ENV_NAME = os.getenv('ENV_NAME')
PORT = int(os.getenv('PORT'))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname).1s] [%(process)d] - %(message)s"
)
logger = logging.getLogger(ENV_NAME)


def _get_packages():
    packages = []
    current_werkzeug = None
    for d in metadata.distributions():
        packages.append(d)
        if d.name.lower().startswith("werkzeug"):
            current_werkzeug = d
    
    return packages, current_werkzeug


packages, current_werkzeug = _get_packages()

DEFAULT_CONTEXT = {
    "name": current_werkzeug.name,
    "werkzeug_version": current_werkzeug.version,
    "packages": "\n".join([f"{p.name}=={p.version}" for p in packages]),
}

def application(environ, start_response):
    request = Request(environ)
    response = dispatch_request(request)
    return response(environ, start_response)

def dispatch_request(request):
    adapter = url_map.bind_to_environ(request.environ)
    try:
        endpoint, values = adapter.match()
        return getattr(views, f'on_{endpoint}')(request, **values)
    except HTTPException as e:
        return e

def render_template(template_name, **context):
    template_path = os.path.join(os.path.dirname(__file__), 'templates', template_name)
    with open(template_path, 'r') as f:
        template = f.read()
    
    current_context = {**DEFAULT_CONTEXT, **context}
    for key, value in current_context.items():
        template = template.replace(f'{{ {key} }}', str(value))
    return Response(template, mimetype='text/html')

class views:
    def on_index(request):
        logger.info(f"incoming request {request.path}!")
        return render_template('index.html')

    def on_form(request):
        logger.info(f"incoming request {request.path}!")
        try:
            start_time = time.process_time()
            _, _, files = parse_form_data(request.environ)
            end_time = time.process_time()
            elapsed_time_for_parse_form_data = end_time - start_time
            if 'file' in files:
                file_storage = files['file']
                # basic check to ensure file has a name
                if file_storage.filename:
                    # Very basic handling, for real app, save to a secure location, check file type, etc.
                    start_time = time.process_time()
                    file_storage.save(os.path.join(os.path.dirname(__file__), 'uploads', file_storage.filename))
                    end_time = time.process_time()
                    logger.info('File: "%s" parse_form_data() tooks %.4f, file_storage.save() tooks %.4f', file_storage.filename, elapsed_time_for_parse_form_data, end_time - start_time)
                    return render_template('form.html', message="File uploaded successfully.")
                else:
                    logger.warning('File: "%s" Failed!', file_storage.filename)
                    return render_template('form.html', message="File upload failed, no filename provided.")

            else:
                logger.warning('No File Provided!')
                return render_template('form.html', message="Form submitted successfully, but no file provided.")

        except Exception as e:
            logger.exception('Error processing the form!', exc_info=e)
            return render_template('form.html', message=f"Error processing form: {e}")


url_map = Map([
    Rule('/', endpoint='index'),
    Rule('/form', endpoint='form'),
])

# Ensure uploads directory exists
uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir, exist_ok=True) 

application = SharedDataMiddleware(application, {'/uploads': uploads_dir})


if __name__ == '__main__':
    from werkzeug.serving import run_simple

    logger.info(f"Environment is starting: {ENV_NAME} on the port :{PORT}")
    run_simple('0.0.0.0', PORT, application, use_debugger=True, use_reloader=True)
