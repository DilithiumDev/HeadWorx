from app.src.core.config.config import load_config
from app.src.core.config.schemas import ConfigurationSchema
# from src.core.builder import BuildAppContext
from os import getenv
from dotenv import load_dotenv
from prefect import flow, task

value_registry = {}
task_registry = {
    "say": say,
    "setvar": setvar,
    "getvar": getvar,
}

def main(config_path: str):
    config: ConfigurationSchema = load_config(config_path)

    print(f"Configuration: {config.project}")

    # TODO: Load services and dependencies.
    
    # ctx = BuildAppContext(config)

    # print(f"Context: {ctx}")
    mainflow()

@task
def say(msg: str) -> None:
    with open("out.txt", "a") as f:
        f.write(msg + "\n")

@task
def setvar(varname: str, value: any) -> None:
    global value_registry
    value_registry[varname] = value

@task
def getvar(varname: str) -> any:
    global value_registry
    return value_registry.get(varname)

@flow
def mainflow():
    say("Setting var1 to \"foo\".")
    setvar("var1", "foo")
    var1_value = getvar("var1")
    say(f"var1 = {var1_value}")

if __name__ == "__main__":
    load_dotenv()
    environment = getenv("ENVIRONMENT", "dev")
    config_path = f"conf/{environment}/config.yaml"

    main(config_path)
