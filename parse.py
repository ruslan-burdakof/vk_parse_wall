from connect import get_session
from utils import PostMem, MemDB
from utils import checking_for_nice_Ratio, checking_for_nice_OnlyLikes
from os.path import exists
import pickle

def iterate_wall_get(session, offset, count = 1, max_count = 150):
    step = 0
    while step < max_count:
        print(f"iterate offset: {offset}")
        post = session.method('wall.get', {'count': 1, 'offset': offset})
        offset += 1
        step += 1
        yield post

from pprint import pprint

def save_wall(wall, checking):
    last_save_post = None
    db = MemDB()
    for step, data in enumerate(wall, 1):
        try:
            post = PostMem(data)
            print(f"owner_id:{post.owner_id}\tpost:{post.id}\tstep:{step}")
            if not post:
                print("Post not recognized")
                print(post.json)
                continue
            if checking(post):
                db.save_post(post)
                last_save_post = post
        except Exception as e:
            print(f"Error parsing wall {type(e)}: {e}")
            return e, data
    db.close()
    return step, last_save_post

def cleare_wall(session, wall):
    for step, data in enumerate(wall, 1):
        try:
            owner_id = data['items'][0]['owner_id']
            post_id = data['items'][0]['id']
            print(f"Cleare owner_id:{owner_id}\tpost:{post_id}")
            cleare = session.method('wall.delete', {'owner_id': owner_id,
                                                    'post_id': post_id})
            if cleare != 1:
                print(f"wall.delete() return: {cleare}")
                raise Exception("Error cleare")
        except Exception as e:
            print(f"Error cleare wall {type(e)}: {e}")
            return e, cleare
    return step, cleare

if __name__ == '__main__':
    from sys import argv
    login, password = None, None
    try:
        login, password = argv[1], argv[2]
        assert len(argv) <= 3
    except:
        print('enter: python parse.py "login" "password"')
        print('restart: python parse.py')
    
##    login = "+7**********"
##    password = "*******"

    session = get_session(login, password)
  
    if exists("last_post.pkl"):
        login, offset, last_post = pickle.load(open("last_post.pkl", "rb"))
        if session.login == login:
            offset = offset
    else:
        offset = 0

    offset = 0
    step=0
    max_count = 1000
    min_likes = 5
    checking = lambda post: checking_for_nice_OnlyLikes(post, min_likes)

    wall = iterate_wall_get(session, offset, max_count = max_count)
    step, last_post = save_wall(wall, checking)
##    data = cleare_wall(session, wall)

    with open("last_post.pkl", "wb") as file:
        pickle.dump((session.login, offset+step, last_post), file)