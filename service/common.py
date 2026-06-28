def scalar(connection, sql, params=()):
    cur = connection.cursor()
    cur.execute(sql, params)
    row = cur.fetchone()
    return row[0] if row else 0
