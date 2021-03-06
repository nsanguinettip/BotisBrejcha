import requests
import json

COMMON_HEADERS = {'Content-type': 'application/json'}
END_POINT = 'pizzapi.azurewebsites.net'
END_POINT_INFRA = '192.168.1.127'
PORT = 80
PORT_INFRA = 1919


############################################################################################################
#    TWITTER PROFILES
############################################################################################################
def get_twitter_profiles(account, delta, profile_count):
    response = requests.get("http://%s:%d/api/v1/TwitterProfiles?account=%s&delta=%s&profile_count=%s" % (END_POINT, PORT, account, delta, profile_count),
                            headers=COMMON_HEADERS)
    return response.json()


def get_manual_profiles(profile_count):
    response = requests.get("http://%s:%d/api/v1/TwitterProfiles/manual/?profile_count=%s" % (END_POINT, PORT, profile_count),
                            headers=COMMON_HEADERS)
    return response.json()


def update_validated_profiles(profile_list):
    response = requests.put("http://%s:%d/api/v1/TwitterProfiles/manual/" %
                            (END_POINT, PORT), json.dumps(profile_list), headers=COMMON_HEADERS)
    return response.json()

def add_blacklist(profile_list):
    response = requests.post("http://%s:%d/api/v1/TwitterProfiles/Blacklist/" %
                             (END_POINT, PORT), json.dumps(profile_list), headers=COMMON_HEADERS)
    return response.json()
############################################################################################################
#    JOBS
##########################################################################################################


def get_pending_jobs(infra_id):
    response = requests.get("http://%s:%d/api/v1/Jobs/?infra_id=%s" %
                             (END_POINT, PORT, infra_id), headers=COMMON_HEADERS)
    return response.json()


def get_recurrent_jobs(infra_id):
    response = requests.get("http://%s:%d/api/v1/Jobs/recurrent/?infra_id=%s" %
                             (END_POINT, PORT, infra_id), headers=COMMON_HEADERS)
    return response.json()


def add_pending_job(jobs_list):
    response = requests.post("http://%s:%d/api/v1/Jobs/" %
                             (END_POINT, PORT), json.dumps(jobs_list), headers=COMMON_HEADERS)
    return response.json()


def delete_pending_job(job_id):
    response = requests.delete("http://%s:%d/api/v1/Jobs/?job_id=%s" %
                               (END_POINT, PORT, job_id), headers=COMMON_HEADERS)
    return response.json()


def update_job(job_data):
    response = requests.put("http://%s:%d/api/v1/Jobs/" %
                             (END_POINT, PORT), json.dumps(job_data), headers=COMMON_HEADERS)
    return response.json()


def update_job_start(job_data):
    response = requests.put("http://%s:%d/api/v1/Jobs/start/" %
                             (END_POINT, PORT), json.dumps(job_data), headers=COMMON_HEADERS)
    return response.json()


############################################################################################################
#    INFRASTRUCTURE
##########################################################################################################
def get_infra_data():
    response = requests.get("http://%s:%d/api/v1/Infrastructure" %
                            (END_POINT, PORT), headers=COMMON_HEADERS)
    return response.json()


def start_remote_infra(infra_id):
    response = requests.get("http://%s:%d/api/v1/Infrastructure/start?infra_id=%s" %
                            (END_POINT_INFRA, PORT_INFRA, infra_id), headers=COMMON_HEADERS)
    return response.json()


def stop_remote_infra(infra_id):
    response = requests.get("http://%s:%d/api/v1/Infrastructure/stop?infra_id=%s" %
                            (END_POINT_INFRA, PORT_INFRA, infra_id), headers=COMMON_HEADERS)
    return response.json()


def reset_remote_infra(infra_id):
    response = requests.get("http://%s:%d/api/v1/Infrastructure/reset?infra_id=%s" %
                            (END_POINT_INFRA, PORT_INFRA, infra_id), headers=COMMON_HEADERS)
    return response.json()


def get_acc_infra_data(infra_id):
    response = requests.get("http://%s:%d/api/v1/Infrastructure/id?infra_id=%s" %
                            (END_POINT_INFRA, PORT_INFRA, infra_id), headers=COMMON_HEADERS)
    return response.json()


def add_infra_data(infra_data):
    response = requests.post("http://%s:%d/api/v1/Infrastructure/" %
                            (END_POINT, PORT), json.dumps(infra_data), headers=COMMON_HEADERS)
    return response.json()


def update_infra_data(infra_data):
    response = requests.put("http://%s:%d/api/v1/Infrastructure/" %
                            (END_POINT, PORT), json.dumps(infra_data), headers=COMMON_HEADERS)
    return response.json()


def get_infra_interactions(infra_id):
    response = requests.get("http://%s:%d/api/v1/Infrastructure/interactions/?infra_id=%s" %
                            (END_POINT_INFRA, PORT_INFRA, infra_id), headers=COMMON_HEADERS)
    return response.json()


def get_interaction_by_user(infra_id):
    response = requests.get("http://%s:%d/api/v1/Contacts/by_user/?infra_id=%s" %
                            (END_POINT_INFRA, PORT_INFRA, infra_id), headers=COMMON_HEADERS)
    return response.json()


def update_infra_interactions(infra_data):
    response = requests.post("http://%s:%d/api/v1/Infrastructure/interactions/" %
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


def get_contacts():
    response = requests.get("http://%s:%d/api/v1/Contacts/" %
                            (END_POINT_INFRA, PORT_INFRA), headers=COMMON_HEADERS)
    return response.json()
