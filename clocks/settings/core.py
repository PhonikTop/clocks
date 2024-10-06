import os


def get_env_param_str(param_name, default_param_str=None, raise_exception=True):
    param_str = os.environ.get(param_name) or default_param_str
    if param_str is None and raise_exception:
        raise EnvironmentError(f"Incorrect env param: {param_name}")
    return param_str


def get_env_param_bool(param_name, default_param_bool=None, raise_exception=True):
    param_str = os.environ.get(param_name)

    if param_str is None:
        if default_param_bool is not None:
            return default_param_bool
        if raise_exception:
            raise EnvironmentError(f"Missing env param: {param_name}")
        return None

    param_str = param_str.lower()
    if param_str in ["true", "1", "yes"]:
        return True
    elif param_str in ["false", "0", "no"]:
        return False
    elif raise_exception:
        raise EnvironmentError(f"Incorrect boolean env param: {param_name}")

    return None
