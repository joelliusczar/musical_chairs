import sqlite3
import calendar
from datetime import datetime, timedelta


def clean_up_history(conn, cutoffTimestamp):
    cursor = conn.cursor()
    params = (cutoffTimestamp, )
    cursor.execute("DELETE FROM [StationHistory] "
        "WHERE [LastPlayedTimestamp] < ?", params)
    cursor.close()

if __name__ == '__main__':
    config = get_config()
    dbName = config['dbName']
    searchBase = config['searchBase']
    conn = sqlite3.connect(dbName)
    dt = datetime.now()
    td = timedelta(days = 14)
    cutoffDate = dt - td
    cutoffTimestamp = calendar.timegm(cutoffDate.timetuple())
    clean_up_history(conn, cutoffTimestamp)
    conn.commit()
    conn.close()