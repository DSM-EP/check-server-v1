from app import create_app

from app.model.mongo_extension import init_mongodb
from app.model.mysql_extension import create_all_table

app = create_app()


@app.on_event('startup')
async def db_initialize():
    create_all_table()
    await init_mongodb()


if __name__ == '__main__':
    from uvicorn import run

    run(app)
