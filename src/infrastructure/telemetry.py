"""Telemetry helpers to avoid duplicate OpenTelemetry tracer configuration."""

from __future__ import annotations

import os
from contextlib import suppress
from typing import Optional

__all__ = ["ensure_global_tracer_provider"]


_ALREADY_CONFIGURED = False


def ensure_global_tracer_provider() -> Optional[object]:
    """Ensure a single OpenTelemetry tracer provider is configured.

    Many third-party SDKs (e.g., Vertex AI, LangChain integrations) attempt to
    call :func:`opentelemetry.trace.set_tracer_provider` multiple times. The
    OpenTelemetry SDK only allows this once and will emit a warning on
    subsequent attempts. We proactively install a concrete tracer provider when
    the environment is otherwise using the proxy/no-op defaults so later calls
    become no-ops and the warning disappears.

    Returns
    -------
    Optional[object]
        The configured tracer provider, or ``None`` when OpenTelemetry is not
        available in the environment.
    """

    global _ALREADY_CONFIGURED  # pylint: disable=global-statement
    if _ALREADY_CONFIGURED:
        return None

    try:
        from opentelemetry import trace
        from opentelemetry.trace import NoOpTracerProvider, ProxyTracerProvider
    except ImportError:
        _ALREADY_CONFIGURED = True
        return None

    provider = trace.get_tracer_provider()

    # Respect explicit user configuration if they supplied one via environment
    # variables or prior initialization. Avoid installing another provider if a
    # concrete implementation is already active.
    if not isinstance(provider, (ProxyTracerProvider, NoOpTracerProvider)):
        _ALREADY_CONFIGURED = True
        return provider

    # Avoid eagerly importing the SDK when tracing is intentionally disabled.
    if os.environ.get("OTEL_PYTHON_DISABLE_TRACES", "").lower() in {"1", "true", "yes"}:
        _ALREADY_CONFIGURED = True
        return provider

    with suppress(ImportError):
        from opentelemetry.sdk.trace import TracerProvider as SDKTracerProvider

        trace.set_tracer_provider(SDKTracerProvider())
        _ALREADY_CONFIGURED = True
        return trace.get_tracer_provider()

    _ALREADY_CONFIGURED = True
    return provider
