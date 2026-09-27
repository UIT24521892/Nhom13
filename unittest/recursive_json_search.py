from policy import POLICY
from test_data import data

VALID_ROLES = {"admin", "operator", "viewer"}


def filter_for_role(value, role):
    """Loại trường không được phép khỏi object/list được trả về."""
    if isinstance(value, dict):
        return {
            k: filter_for_role(v, role)
            for k, v in value.items()
            if k not in POLICY or role in POLICY[k]
        }
    if isinstance(value, list):
        return [filter_for_role(item, role) for item in value]
    return value


def json_search(key, input_object, role=None):
    role = "viewer" if role is None else role

    if role not in VALID_ROLES:
        return []
    if key in POLICY and role not in POLICY[key]:
        return []

    ret_val = []

    if isinstance(input_object, dict):
        for k, v in input_object.items():
            if k == key:
                ret_val.append({k: filter_for_role(v, role)})
            if isinstance(v, (dict, list)):
                ret_val.extend(json_search(key, v, role))

    elif isinstance(input_object, list):
        for item in input_object:
            if isinstance(item, (dict, list)):
                ret_val.extend(json_search(key, item, role))

    return ret_val


if __name__ == "__main__":
    print(json_search("issueSummary", data, role="viewer"))
