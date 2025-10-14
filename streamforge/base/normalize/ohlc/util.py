from ciso8601 import parse_datetime


def parse_string_to_timestamp(date_string: str, offset: int=0) -> int:
    datetime_obj = parse_datetime(date_string)
    timestamp_obj = datetime_obj.timestamp() - offset
    return int(timestamp_obj)
