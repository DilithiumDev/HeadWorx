from prefect import flow, task
import yaml
import re

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

# 1. Registry of available tasks
TASK_REGISTRY = {
    "say": say,
    "set_val": lambda value: value,
    "add": lambda a, b: a + b
}




@task
def run_node(task_name, **kwargs):
    # This task executes the registered function
    return TASK_REGISTRY[task_name](**kwargs)

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
        results[node_id] = run_node(task_name, **resolved_params)

    return results

# Usage
with open("workflow.yaml", "r") as f:
    config = yaml.safe_load(f)
    dynamic_flow(config)