from taskgraph.transforms.base import TransformSequence

transforms = TransformSequence()


@transforms.add
def generate_variant_tasks(config, tasks):
    """Duplicate each task for both fuzz variants (default and no-restrictive-starts)."""
    project = config.params['project'].lower()
    pr_number = config.params.get("pull_request_number", -1)

    for task in tasks:
        apworld_name = task["attributes"]["apworld_name"]
        version = task["attributes"]["version"]

        for extra_args_key in ["default", "no-restrictive-starts"]:
            if extra_args_key == "default":
                label = f"upload-fuzz-results-{apworld_name}-{version}"
                fuzz_task_label = f"fuzz-{apworld_name}-{version}"
            else:
                label = f"upload-fuzz-results-{extra_args_key}-{apworld_name}-{version}"
                fuzz_task_label = f"fuzz-{extra_args_key}-{apworld_name}-{version}"

            fuzz_index_path = f"ap.{project}.fuzz.pr.{pr_number}.{apworld_name}.{version}.{extra_args_key}.latest"

            yield {
                "label": label,
                "description": task["description"],
                "attributes": {
                    **task["attributes"],
                    "extra_args_key": extra_args_key,
                },
                "worker-type": task["worker-type"],
                "run-on-tasks-for": task["run-on-tasks-for"],
                "soft-dependencies": [fuzz_task_label],
                "worker": {
                    "implementation": task["worker"]["implementation"],
                    "fuzz-task": {"task-reference": f"<{fuzz_task_label}>"},
                    "fuzz-index-path": fuzz_index_path,
                    "world-name": apworld_name,
                    "world-version": version,
                    "extra-args": extra_args_key if extra_args_key != "default" else "",
                },
            }


@transforms.add
def add_upload_fuzz_scopes(config, tasks):
    project = config.params['project'].lower()

    for task in tasks:
        scopes = task.setdefault("scopes", [])
        scopes.append("ap:github:action:upload-fuzz-results:branch:main")
        scopes.append(f"ap:github:repo:{project}")
        yield task
