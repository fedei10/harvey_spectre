from pathlib import Path

import yaml


def load_prompt_template():
    path = Path(__file__).with_name("prompt_template.yaml")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


SYSTEM_PROMPT = load_prompt_template()["system_prompt"]
