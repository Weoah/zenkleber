from fastapi import FastAPI
from time import time

from src import db, zendesk as zen, slack as sla


app = FastAPI()


@app.get('/')
async def index():
    return {'message': 'tranquilo e favoravel'}


@app.get('/periodic')
async def periodic():
    start = time()
    zen.search.main()
    return {'message': 'checado', 'process_time': f'{time() - start:.2f}'}


@app.get('/update_message')
async def update_message():
    zen.update.main()
    return {'message': 'ok', 'data': db.get_message()}


@app.get('/close_message')
async def close_message():
    zen.close.main()
    return {'message': 'ok', 'data': db.get_message()}


@app.get('/new_ticket')
async def new_ticket():
    zen.new.main()
    return {'message': 'ok'}


@app.get('/__truncate_table')
async def truncate_table():
    db._truncate_table()
    return {'message': 'ok'}


@app.get('/__truncate_tablee')
async def truncate_tablee():
    sla.test_message()
    return {'message': 'ok'}
