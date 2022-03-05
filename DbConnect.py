import psycopg2
from contextlib import closing

from configpars import config
from Dto import *
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s:%(message)s', )
log = logging.getLogger(__name__)

class BdService:
    def __init__(self):
        self.db_connect = _Db()

    def get_all_users(self) -> List[UsersDto]:
        return Mapper.mapToUserDto(self.db_connect.execute_for_many("select * from users"))

    def has_user_in_db(self, userId) -> bool:
        return self.db_connect.execute_for_one(
            str("select exists (select * from users where id = {})".format(userId))
        )

    def add_user(self, user: list):
        self.db_connect.insert(
            "insert into users(id, firstname, lastname, username, additionalinfo, isblock) values (%s, %s, %s, %s, %s, %s)",
            user
        )

    def add_friend(self, value):
        return self.db_connect.insert(
            str("insert into userstofriend (userid, friendid) values (%s, %s)"),
            value
        )

    def has_friend(self, userId, friendId) -> bool:
        return self.db_connect.execute_for_one(
            str("select exists (select * from userstofriend where userId = {} and friendId = {})".format(userId,
                                                                                                         friendId))
        )

    def get_user_frienids(self, userid) -> List[UsersDto]:
        return Mapper.mapToUserDto(self.db_connect.execute_for_many(
            str("""select u.* from users u 
                    join userstofriend uf on u.id = uf.friendid 
                    where uf.userid = {} """.format(userid))
        ))

    def delete_friend(self, value):
        self.db_connect.insert(
            str("delete from userstofriend where userId = %s and friendId = %s"),
            value
        )

    def update_user_block(self, block: bool, userId):
        self.db_connect.insert(
            "update users set isblock = %s where id = %s ",
            [block, userId]
        )

    def is_blocked_user(self, userId):
        return self.db_connect.execute_for_one(
            "select isblock from users u where id = {} ".format(userId)
        )

    def add_offer(self, userId, offer: str, createdate):
        self.db_connect.insert(
            "insert into usersoffer (userid, offer, createdate) values (%s, %s, %s)",
            [userId, offer, createdate]
        )

    def get_admin_list(self):
        return Mapper.mapToList(self.db_connect.execute_for_many(
            "select userid from admins "
        ))


class _Db:
    def __init__(self):
        self.params = config("config.ini", "postgresql")  # make params

    def execute_for_one(self, sql: str):
        with closing(psycopg2.connect(**self.params)) as conn:
            with conn.cursor() as cursor:
                log.debug('Execute query for one:\n {}'.format(sql))
                cursor.execute(sql)
                return cursor.fetchone()[0]

    def execute_for_many(self, sql: str):
        with closing(psycopg2.connect(**self.params)) as conn:
            with conn.cursor() as cursor:
                log.debug('Execute query for many:\n {}'.format(sql))
                cursor.execute(sql)
                return cursor.fetchall()

    def insert(self, sql: str, value: list):
        with closing(psycopg2.connect(**self.params)) as conn:
            with conn.cursor() as cursor:
                log.debug('Execute query insert:\n {}'.format(sql))
                cursor.execute(sql, value)
                conn.commit()
