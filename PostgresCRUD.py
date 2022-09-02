import psycopg2, configparser, vlibDuplicate, configparser
from datetime import datetime, timezone

def config(filename='DuplicatorConfig.cfg', section='postgresql'):
    # create a parser
    parser = configparser.ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    print(db)
    return db

config_obj = configparser.ConfigParser(interpolation = None)
config_obj.read("DuplicatorConfig.cfg")
#defaultpath = dict(config_obj.items("query"))
queries = config_obj["query"]

params = config()
conn = psycopg2.connect(**params)
cur = conn.cursor()

# name = vlibDuplicate.main("C:/CPI/cad/AOITestBoard_testing.datj","C:/CPI/cad","AOITestBoard_testing")
# fam = "hellooo"
# dt = datetime.now(timezone.utc)

# q1 = """INSERT INTO family_model (model_name, datetime_creation) VALUES (%s,%s)"""
# to_insert1 = (fam, dt)
# cur.execute(q1, to_insert1)

# q2 = """INSERT INTO family_library_linkages (model_name, library_name, datetime_creation) VALUES (%s,%s,%s)"""
# to_insert2 = (fam, name, dt)
# cur.execute(q2, to_insert2)


for i in range (0,5):
    new_name = ("cad/AOITestBoard_new_0_"+str(i)+".dat",)
    q3 = """DELETE from family_library_linkages WHERE library_name = %s"""
    cur.execute(q3,new_name)

# q3 = """DELETE from family_library_linkages WHERE library_name = %s"""
# cur.execute(q3,("cad/AOITestBoard_new_12.dat",))

# q3 = """DELETE from family_model WHERE model_name = %s"""
# cur.execute(q3,("myx",))

# q4 = "DELETE from family_model WHERE model_name != %s"
# cur.execute(q4,("VITROXMASTER",))

conn.commit()

cur.close()
conn.close()

# #as an aware datetime
# from datetime import datetime, timezone

# utc_dt = str(datetime.now(timezone.utc))[:len(utc_dt)] # UTC time
# #dt = utc_dt.astimezone() # local time

# #print(len(dtt))
# print(utc_dt[:len(utc_dt)-6])
#print(dt)