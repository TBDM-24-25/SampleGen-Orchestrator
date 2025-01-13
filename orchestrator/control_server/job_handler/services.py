from datetime import date, datetime
from .models import EnviromentVariable
from jinja2 import Environment, FileSystemLoader
import os

def json_serial_date_time(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))

def render_job_instruction_message(operation,
                                   container_image_name,
                                   number_of_containers,
                                   container_cpu_limit,
                                   container_memory_limit,
                                   enviroment_variables,
                                   user,
                                   job_id,
                                   timestamp,
                                   job_description,
                                   computation_duration_in_seconds):
    # Refactor environment variable list to a dict so that it can be rendered into the job_instructions jinja2 template
    try:
        prepared_enviroment_variables = {}
        for enviroment_variable in enviroment_variables:
            prepared_enviroment_variables[enviroment_variable.variable_name] = enviroment_variable.variable_value
    except TypeError:
        prepared_enviroment_variables = {}

    # Load all the values into a context dict
    context = {
        "operation": operation,
        "container_image_name": container_image_name,
        "number_of_containers": number_of_containers,
        "resource_limits": {
            "cpu": container_cpu_limit,
            "memory": container_memory_limit
        },
        "environment_variables": prepared_enviroment_variables,
        "metadata": {
            "user": user,
            "job_id": job_id,
            "timestamp": timestamp,
            "description": job_description,
            "computation_duration_in_seconds": computation_duration_in_seconds,
        }
    }

    # Load the jinja2 template
    TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'message_templates')

    # Create a Jinja2 environment that loads templates from 'message_templates'
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    # Get your Jinja2 template file
    template = env.get_template('job_instructions.j2')
    rendered_message = template.render(context)

    return rendered_message