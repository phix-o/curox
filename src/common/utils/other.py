from fastapi.routing import APIRoute

from src.main import app


def reverse(name: str) -> str:
    """Get a route by name from a ``FastAPI`` application."""
    results = [
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.name == name
    ]
    if not results:
        raise KeyError(f"No GET route registered with name: {name}")

    return results[0].path

