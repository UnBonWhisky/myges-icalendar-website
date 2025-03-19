#!/usr/bin/python3
import os, httpx, sys, base64, aiosqlite, uvicorn, aiofiles, secrets, asyncio
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from icalendar import Calendar

from config import *
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)

client = httpx.AsyncClient()

basepath = "./files" #"/var/www/html/files/"

def loop(minutes: int):
    """Décorateur pour exécuter une fonction périodiquement toutes les X minutes."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            while True:
                task = asyncio.create_task(func(*args, **kwargs))
                await asyncio.sleep(minutes * 60)
                await task
        return wrapper
    return decorator

@app.post("/api/calendar")
async def get_calendar(user_creds: UserCreds, request: Request):

    myges = MyGES_Informations()
    myges.basic_auth = user_creds.basic_auth
    myges.token = user_creds.token
    myges.expiry_date = user_creds.expiry_date

    if (user_creds.token is None) or (user_creds.expiry_date is None) or (not is_local_ip(request.client.host)):
        if user_creds.basic_auth is None:
            raise HTTPException(status_code=400, detail="No basic_auth provided")
        login_informations = await myges.get_token(user_creds.basic_auth)

        if login_informations.status_code != 302:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        else :
            user_creds.token = login_informations.token
            user_creds.expiry_date = login_informations.expiry_date

    decode_auth = base64.b64decode(user_creds.basic_auth.encode()).decode().split(":")

    try :
        async with aiofiles.open(f'{basepath}/{decode_auth[0]}.ics', 'r') as f:
            await f.close()
    except FileNotFoundError:
        global_calendar = await myges.get_calendar_events()

        await myges.create_calendar(global_calendar, basepath, decode_auth[0])

    api_key = secrets.token_hex(16)

    action_done, api_key = await myges.write_database(decode_auth[0], user_creds.basic_auth, api_key, user_creds.token, user_creds.expiry_date)


    return {
        "filename": f"{decode_auth[0]}",
        "api_key": api_key,
        "action": action_done
    }

@app.get("/calendar/feed/{filename}")
async def return_calendar(filename: str, api_key: str = Query(None)):
    if api_key is None:
        raise HTTPException(status_code=400, detail="No api_key provided")

    try :
        async with aiosqlite.connect('myges.db') as db:
            await db.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, basic_auth TEXT, api_key TEXT, token TEXT, expiry_date INT, update_time TEXT)")
            cursor = await db.cursor()

            await cursor.execute("SELECT username, api_key FROM users WHERE api_key = ? AND username = ?", (api_key, filename,))
            response = await cursor.fetchone()

            await cursor.close()

            if response is None:
                raise HTTPException(status_code=403, detail="Invalid informations provided")
            else :
                return FileResponse(f"{basepath}/{filename}.ics")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

@app.post("/calendar/renew")
async def renew_calendar(request: CalendarSettings):
    username = request.username
    apikey = request.api_key

    if username is None or apikey is None:
        raise HTTPException(status_code=400, detail="No username and apikey provided")

    await refresh_calendar(username, apikey)
    return "OK"

@app.post("/calendar/delete")
async def delete_calendar(request: CalendarSettings):
    username = request.username
    apikey = request.api_key

    if username is None or apikey is None:
        raise HTTPException(status_code=400, detail="No username and apikey provided")

    async with aiosqlite.connect('myges.db') as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, basic_auth TEXT, api_key TEXT, token TEXT, expiry_date INT, update_time TEXT)")
        cursor = await db.cursor()

        await cursor.execute("SELECT username, api_key FROM users WHERE username = ? AND api_key = ?", (username, apikey,))
        response = await cursor.fetchone()

        if response is None:
            raise HTTPException(status_code=404, detail="User not found")

        await cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        await db.commit()
        await cursor.close()

    try :
        os.remove(f"{basepath}/{username}.ics")
    except FileNotFoundError:
        pass

    return "OK"



@app.get('/api/token/get')
async def extension_token_get(request: Request):
    # Get the Authorization header
    header = request.headers.get("Authorization")
    if header is None:
        raise HTTPException(status_code=400, detail="No Authorization header provided")

    # Get the basic auth
    basic_auth = header.split(" ")[1]
    myges = MyGES_Informations()
    await myges.setup_http_client()
    login_informations = await myges.get_token(basic_auth)

    if login_informations.status_code != 302:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    else :

        return {
            "token": login_informations.token,
            "expires_in": login_informations.expires_in
        }

@loop(minutes=1)
async def refresh_loop():
    await refresh_calendar()


async def refresh_calendar(username: str = None, apikey: str = None):
    async with aiosqlite.connect('myges.db') as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, basic_auth TEXT, api_key TEXT, token TEXT, expiry_date INT, update_time TEXT)")
        cursor = await db.cursor()

        if username is None or apikey is None:
            await cursor.execute("SELECT username, basic_auth, token, expiry_date FROM users WHERE update_time = ?", (datetime.datetime.now().strftime("%H:%M"),))
            responses = await cursor.fetchall()
        else :
            await cursor.execute("SELECT username, basic_auth, token, expiry_date FROM users WHERE username = ? AND api_key = ?", (username, apikey,))
            responses = await cursor.fetchall()

        await cursor.close()

        if responses is None or responses == []:
            return

        for i, response in enumerate(responses) :
            myges = MyGES_Informations()
            if i % 5 == 0 :
                await myges.setup_http_client()
            myges.basic_auth = response[1]

            actual_time = int(datetime.datetime.now().timestamp())

            if actual_time > response[3]:
                login_informations = await myges.get_token(response[1])

                if login_informations.status_code != 302:
                    return
                else :
                    myges.token = login_informations.token
                    myges.expiry_date = login_informations.expiry_date

                    cursor = await db.cursor()
                    await cursor.execute("UPDATE users SET token = ?, expiry_date = ? WHERE username = ?", (login_informations.token, login_informations.expiry_date, response[0],))
                    await db.commit()
                    await cursor.close()
            else :
                myges.token = response[2]
                myges.expiry_date = response[3]

            global_calendar = await myges.get_calendar_events()

            await myges.create_calendar(global_calendar, basepath, response[0])

async def start_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=40500)
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await asyncio.gather(
        refresh_loop(),
        start_server()
    )

if __name__ == "__main__":
    asyncio.run(
        main()
    )
