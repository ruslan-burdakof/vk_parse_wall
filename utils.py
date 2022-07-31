import sqlite3
import requests
from os.path import splitext, exists, join  as path_join
from os import mkdir

class PostMem:
    def __init__(self, data: dict):
        self._parse_dict(data)
		
    def __bool__(self):
        return self.recognized
		
    def _parse_dict(self, data: dict):
        if 'items' in data:
            if len(data['items'])>1:
                raise Exception("There are several entries in the dictionary?")
            data = data['items'][0]
        try:
            self.json = str(data)
            self.owner_id = int(data['owner_id'])
            self.id = int(data['id'])
            self.likes = int(data['likes']['count'])
            self.text = data['text']
            self.images = self._get_imgs(data)
            
            self.views = int(data['views']['count'])
            self.recognized = True
        except KeyError as e:
            if 'views' in str(e):
                self.views = -1
                self.recognized = True
        except Exception as e:
            print(f"Error convert data to PostMem({type(e)}): {e}")
            self.recognized = False
       
    def _get_imgs(self, data):
        images = []
        if 'copy_history' in data:
            data = data['copy_history'][0]
        if 'attachments' in data:
            attachments = data['attachments']
            for att_ in attachments:
                if att_['type'] != 'photo':
                    continue
                ans = att_['photo']['sizes'][-1]['url']
                images.append(ans)                    
        return images
 
    def itr_filenames_and_url(self):
        if self.images:
            if len(self.images) == 1:
                url = self.images[0].partition('?')[0]
                name = f"{self.owner_id}_{self.id}{splitext(url)[1]}"
                yield name, self.images[0]
            else:
                for inx, imag in enumerate(self.images):
                    url = imag.partition('?')[0]
                    name = f"{self.owner_id}_{self.id}part{inx}{splitext(url)[1]}"
                    yield name, imag
        return None

    def itr_commit_img_to_DB(self):
        for count, url in enumerate(self.images):
            yield (self.owner_id, self.id, count, url)

	def commit_post_to_DB(self):
        return (self.owner_id, self.id, self.views, self.likes, self.text, self.json)

class MemDB(sqlite3.Connection):
    def __init__(self, path_db="mem.s3db", path_img = 'mem'):
        self.path_db = path_db
        self.path_img = path_img
        self._create_img_folder()
        self._connect(path_db)

    def _connect(self, path_db):
        if not exists(path_db):
            super().__init__(path_db)
            self._create_DB()
        else:
            super().__init__(path_db)
    
    def _create_img_folder(self):
        if not exists(self.path_img):
            mkdir(self.path_img)

    def _create_DB(self):
        sqlRequest = '''CREATE TABLE posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        owner_id INTEGER,
                        post_id INTEGER,
                        views   INTEGER,
                        likes   INTEGER,
                        text    TEXT,
                        json    TEXT,
                        CONSTRAINT owner_post_id UNIQUE (
                            owner_id,
                            post_id
                            )
                        );
                     '''
        self.execute(sqlRequest)
        sqlRequest = '''CREATE TABLE pictures (
                        pict_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        owner_id INTEGER,
                        post_id    INTEGER,
                        count   INTEGER,
                        url     TEXT UNIQUE
                        );
                     '''
        self.execute(sqlRequest)

    def _save_to_img(self, post: PostMem):
        for name, url in post.itr_filenames_and_url():
            path = path_join(self.path_img, name)
            if exists(path):
                print(f"File exists: {name}")
                continue
            ptr = requests.get(url)
            out = open(path, "wb")
            out.write(ptr.content)
            out.close()
            print(f"Save: {name}")
    
    def _add_post_to_db(self, post: PostMem):
        try:
            insert='INSERT INTO posts(owner_id,post_id,views,likes,text,json) VALUES (?,?,?,?,?,?)'
            self.execute(insert, post.commit_post_to_DB())
            self.commit()
            if post.images:
                insert='INSERT INTO pictures(owner_id,post_id,count,url) VALUES (?,?,?,?)'
                self.executemany(insert, post.itr_commit_img_to_DB())
                self.commit()
            print(f"Put post to DB: {post.owner_id}_{post.id}")

        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                print('Database entry already exists')

        except Exception as e:
            print(f"Error reccord post in DB {type(e)}: {e}")

    def save_post(self, post: PostMem):
        self._add_post_to_db(post)
        if post.images:
            self._save_to_img(post)

def checking_for_nice_Ratio(post: PostMem, ratio = 0.03):
    if post.likes/post.views >= ratio:
        return True
    return False

def checking_for_nice_OnlyLikes(post: PostMem, likes: int):
    if post.likes >= likes:
        return True
    return False

def checking_true(post):
    return True