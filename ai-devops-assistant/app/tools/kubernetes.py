import subprocess


KUBECTL = "/usr/local/bin/kubectl"


def run_kubectl(args: list[str]) -> str:
    result = subprocess.run(
        [KUBECTL] + args,
        capture_output=True,
        text=True,
        timeout=10,
    )

    if result.returncode != 0:
        return f"ERROR: {result.stderr.strip()}"

    return result.stdout.strip()


def get_pods(namespace: str = "staging") -> str:
    return run_kubectl(
        [
            "get",
            "pods",
            "-n",
            namespace,
            "-o",
            "wide",
        ]
    )


def get_deployment_image(namespace: str = "staging") -> str:
    return run_kubectl(
        [
            "get",
            "deployment",
            "cloud-native-devops-app",
            "-n",
            namespace,
            "-o",
            "jsonpath={.spec.template.spec.containers[0].image}",
        ]
    )


def get_pod_details(pod_name: str, namespace: str = "staging") -> dict:
    return {
        "pod": pod_name,
        "describe": run_kubectl(
            [
                "describe",
                "pod",
                pod_name,
                "-n",
                namespace,
            ]
        ),
        "logs": run_kubectl(
            [
                "logs",
                pod_name,
                "-n",
                namespace,
                "--tail=100",
            ]
        ),
        "previous_logs": run_kubectl(
            [
                "logs",
                pod_name,
                "-n",
                namespace,
                "--previous",
                "--tail=100",
            ]
        ),
    }


def find_pods_with_restarts(namespace: str = "staging") -> list[str]:
    output = run_kubectl(
        [
            "get",
            "pods",
            "-n",
            namespace,
            "--no-headers",
        ]
    )

    if output.startswith("ERROR:"):
        return []

    pods_with_restarts = []

    for line in output.splitlines():
        columns = line.split()

        if len(columns) < 5:
            continue

        pod_name = columns[0]
        restart_count = columns[3]

        try:
            restart_number = int(
                restart_count.split("(")[0]
            )
        except ValueError:
            continue

        if restart_number > 0:
            pods_with_restarts.append(pod_name)

    return pods_with_restarts


def investigate_restarted_pods(namespace: str = "staging") -> list[dict]:
    pods = find_pods_with_restarts(namespace)

    investigations = []

    for pod in pods:
        details = get_pod_details(pod, namespace)

        investigations.append(details)

    return investigations


def get_incident_evidence(namespace: str = "staging") -> dict:
    restarted_pods = find_pods_with_restarts(namespace)

    evidence = {
        "namespace": namespace,
        "restarted_pods": [],
    }

    for pod in restarted_pods:
        details = get_pod_details(pod, namespace)

        evidence["restarted_pods"].append(
            {
                "pod": pod,
                "describe": details["describe"],
                "logs": details["logs"],
                "previous_logs": details["previous_logs"],
            }
        )

    return evidence


def get_events(namespace: str = "staging") -> str:
    return run_kubectl(
        [
            "get",
            "events",
            "-n",
            namespace,
            "--sort-by=.lastTimestamp",
        ]
    )


def detect_pod_anomalies(pods: list[dict]) -> list[dict]:
    anomalies = []

    for pod in pods:
        pod_name = pod["pod"]
        ready = pod["ready"]
        status = pod["status"]
        restarts = pod["restarts"]

        try:
            restart_number = int(
                restarts.split("(")[0]
            )
        except ValueError:
            restart_number = 0

        if status in {
            "CrashLoopBackOff",
            "ImagePullBackOff",
            "ErrImagePull",
            "Pending",
            "Error",
            "Failed",
        }:
            anomalies.append(
                {
                    "pod": pod_name,
                    "type": "pod_status",
                    "detail": status,
                }
            )

        if ready != "1/1":
            anomalies.append(
                {
                    "pod": pod_name,
                    "type": "readiness",
                    "detail": f"Ready status is {ready}",
                }
            )

        if restart_number >= 3 and (
            status != "Running" or ready != "1/1"
        ):
            anomalies.append(
                {
                    "pod": pod_name,
                    "type": "restarts",
                    "detail": (
                        f"{restart_number} restarts detected "
                        "while pod is not fully healthy"
                    ),
                }
            )

    return anomalies


def detect_event_anomalies(events: str) -> list[str]:
    anomalies = []

    if not events:
        return anomalies

    keywords = [
        "Warning",
        "Failed",
        "BackOff",
        "Unhealthy",
        "FailedMount",
        "FailedScheduling",
        "ErrImagePull",
        "ImagePullBackOff",
        "CrashLoopBackOff",
    ]

    for line in events.splitlines():
        if any(keyword in line for keyword in keywords):
            anomalies.append(line.strip())

    return anomalies[-10:]


def build_incident_summary(namespace: str = "staging") -> dict:
    pods_output = get_pods(namespace)
    events_output = get_events(namespace)
    deployment_image = get_deployment_image(namespace)

    # Keep only the 15 most recent Kubernetes events.
    if events_output:
        events_output = "\n".join(
            events_output.splitlines()[-15:]
        )

    summary = {
        "namespace": namespace,
        "deployment_image": deployment_image,
        "health": "unknown",
        "pods": [],
        "pod_anomalies": [],
        "event_anomalies": [],
        "recent_events": events_output,
    }

    if pods_output.startswith("ERROR:"):
        summary["health"] = "unknown"
        summary["pod_error"] = pods_output
        return summary

    lines = pods_output.splitlines()

    # Skip kubectl table header.
    for line in lines[1:]:
        columns = line.split()

        if len(columns) < 5:
            continue

        pod_name = columns[0]
        ready = columns[1]
        status = columns[2]
        restarts = columns[3]

        summary["pods"].append(
            {
                "pod": pod_name,
                "ready": ready,
                "status": status,
                "restarts": restarts,
            }
        )

    summary["pod_anomalies"] = detect_pod_anomalies(
        summary["pods"]
    )

    summary["event_anomalies"] = detect_event_anomalies(
        events_output
    )

    if (
        summary["pod_anomalies"]
        or summary["event_anomalies"]
    ):
        summary["health"] = "unhealthy"
    else:
        summary["health"] = "healthy"

    return summary


def _extract_value(text: str, key: str) -> str:
    for line in text.splitlines():
        if key in line:
            return line.split(key, 1)[1].strip()

    return "Not available"


def _extract_events(text: str) -> list[str]:
    events = []

    in_events = False

    for line in text.splitlines():
        if line.strip() == "Events:":
            in_events = True
            continue

        if in_events and line.strip():
            if (
                line.startswith("  Normal")
                or line.startswith("  Warning")
            ):
                events.append(line.strip())

    return events