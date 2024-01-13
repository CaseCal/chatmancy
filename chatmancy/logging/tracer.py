SERVICE_NAME = "chatmancy"

try:
    from opentelemetry import trace
    from .. import __version__ as chatmancy_version

    tracer = trace.get_tracer(__name__)
    telemetry_installed = True
except ImportError:
    telemetry_installed = False


def trace(*args, **kwargs):
    def decorator(func):
        if telemetry_installed:

            def wrapped(*args, **kwargs):
                with tracer.start_as_current_span(
                    f"{SERVICE_NAME}.{func.__name__}",
                    attributes={
                        "service.name": SERVICE_NAME,
                        "service.version": chatmancy_version,
                        "function.name": func.__name__,
                    },
                ):
                    return func(*args, **kwargs)

            return wrapped
        else:
            return func

    return decorator
