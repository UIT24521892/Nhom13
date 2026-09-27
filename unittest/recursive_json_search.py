"""Recursive JSON search with role-based filtering for protected fields."""

from policy import POLICY


_ROLES = {"admin", "operator", "viewer"}


def _effective_role(role):
    """Treat absent and unrecognized roles as least-privileged viewers."""
    return role if role in _ROLES else "viewer"


def _can_read(key, role):
    """Return whether ``role`` is authorized to read a policy-controlled key."""
    allowed_roles = POLICY.get(key)
    return allowed_roles is None or role in allowed_roles


def _redact(value, role):
    """Return a recursively filtered copy, removing fields denied to role."""
    if isinstance(value, dict):
        return {
            key: _redact(child, role)
            for key, child in value.items()
            if _can_read(key, role)
        }
    if isinstance(value, list):
        return [_redact(child, role) for child in value]
    return value


def json_search(key, input_object, role=None):
    """Collect all values stored under ``key`` in nested dicts and lists.

    Policy-controlled keys are returned only to an allowed role. Matching
    parent objects and lists are recursively filtered before they are exposed.
    """
    effective_role = _effective_role(role)
    if not _can_read(key, effective_role):
        return []

    results = []

    def visit(value):
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                if child_key == key:
                    results.append(_redact(child_value, effective_role))
                visit(child_value)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(input_object)
    return results
