import vk_api
from vk_api.vk_api import VkUserPermissions as vkPer

import pickle
from os.path import exists

def load_last_session(path = None) -> (str, dict):
    if path is None:
        path = "last_session.pkl"
    if exists(path):
        login, token = pickle.load(open(path,"rb"))
        return (login, token)
    raise Exception(f"file lats session not found: {path}")

def save_session(vk_session: vk_api.vk_api.VkApi, path = None):
    assert isinstance(vk_session, vk_api.vk_api.VkApi)
    del vk_session.password
    if path is None:
        path = "last_session.pkl"
    pickle.dump((vk_session.login, vk_session.token),
                open(path, "wb" ))
    print(f"file lats session save: {path}")

def get_session(login = None,
                password = None,
                path_to_last_save_session = None) -> vk_api.vk_api.VkApi:
    if login is not None and password is not None:
        usr_scope = vkPer.WALL|vkPer.STATUS|vkPer.PAGES|vkPer.PHOTOS
        vk_session = vk_api.VkApi(login,
                                  password,
                                  scope = usr_scope)
        vk_session.auth()
        save_session(vk_session)            
        return vk_session
    if login is None and password is None:
        login, token = load_last_session(path_to_last_save_session)
        vk_session = vk_api.VkApi(login = login, token = token['access_token'])
##        vk_session.auth()
        return vk_session

def get_token(login = None,
              password = None,
              path_to_last_save_session = None) -> str:
    if login is not None and password is not None:
        usr_scope = vkPer.WALL|vkPer.STATUS|vkPer.PAGES|vkPer.PHOTOS
        vk_session = vk_api.VkApi(login,
                                  password,
                                  scope = usr_scope)
        return vk_session.token['access_token']
    if login is None and password is None:
        login, token = load_last_session(path_to_last_save_session)
        return token['access_token']
    return session.token['access_token']


if __name__ == '__main__':
    from sys import argv
    if len == 3:
        login, password = argv[1], argv[2]
        get_session(login, password)
    else:
        print('enter: python connect.py "login" "password"')
        print('restart: python connect.py')
