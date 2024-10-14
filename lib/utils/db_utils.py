import mysql.connector

cxn = mysql.connector.connect(
    user="relicbot",
    password="7s@6&9&Bqp02&^0y@Sr2HuXFQua$D4ut4ejFjW1C",
    host="relicbot.mysql.database.azure.com",
    port=3306,
    database='relicbot')
cur = cxn.cursor()


def with_commit(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        commit()

    return inner


def commit():
    # print("Committing..")
    cxn.commit()


# def autosave(sched):
#     sched.add_job(commit, CronTrigger(second='0'))


def close():
    cxn.close()


def field(command, *values):
    cur.execute(command, tuple(values))

    if (fetch := cur.fetchone()) is not None:
        return fetch[0]


def record(command, *values):
    cur.execute(command, tuple(values))

    return cur.fetchone()


def records(command, *values):
    cur.execute(command, tuple(values))

    return [item for item in cur.fetchall()]


def records_dict(command, *values):
    cur.execute(command, tuple(values))

    return dict(cur.fetchall())


def list_records(command, input_list):
    list_query = ', '.join(['%s'] * len(input_list))
    command = command % (list_query,)
    return records(command, input_list)


def column(command, *values):
    cur.execute(command, tuple(values))

    return [item[0] for item in cur.fetchall()]


def execute(command, *values):
    cur.execute(command, tuple(values))


def multiexec(command, valueset):
    cur.executemany(command, valueset)


def scriptexec(path):
    with open(path, "r", encoding="utf-8") as script:
        cur.executescript(script.read())
