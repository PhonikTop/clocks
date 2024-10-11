import os


def get_env_param_str(param_name, default_param_str=None, raise_exception=True):
    param_str = os.environ.get(param_name) or default_param_str
    if param_str is None and raise_exception:
        raise EnvironmentError(f"Incorrect env param: {param_name}")
    return param_str


def get_env_param_bool(param_name, default=None, required=True):
    param_str = os.environ.get(param_name) or default
    if param_str is None and required:
        raise EnvironmentError(f"Incorrect env param: {param_name}")

    if isinstance(param_str, str):
        param_str = param_str.lower()

    truthy_values = {
        "1": True,
        "true": True,
        True: True,
        1: True,
    }
    return truthy_values.get(param_str, False)
