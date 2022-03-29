from datetime import datetime as dt


def add_emojis_to_dict(dictionary: dict) -> dict:
    """
    Format a dictionary adding emojis indicating positive and negative values.
    Watch out: float values, including booleans, will be returned as strings.
    """
    dict_ = dictionary.copy()
    for k, v in dict_.items():
        if isinstance(v, bool):
            if v > 0:
                v = f'{v} ⭐'
            else:
                v = f'{v} ❗'
            dict_[k] = v
        elif isinstance(v, float):
            if v > 0:
                v = f'{v} ⭐'
            elif v < 0:
                v = f'{v} ❗'
            dict_[k] = v
        if isinstance(v, dict):
            dict_[k] = add_emojis_to_dict(v)
    return dict_


def format_datetime_element(datetime: dt) -> str:
    """ Style the displaying Dash format for a datetime object. """
    # TODO 2022.02.08 Insert timezone info
    str_datetime = str(datetime)
    if '.' in str_datetime:
        return str_datetime[:-3]
    return str_datetime


def format_dict_zeros(dictionary: dict) -> dict:
    """ Return a copy of the input dictionary replacing float zeros (0.0) to int zeros (0). """
    dict_ = dictionary.copy()
    for k, v in dict_.items():
        if v == 0:
            dict_[k] = 0
        if isinstance(v, dict):
            dict_[k] = format_dict_zeros(v)
    return dict_
