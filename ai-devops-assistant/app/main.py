from fastapi import FastAPI

from app.ai.client import ask_ollama, is_ai_available, AI_PROVIDER
from app.tools.kubernetes import build_incident_summary


app = FastAPI(
    title="AI DevOps Assistant",
    description="AI-assisted Kubernetes incident investigation",
    version="0.2.0",
)


def deterministic_diagnosis(evidence: dict) -> str:
    """
    Provide a safe diagnosis from Kubernetes evidence
    without requiring an AI model.
    """

    if evidence["health"] == "healthy":
        return (
            "HEALTH:\n"
            "healthy - No active Kubernetes anomalies detected.\n\n"
            "ANOMALY:\n"
            "none\n\n"
            "EVIDENCE:\n"
            "All monitored pods are running and ready.\n\n"
            "POSSIBLE CAUSE:\n"
            "none\n\n"
            "NEXT DIAGNOSTICS:\n"
            "1. Continue monitoring pod health.\n"
            "2. Review recent Kubernetes events if an incident occurs."
        )

    diagnoses = []

    for anomaly in evidence.get("pod_anomalies", []):
        pod = anomaly["pod"]
        anomaly_type = anomaly["type"]
        detail = anomaly["detail"]

        if detail == "ImagePullBackOff":
            diagnoses.append(
                f"Pod {pod} is in ImagePullBackOff."
            )

        elif anomaly_type == "readiness":
            diagnoses.append(
                f"Pod {pod} is not ready: {detail}."
            )

        elif anomaly_type == "pod_status":
            diagnoses.append(
                f"Pod {pod} has abnormal status: {detail}."
            )

    image_pull_events = [
        event
        for event in evidence.get("event_anomalies", [])
        if "Failed to pull image" in event
        or "ErrImagePull" in event
        or "ImagePullBackOff" in event
    ]

    if image_pull_events:
        deployment_image = evidence.get(
            "deployment_image",
            "Not available",
        )

        possible_cause = (
            f"The Deployment is configured to use "
            f"'{deployment_image}', and Kubernetes cannot pull "
            "that image. The image repository or tag is likely "
            "unavailable."
        )
    else:
        possible_cause = (
            "The available evidence shows an active Kubernetes anomaly, "
            "but the root cause is not confirmed."
        )

    evidence_lines = []

    for pod in evidence.get("pods", []):
        if pod["status"] != "Running" or pod["ready"] != "1/1":
            evidence_lines.append(
                f"{pod['pod']}: "
                f"status={pod['status']}, "
                f"ready={pod['ready']}"
            )

    for event in image_pull_events[:2]:
        evidence_lines.append(event)

    next_diagnostics = [
        "Check the Helm image repository and tag.",
        "Verify that the configured image exists in the container registry.",
        "Review the pod events with: kubectl describe pod <pod> -n staging",
    ]

    return (
        "HEALTH:\n"
        "unhealthy - Active Kubernetes anomalies were detected.\n\n"
        "ANOMALY:\n"
        + "\n".join(diagnoses[:3])
        + "\n\n"
        "EVIDENCE:\n"
        + "\n".join(evidence_lines[:3])
        + "\n\n"
        "POSSIBLE CAUSE:\n"
        + possible_cause
        + "\n\n"
        "NEXT DIAGNOSTICS:\n"
        + "\n".join(
            f"{index}. {item}"
            for index, item in enumerate(next_diagnostics, 1)
        )
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ai/status")
def ai_status():
    return {
        "provider": AI_PROVIDER,
        "configured": AI_PROVIDER == "ollama",
        "model": "qwen3:4b" if AI_PROVIDER == "ollama" else None,
        "available": is_ai_available(),
    }


@app.get("/investigate")
def investigate():
    evidence = build_incident_summary("staging")

    deterministic_analysis = deterministic_diagnosis(
        evidence
    )

    ai_analysis = None

    if is_ai_available():
        prompt = f"""
You are a Kubernetes incident investigator.

Analyze ONLY this evidence:

{evidence}

Improve the following deterministic diagnosis with concise
evidence-based reasoning:

{deterministic_analysis}

Rules:
- Do not invent facts.
- Do not claim an unconfirmed root cause.
- Do not recommend changing, deleting, restarting, or scaling infrastructure.
- Return only the improved diagnosis.
"""

        try:
            ai_analysis = ask_ollama(prompt)

        except Exception as exc:
            ai_analysis = (
                "AI analysis unavailable. "
                f"Deterministic diagnosis is available. "
                f"Reason: {exc}"
            )

    return {
    
        "namespace": "staging",
        "status": evidence["health"],
        "deployment": {
            "image": evidence.get("deployment_image"),
        },

        "summary": (
            "No active Kubernetes anomalies detected."
            if evidence["health"] == "healthy"
            else "Active Kubernetes anomalies detected."
        ),
        "anomalies": evidence.get("pod_anomalies", []),
        "event_anomalies": evidence.get("event_anomalies", []),
        "diagnosis": deterministic_analysis,
        "ai_analysis": ai_analysis,
 }
    