import aiosqlite
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'urlbase.db')

CHARS = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'

async def transform(url:str):
    urls = await select_db(url, 'long_url')
    if urls:
        return urls[1]
    rec_id = await put_into_db(url)
    short_url = encode(rec_id)
    tmp = await update_db(short_url, rec_id)
    return short_url

def encode(num:int, CHARS=CHARS, base=62):
    arr = []
    while num>0:
        num, rem = divmod(num, base)
        arr.append(CHARS[rem])
    short_url = 'http://short/red/'+''.join(arr)
    return short_url


async def put_into_db(url:str):
    rec_id = None
    query = 'INSERT INTO urls (long_url) VALUES (?)'
    param = (url,)
    async with aiosqlite.connect(db_path) as db:
        async with db.execute(query, param) as cursor:
            rec_id = cursor.lastrowid   
        await db.commit()
    return rec_id 

async def update_db(url:str, rec_id:int):
    query = 'UPDATE urls SET short_url=? WHERE id=? '
    params = (url, rec_id)
    async with aiosqlite.connect(db_path) as db:
        await db.execute(query, params)
        await db.commit()
    return True    

async def select_db(url:str, url_type:str):
    urls = None
    query = f'SELECT long_url,short_url FROM urls WHERE {url_type}=?' 
    param = (url,)
    async with aiosqlite.connect(db_path) as db:
        async with db.execute(query, param) as cursor:
            urls = await cursor.fetchone()
    return urls if urls is not None else None

