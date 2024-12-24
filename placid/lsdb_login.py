from client.LSDBClient import LSDBClient
import os
import json
import sys
import time

if __name__ == '__main__':
    """
    TODO: Alter Main to request IP and Port (known values).
          Request user name and pass to Client Helper
    """
    if not int(os.environ.get('DEBUG')):
        username = sys.argv[1]
        password = sys.argv[2]
        my_client = LSDBClient()
        my_client.login(username, password)
        action = my_client.generalGET('action_results/2/')
        print(json.dumps(action, indent=4, sort_keys=True))
        time.sleep(5)
        print("\n --------------------------- \n")
        check_complete = my_client.generalGET('action_results/2/check_complete/')
        print(json.dumps(check_complete, indent=4, sort_keys=True))

    else:
        my_client = LSDBClient()
        my_client.login(os.environ.get('USERNAME'), os.environ.get('PASS'))
        action = my_client.generalGET('action_results/1/')
        print(json.dumps(action, indent=4, sort_keys=True))
        time.sleep(5)
        print("\n --------------------------- \n")
        check_complete = my_client.generalGET('action_results/1/check_complete/')
        print(json.dumps(check_complete, indent=4, sort_keys=True))
