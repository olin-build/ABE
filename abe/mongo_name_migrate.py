from . import database as db
import logging
logging.basicConfig(level=logging.DEBUG)


db_name = os.getenv("HEROKU_APP_NAME", "testing")
logging.info("Updating allDay field in db {}".format(db_name))
res = db.Event.update({}, {"$rename": {"allDay": "all_day"}}, False, True)
print(res)
