from typing import Union
from pydantic import BaseModel
from urllib.parse import urlparse
import httpx, random, datetime, dateutil.relativedelta, aiosqlite, aiofiles, httpcore, asyncio, json, os
from icalendar import Event, vText, Calendar
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

def proxy_handler(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        while True:
            try:
                return await func(self, *args, **kwargs)
            
            except (httpx.ProxyError, httpcore.ProxyError) as e:
                print(f"=== Proxy Error : {str(e)} ===")
                await asyncio.sleep(0.1)
            
            except (httpx.ConnectTimeout, httpx.ReadTimeout) as e:
                current_timeout_loop = self.connect_timeout_loop
                async with self.setup_proxy_lock :
                    
                    if self.connect_timeout_loop < 3 and current_timeout_loop == self.connect_timeout_loop :
                        print(f"=== {str(type(e).__name__)} : {str(e)} ===")
                        await asyncio.sleep(0.1)
                        self.connect_timeout_loop += 1
                        
                    if self.connect_timeout_loop >= 3 and current_timeout_loop == self.connect_timeout_loop :
                        await self.setup_http_client(reason = str(type(e).__name__), reason_message = str(e))
                        await asyncio.sleep(0.1)
                        self.connect_timeout_loop = 0
                    
    return wrapper

AddressCampus = {
    "NATION1": "242 rue du Faubourg Saint Antoine, 75012 Paris",
    "NATION2": "220 rue du Faubourg Saint Antoine, 75012 Paris",
    "ERARD": "21 rue Erard, 75012 Paris",
    "VOLTAIRE1": "1 rue Bouvier, 75011 Paris",
    "VOLTAIRE2": "20 rue Bouvier, 75011 Paris",
    "MONTSOURIS": "5 rue Lemaignan, 75014 Paris",
    "JOURDAN": "10 boulevard Jourdan, 75014 Paris",
    "RANELAGH": "64 rue du Ranelagh, 75016 Paris",
    "QUAICITROEN": "35 quai André Citroën, 75015 Paris",
    "MAINDOR": "8-14 passage de la Main d'Or, 75011 Paris",
    "RAUCH": "1 passage Rauch, 75011 Paris",
    "VAUGIRARD": "273/277 rue de Vaugirard, 75015 Paris",
    "GRANGESAUXBELLES": "39 rue de la Grange aux Belles, 75010 Paris",
    "MONTROUGE": "13 rue Camille Pelletan, 92120 Montrouge"
}

class CalendarSettings(BaseModel):
    username: str | None = None
    api_key: str | None = None

class UserCreds(BaseModel):
    basic_auth: Union[None, str] = None
    token: Union[None, str] = None
    expiry_date: Union[None, int] = None

class TokenInformations(BaseModel):
    token: Union[None, str]
    expiry_date: Union[None, int]
    status_code: int
    expires_in: Union[None, int] = None

def is_local_ip(ip: str) -> bool:
    """Check if the request is from a local IP (127.0.0.1, 192.168.x.x, etc.)"""
    list_private_ip = [
        "10.",
        "127.",
        "172.16",
        "172.17",
        "172.18",
        "172.19",
        "172.20",
        "172.21",
        "172.22",
        "172.23",
        "172.24",
        "172.25",
        "172.26",
        "172.27",
        "172.28",
        "172.29",
        "172.30",
        "172.31",
        "192.168.",
        "::1"
    ]
    for private_ip in list_private_ip:
        if ip.startswith(private_ip):
            return True
    return False

class MyGES_Informations():
    def __init__(self, *args, **kwargs):
        self.client = httpx.AsyncClient()
        self.basic_auth = None
        self.token = None
        self.expiry_date = None
        self.proxy = []

        self.setup_proxy_lock = asyncio.Lock()
        self.connect_timeout_loop = 0

        self.current_credentials = [os.getenv("PROXY_USERNAME"), os.getenv("PROXY_PASSWORD")]
    
    async def setup_http_client(self, reason: str = None, reason_message: str = None):
        """Returns a configured httpx.AsyncClient with optional proxy"""

        self.proxy = await self.setup_proxy() if self.proxy == [] else self.proxy

        if self.proxy == [] :
            proxy = None
        else :
            proxy = random.choice(self.proxy)
            self.proxy.remove(proxy)

        self.client = httpx.AsyncClient(proxy=proxy)
        print(f"=== Proxy Setup updated ! New proxy server : {proxy.replace(f'https://{self.current_credentials[0]}:{self.current_credentials[1]}@', '').replace(':89', '')}{' | Reason : ' + reason + ' - ' + reason_message if reason is not None and reason_message is not None else '' } ===")

    async def setup_proxy(self):
        """Fetches proxy from NordVPN API and returns a random proxy."""
        ProxyClient = httpx.AsyncClient()
        try :
            resp = await ProxyClient.get("https://api.nordvpn.com/v1/servers/recommendations?identifier=proxy_ssl&limit=500")
            resp = resp.json()
        except :
            with open("backup_servers.json", "r") as f :
                resp = json.load(f)
        proxies = []
        for machine in resp :
            if machine["status"] == "online":
                got_proxy = False
                for service in machine["services"] :
                    if service["identifier"] == "proxy":
                        got_proxy = True
                        break
                if got_proxy :
                    for technology in machine["technologies"] :
                        if technology["identifier"] == "proxy_ssl" :
                            proxies.append(f"https://{self.current_credentials[0]}:{self.current_credentials[1]}@{machine['hostname']}:89")
                            break

        return random.sample(proxies, k=50) if proxies else None
    
    @proxy_handler
    async def get_token(self, basic_auth: str):
        """Fetches the OAuth token and processes the response."""
        
        headers = {
            "Authorization": f"Basic {basic_auth}"
        }
        resp = await self.client.get(
            "https://authentication.kordis.fr/oauth/authorize?response_type=token&client_id=myGES-app",
            headers=headers,
            follow_redirects=False
        )
        if resp.status_code == 302:
            location = urlparse(resp.headers["Location"])
            fragments = location.fragment.split("&")
            infos = {}
            for fragment in fragments:
                key, value = fragment.split("=")
                infos[key] = value
            self.token = infos["access_token"]
            self.expiry_date = int(datetime.datetime.now().timestamp()) + int(infos["expires_in"])
            self.basic_auth = basic_auth

            return TokenInformations(token=self.token, expiry_date=self.expiry_date, status_code=resp.status_code, expires_in=int(infos["expires_in"]))
        
        else :
            return TokenInformations(token=None, expiry_date=None, status_code=resp.status_code)
    
    async def get_date(self, more_month: int):
        day1 = datetime.datetime.today().replace(day=1, hour=0, minute=0, second=0) + dateutil.relativedelta.relativedelta(months=more_month)
        LastDate = day1.replace(day=28, hour=23, minute=59, second=59) + datetime.timedelta(days=4)
        LastDate = LastDate - datetime.timedelta(days=LastDate.day)

        day1 = (int(day1.timestamp())+3600)*1000
        LastDate = (int(LastDate.timestamp())+3600)*1000

        return day1, LastDate

    async def get_calendar(self, day1: int, LastDay: int):
        url = f"https://api.kordis.fr/me/agenda?start={day1}&end={LastDay}"
        headers = {
            'accept-encoding': 'gzip',
            'authorization': f'bearer {self.token}',
            'connection': 'Keep-Alive',
            'user-agent': 'okhttp/3.13.1'
        }
        calendrier = await self.client.get(url, headers=headers, timeout=30)
        return calendrier.json()
    
    @proxy_handler
    async def get_calendar_events(self):
        """Fetches the calendar events and return all classes."""
        global_calendar = []
        for month in range(2):
            day1, LastDay = await self.get_date(month)
            calendrier = await self.get_calendar(day1, LastDay)

            global_calendar.append(calendrier)
        
        return global_calendar
    
    async def create_events(self, calendrier, ics_file, dtstamp):
        """Creates events from the calendar."""
        
        for calendar_event in calendrier["result"]:
            event = Event()
            
            # UID of the event
            event.add('uid', f"Class_{calendar_event['reservation_id']}")
            
            # Check if it's a professor or student data based on 'classes'
            is_professor = calendar_event["classes"] != "None"
            
            # Construct the summary of the event
            campus_name = ""
            if calendar_event["rooms"] and isinstance(calendar_event["rooms"], list):
                campus_name = calendar_event["rooms"][0]["campus"]
                room_name = calendar_event["rooms"][0]["name"]
                summary = f"{calendar_event['name']} - {campus_name} - {room_name}"
            else:
                summary = f"{calendar_event['name']} - {calendar_event['discipline']['teacher']}"
            
            event.add('summary', summary)
            
            # Timestamp of the event
            dtstart = datetime.datetime.fromtimestamp(int(calendar_event["start_date"]) / 1000, tz=datetime.timezone.utc)
            event.add('dtstart', dtstart)
            
            dtend = datetime.datetime.fromtimestamp(int(calendar_event["end_date"]) / 1000, tz=datetime.timezone.utc)
            event.add('dtend', dtend)
            
            event.add('dtstamp', dtstamp)
            
            address = ""
            description = ""
            
            # Manage the description and location of the event
            if is_professor:
                # Description for professor version
                classes_info = calendar_event["classes"] if calendar_event["classes"] != "None" else "Non spécifiées"
                description += (f"Classes : {classes_info}\n"
                                f"Type de classe : {calendar_event['type']}\n"
                                f"Type de présence : {calendar_event['modality']}\n")
            else:
                # Description for student version
                student_group_name = calendar_event["discipline"]["student_group_name"]
                description += (f"Groupe : {student_group_name}\n"
                                f"Type de classe : {calendar_event['type']}\n"
                                f"Type de présence : {calendar_event['modality']}\n")
            
            # Handle room and address information
            if calendar_event["type"] == "Cours" or calendar_event["type"].startswith("Cours"):
                if calendar_event["modality"] == "Présentiel":
                    if not isinstance(calendar_event["rooms"], list) or not calendar_event["rooms"]:
                        AddressCampusValue = "En attente de réservation"
                        description += ('Campus : SALLE NON RÉSERVÉE\n'
                                        'Adresse : NON DISPONIBLE\n')
                        address = "En attente de réservation"
                    else:
                        try:
                            AddressCampusValue = AddressCampus[campus_name]
                        except KeyError:
                            print(f"========== Campus **{campus_name}** not found in AddressCampus ==========")
                            AddressCampusValue = "NON DISPONIBLE"
                        description += (f"Campus : {campus_name}\n"
                                        f"Salle : {room_name}\n"
                                        f"Adresse : {AddressCampusValue}\n")
                        address = AddressCampusValue

                elif calendar_event["modality"] == "Distanciel":
                    AddressCampusValue = f"{calendar_event['type']} à distance"
                    description += f"Adresse : {AddressCampusValue}\n"
                    address = AddressCampusValue
                else:
                    AddressCampusValue = "Aucune information disponible"
                    description += "Adresse : Aucune information disponible\n"
                    address = AddressCampusValue

            elif calendar_event["type"] in ["Examen", "Soutenance"]:
                if not calendar_event["modality"] and not calendar_event["rooms"]:
                    AddressCampusValue = "En attente des informations"
                    description += "Informations indisponibles pour le moment\n"
                    address = AddressCampusValue

                elif isinstance(calendar_event["rooms"], list) and calendar_event["rooms"]:
                    salles = [room["name"] for room in calendar_event["rooms"] if room["campus"] == campus_name]
                    try:
                        AddressCampusValue = AddressCampus[campus_name]
                    except KeyError:
                        print(f"========== Campus **{campus_name}** not found in AddressCampus ==========")
                        AddressCampusValue = "NON DISPONIBLE"
                    description += (f"Campus : {campus_name}\n"
                                    f"Salle{'s' if len(salles) > 1 else ''} : {', '.join(salles)}\n"
                                    f"Adresse : {AddressCampusValue}\n")
                    address = AddressCampusValue

                elif calendar_event["modality"] and not calendar_event["rooms"]:
                    if calendar_event["modality"] == "Présentiel":
                        AddressCampusValue = "En attente des informations"
                        description += "Informations indisponibles pour le moment\n"
                        address = AddressCampusValue
                    else:
                        AddressCampusValue = f"{calendar_event['type']} à distance"
                        description += f"Adresse : {AddressCampusValue}\n"
                        address = AddressCampusValue
                else:
                    AddressCampusValue = "Aucune information disponible"
                    description += "Adresse : Aucune information disponible\n"
                    address = AddressCampusValue

            elif calendar_event["type"] == "Autre":
                if calendar_event["modality"] == "Présentiel":
                    if not isinstance(calendar_event["rooms"], list) or not calendar_event["rooms"]:
                        AddressCampusValue = "En attente de réservation"
                        description += ('Campus : SALLE NON RÉSERVÉE\n'
                                        'Adresse : NON DISPONIBLE\n')
                        address = "En attente de réservation"
                    else:
                        try:
                            AddressCampusValue = AddressCampus[campus_name]
                        except KeyError:
                            print(f"========== Campus **{campus_name}** not found in AddressCampus ==========")
                            AddressCampusValue = "NON DISPONIBLE"
                        description += (f"Campus : {campus_name}\n"
                                        f"Salle : {room_name}\n"
                                        f"Adresse : {AddressCampusValue}\n")
                        address = AddressCampusValue
                elif calendar_event["modality"] == "Distanciel":
                    AddressCampusValue = "Cours à distance"
                    description += f"Adresse : {AddressCampusValue}\n"
                    address = AddressCampusValue
                else:
                    AddressCampusValue = "Aucune information disponible"
                    description += "Adresse : Aucune information disponible\n"
                    address = AddressCampusValue
            else:
                continue
            
            # Add a generic contact information at the end of the description
            description += "\nUn problème ? Contactez le créateur par mail sur contact@unbonwhisky.fr"

            # Add description and location to the event
            event.add('description', description)
            event.add('location', vText(address))

            # Add priority to the event
            event.add('priority', 5)

            # Add the event to the calendar
            ics_file.add_component(event)

            
    async def write_database(self, username: str, basic_auth: str, api_key: str, token: str, expiry_date: int):
        async with aiosqlite.connect('myges.db') as db:
            await db.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, basic_auth TEXT, api_key TEXT, token TEXT, expiry_date INT, update_time TEXT)")
            cursor = await db.cursor()
            await cursor.execute("SELECT username, basic_auth, api_key FROM users WHERE username = ?", (username,))
            response = await cursor.fetchone()
            actual_key = None
            if response is None :
                await db.execute("INSERT INTO users (username, basic_auth, api_key, token, expiry_date, update_time) VALUES (?, ?, ?, ?, ?, ?)", (username, basic_auth, api_key, token, expiry_date, datetime.datetime.now().strftime("%H:%M")))
                action = "add"
                actual_key = api_key
            elif basic_auth != response[1] :
                await db.execute("UPDATE users SET basic_auth = ?, api_key = ? WHERE username = ?", (basic_auth, api_key, username,))
                action = "update"
                actual_key = api_key
            else:
                actual_key = response[2]
                action = "nothing"
            
            await db.commit()
            await db.close()
            
        return action, actual_key

    async def create_calendar(self, global_calendar: list, basepath: str, user: str):
        cal = Calendar()
        cal.add('prodid', '//Made by Flavien FOUQUERAY - contact@unbonwhisky.fr//')
        cal.add('version', '2.0')
        
        dtstamp = datetime.datetime.now(tz=datetime.timezone.utc)
        
        for x in range(len(global_calendar)):
            await self.create_events(global_calendar[x], cal, dtstamp)
        
        async with aiofiles.open(f'{basepath}/{user}.ics', 'wb+') as f:
            await f.write(cal.to_ical())
            await f.close()
