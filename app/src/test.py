import inspect
import re
from typing import Any, get_args, get_origin, Union

import yaml

try:
    from prefect import flow, task
except ImportError:  # pragma: no cover - fallback for environments without prefect
    def flow(func=None, **_kwargs):
        if func is None:
            return lambda f: f
        return func

    def task(func=None, **_kwargs):
        if func is None:
            return lambda f: f
        return func


# Helper to identify references like "{ from: var_name }"
def resolve_string_templates(param_value, results):
    if not isinstance(param_value, str):
        return param_value

    # Regex to find { from: node_id }
    pattern = r"\{ from: (\w+) \}"

    def replacer(match):
        node_id = match.group(1)
        return str(results[node_id])

    return re.sub(pattern, replacer, param_value)


@task
def say(msg: str) -> None:
    with open("out.txt", "a") as f:
        f.write(msg + "\n")


def _normalize_expected_type(expected_type):
    if isinstance(expected_type, str):
        type_map = {
            "int": int,
            "str": str,
            "float": float,
            "bool": bool,
            "dict": dict,
            "list": list,
            "tuple": tuple,
        }
        return type_map.get(expected_type.lower(), expected_type)
    return expected_type


def _is_value_compatible(value, expected_type):
    expected_type = _normalize_expected_type(expected_type)
    if expected_type is None or expected_type is Any:
        return True
    if expected_type is inspect._empty:
        return True

    origin = get_origin(expected_type)
    if origin is Union:
        return any(_is_value_compatible(value, arg) for arg in get_args(expected_type))

    if origin in {list, dict, tuple}:
        return isinstance(value, origin)

    return isinstance(value, expected_type)


def validate_task_params(task_name, params, param_types=None, task_callable=None):
    if task_callable is None:
        task_entry = TASK_REGISTRY[task_name]
        if isinstance(task_entry, dict):
            task_callable = task_entry["task"]
            registry_param_types = task_entry.get("param_types", {})
        else:
            task_callable = task_entry
            registry_param_types = {}
    else:
        registry_param_types = {}

    if param_types is None:
        param_types = registry_param_types
    elif not param_types:
        param_types = registry_param_types

    if not param_types:
        signature = inspect.signature(task_callable)
        inferred_param_types = {}
        for parameter_name, parameter in signature.parameters.items():
            if parameter_name == "self":
                continue
            annotation = parameter.annotation
            if annotation is not inspect._empty:
                inferred_param_types[parameter_name] = annotation
        param_types = inferred_param_types

    for param_name, expected_type in param_types.items():
        if param_name not in params:
            continue
        value = params[param_name]
        if not _is_value_compatible(value, expected_type):
            raise TypeError(
                f"Task '{task_name}' parameter '{param_name}' expected {expected_type}, got {type(value).__name__}"
            )


# 1. Registry of available tasks
TASK_REGISTRY = {
    "say": {"task": say, "param_types": {"msg": str}},
    "set_val": {"task": lambda value: value, "param_types": {"value": int}},
    "add": {"task": lambda a, b: a + b, "param_types": {"a": int, "b": int}},
}


@task
def run_node(task_name, param_types=None, **kwargs):
    # This task executes the registered function
    task_entry = TASK_REGISTRY[task_name]
    if isinstance(task_entry, dict):
        task_callable = task_entry["task"]
        registry_param_types = task_entry.get("param_types", {})
    else:
        task_callable = task_entry
        registry_param_types = {}

    validate_task_params(
        task_name,
        kwargs,
        param_types=param_types or registry_param_types,
        task_callable=task_callable,
    )
    return task_callable(**kwargs)


@flow
def dynamic_flow(workflow_config):
    # Store results of tasks here to resolve dependencies
    results = {}

    for step in workflow_config["steps"]:
        node_id = step["id"]
        task_name = step["task"]

        # Resolve dependencies: check if a param is a reference
        resolved_params = {}
        for k, v in step["params"].items():
            if isinstance(v, dict) and "from" in v:
                resolved_params[k] = results[v["from"]]
            elif isinstance(v, str):
                resolved_params[k] = resolve_string_templates(v, results)
            else:
                resolved_params[k] = v

        # Execute the task
        results[node_id] = run_node(
            task_name,
            param_types=step.get("param_types"),
            **resolved_params,
        )

    return results


# Usage
# with open("workflow.yaml", "r") as f:
#     config = yaml.safe_load(f)
#     dynamic_flow(config)

if __name__ == "__main__":
    