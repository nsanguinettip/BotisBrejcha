def get_formatted_date(now):
    now_str = "%s-%s-%s %s:%s:%s" % (str(now.month).zfill(2), str(now.day).zfill(2),
                                  str(now.year).zfill(2), str(now.hour).zfill(2), str(now.minute).zfill(2), str(now.second).zfill(2))
    return now_str


def get_variables(command_list):
    variables = {}
    variables["account_username"] = ""
    variables["vm"] = ""
    variables["config"] = ""
    for variable in command_list[1:]:
        if variable != "":
            split = variable.split("=")
            variable_name = split[0].replace("-", "")
            value = split[1].replace('"', "").replace("'", '')
            if variable_name.lower() == "user":
                variables["account_username"] = value
            if variable_name.lower() == "vm":
                variables["vm"] = value
            if variable_name.lower() == "config":
                variables["config"] = value
    return variables
