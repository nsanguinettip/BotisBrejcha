def get_formatted_date(now):
    now_str = "%s-%s-%s %s:%s:%s" % (str(now.month).zfill(2), str(now.day).zfill(2),
                                  str(now.year).zfill(2), str(now.hour).zfill(2), str(now.minute).zfill(2), str(now.second).zfill(2))
    return now_str


def get_variables(command_list):
    variables = {}

    accepted_variables = {
        "user": "account_username",
        "vm": "vm",
        "config": "config",
        "job": "bot_id",
        "job_id": "job_id",
        "duration": "duration",
        "intensity": "intensity",
        "start": "start_time",
        "recurrent": "recurrent",
        "schedule": "schedule",
        "post_list": "post_list",
        "only_dm": "only_dm",
        "interactions": "interactions",
        "filter_type": "filter_type",
        "inbox_link": "inbox_link"
    }

    for variable in command_list[1:]:
        if "=" in variable:
            split = variable.split("=")
            variable_name = split[0].strip()
            value = ""
            if len(split) > 2:
                for part in split[1:]:
                    value += part + '='
                value = value.replace('"', "").replace("'", '').strip()
            else:
                value = split[1].replace('"', "").replace("'", '').strip()

            for key, val in accepted_variables.items():
                if variable_name.lower() == key:
                    variables[val] = value

    return variables
