import requests
import json

COMMON_HEADERS = {'Content-type': 'application/json'}
END_POINT = '127.0.0.1'
PORT = 5000


############################################################################################################
#    TWITTER PROFILES
############################################################################################################
def get_twitter_profiles(account, delta, profile_count):
    response = requests.get("http://%s:%d/api/v1/TwitterProfiles?account=%s&delta=%s&profile_count=%s" % (END_POINT, PORT, account, delta, profile_count),
                            headers=COMMON_HEADERS)
    return response.json()


############################################################################################################
#    JOBS
##########################################################################################################


def get_pending_jobs(infra_id):
    pass


def add_pending_job():
    pass


def delete_pending_job(job_id):
    pass


############################################################################################################
#    SCHEDULE
##########################################################################################################
def get_infra_data():
    response = requests.get("http://%s:%d/api/v1/Infrastructure" %
                            (END_POINT, PORT), headers=COMMON_HEADERS)
    return response.json()


def get_acc_infra_data(account_username):
    response = requests.get("http://%s:%d/api/v1/Infrastructure/account/?account_username=%s" %
                            (END_POINT, PORT, account_username), headers=COMMON_HEADERS)
    return response.json()


def add_infra_data(infra_data):
    response = requests.post("http://%s:%d/api/v1/Infrastructure/" %
                            (END_POINT, PORT), json.dumps(infra_data), headers=COMMON_HEADERS)
    return response.json()


def update_infra_data(infra_data):
    response = requests.put("http://%s:%d/api/v1/Infrastructure/" %
                            (END_POINT, PORT), json.dumps(infra_data), headers=COMMON_HEADERS)
    return response.json()


def delete_infra_data(infra_id):
    response = requests.delete("http://%s:%d/api/v1/Infrastructure/?infra_id=%s" %
                             (END_POINT, PORT, infra_id), headers=COMMON_HEADERS)
    return response.json()

############################################################################################################
#    CONTACTS
##########################################################################################################
def insert_contacts(contacts_list):
    response = requests.post("http://%s:%d/api/v1/Contacts/" % (END_POINT, PORT), json.dumps(contacts_list), headers=COMMON_HEADERS)
    return response.json()