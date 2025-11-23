from taskgraph.transforms.base import TransformSequence

transforms = TransformSequence()


@transforms.add
def add_fuzz_dependencies(config, tasks):
    """Add dependencies on both fuzz variants for each apworld/version."""
    for task in tasks:
        apworld_name = task["attributes"]["apworld_name"]
        version = task["attributes"]["version"]

        default_fuzz = f"fuzz-{apworld_name}-{version}"
        no_restrictive_fuzz = f"fuzz-no-restrictive-starts-{apworld_name}-{version}"

        yield {
            "label": task["label"],
            "description": task["description"],
            "attributes": task["attributes"],
            "worker-type": task["worker-type"],
            "run-on-tasks-for": task["run-on-tasks-for"],
            "requires": task["requires"],
            "dependencies": {
                default_fuzz: default_fuzz,
                no_restrictive_fuzz: no_restrictive_fuzz,
            },
            "worker": {
                "implementation": task["worker"]["implementation"],
                "fuzz-tasks": [
                    {"task-id": {"task-reference": f"<{default_fuzz}>"}, "extra-args": "default"},
                    {"task-id": {"task-reference": f"<{no_restrictive_fuzz}>"}, "extra-args": "no-restrictive-starts"},
                ],
                "world-name": apworld_name,
                "world-version": version,
            },
        }


@transforms.add
def add_fuzz_report_scopes(config, tasks):
    pr_number = config.params.get("pull_request_number", -1)
    project = config.params['project'].lower()

    for task in tasks:
        scopes = task.setdefault("scopes", [])
        scopes.append(f"ap:github:action:create-apfuzz-comment-on-pr:{pr_number}")
        scopes.append(f"ap:github:repo:{project}")
        yield task
