# -*- coding: utf-8 -*-
# Copyright (c) 2018, Christiaan Frans Rademan and David Kruger.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTI-
# TUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUP-
# TION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY,OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

from pymysql import *
from luxon.utils.timer import Timer
from luxon.utils.filter import filter_none_text
from luxon import GetLogger

log = GetLogger(__name__)


def _log(db, msg, elapsed=0):
    """Debug Log Function

    Function to log in the case where debugging
    is enabled.

    Args:
        db (object): MysqlConnect connection object.
        msg (str): Log message.
        elapsed (float): Time elapsed.
    """
    if log.debug_mode():
        log_msg = (msg +
                   " (DURATION: %.4fs) (%s,%s,%s)" %
                   (elapsed,
                    db.get_server_info(),
                    db.get_host_info(),
                    db.thread_id,
                    ))
        if elapsed > 0.1:
            log_msg = "!SLOW! " + log_msg
        log.debug(log_msg)


def _log_query(query=None, params=None):
    """Parse query to log.

    Returns SQL Query (string)
    """
    parsed = []

    if params is not None:
        for param in params:
            if isinstance(param, int) or isinstance(param, float):
                parsed.append(param)
            else:
                parsed.append('\'' + filter_none_text(param) + '\'')
    try:
        log_query = query % tuple(parsed)
    except Exception:
        log_query = query

    return log_query


def _parsed_params(params):
    """Parse SQL paramters provided to query.

    Returns list of values.
    """
    parsed = []
    if params is not None:
        for param in params:
            if isinstance(param, bool):
                # Modify python bool to 0/1 integer.
                # Mysql has no bool field.
                if param is True:
                    parsed.append(1)
                else:
                    parsed.append(0)
                    # MYSQL cannot store timezone information in datetime field
                    # Its therefor recommended to use the:
                    #    tachyonic.neutrino.dt.datetime() singleton.
                    # christiaan.rademan@gmail.com
                    # elif isinstance(param, datetime.datatime):
                    # Store as UTC_TIME if datetime
            # parsed.append(str(utc_time(param)))
            else:
                parsed.append(param)
    return parsed


def _parsed_results(results):
    """Parse results returned by SQL Query.

    Returns list of rows.
    """
    # Since the database connection timezone is set to +00:00
    # all functions such as now() etc will store in UTC/GMT time.
    # For datatime objects sent as params it will be converted to UTC
    # Its therefor not neccessary to parse datatime. However this code
    # is here for any other results that may require paring in future.
    # christiaan.rademan@gmail.com.
    # for result in results:
    #    for field in result:
    #        if isinstance(result[field], datetime.datetime):
    #            # Format Date time to UTC Time.
    #            result[field] = utc_time(result[field])
    return results


class MysqlCursor(cursors.Cursor):
    """Child class of pymysql.connect.cursor.

    Overwrites the execute() method to log Query time,
    and return the query results when executed.

    Args:
        conn (obj): MysqlConnect connection object.
    """
    def __init(self, conn):
        super().__init__(conn)

    def _execute(self, db, query, params=None):
        """Execute SQL Query.

        Also parses results and logs query time if required.

        Args:
            db (obj): MysqlConnect object.
            query (str): SQL Query String.
            params (list):  Query values as per query string.

        Returns:
            List of parsed results.
        """
        with Timer() as elapsed:
            log_query = _log_query(query, params)
            parsed = _parsed_params(params)

            try:
                super().execute(query, parsed)
            except IntegrityError:
                log.error("Query %s" % log_query)
                raise
            except ProgrammingError:
                log.error("Query %s" % log_query)
                raise

            # This command increases self.rownumber
            result = super().fetchall()
            # So in case someone wants to iterate over the
            # object, we set it back to 0
            self.rownumber = 0

            _log(db, "Query %s" % log_query, elapsed())

            # Returning the results for backward
            # compatibility with neutrino.

            return _parsed_results(result)

    def execute(self, query, args=None):
        """Execute SQL Query.

        Turns args into list if it isn't.

        Args:
            query (str): SQL Query String.
            args (int, str or tuple): Query values as per query string.

        Returns:
            Parsed Results list containing dictionaries with
            field values per row.
        """
        if isinstance(args, tuple):
            # Convert params to list if tuple.
            args = list(args)
        elif not isinstance(args, list):
            if args is not None:
                args = [ args ]

        result = self._execute(self.connection, query, args)
        self.connection._uncommited = True

        return result


class MysqlConnect(connections.Connection):
    """Mysql Connection Class.

    Child class of pymysql.connect.

    Overwrites some of the methods for added functionality.

    Args:
        host (str): Host where the database server is located.
        username (str): Username to log in as.
        password (str):Password to use.
        database (str): Database to use, None to not use a particular
                        one.
    """
    def __init__(self, host, username, password, database):
        with Timer() as elapsed:
            if log.debug_mode():
                log.debug("Connecting Database Connection" +
                          " (server=%s,username=%s,database=%s)" %
                          (host, username,
                           database))

            self.crsr = MysqlCursor(self)
            self._uncommitted = False
            self.utc_tz = False
            self.locks = False

            super().__init__(host=host,
                             user=username,
                             passwd=password,
                             db=database,
                             use_unicode=True,
                             charset='utf8',
                             autocommit=False)

            if log.debug_mode():
                log.debug("Connected Database Connection" +
                          " (server=%s,username=%s,database=%s,%s,%s,%s)" %
                          (host,
                           username,
                           database,
                           self.get_server_info(),
                           self.get_host_info(),
                           self.thread_id) +
                          " (DURATION: %s)" % (elapsed()))

    def clean_up(self):
        """Cleanup server Session.

        Autocommit neccessary for next request to start new transactions.
        If not applied select queries will return cached results

        Pool runs this method to ensure new requests start up in clean state.
        """
        try:
            if self.locks is True:
                self.unlock()
            if self._uncommited is True:
                self.rollback()
                self.commit()
        except OperationalError as e:
            log.error(e)

    def close(self):
        """Close the connection now.

        (rather than whenever .__del__() is called)
        As per PEP-0249

        """
        with Timer() as elapsed:
            super().close()
            _log(self, "Mysql database closed", elapsed())

    def commit(self):
        """Commit Transactionl Queries.

        If the database and the tables support transactions, this commits the
        current transaction; otherwise this method successfully does nothing.
        """
        if self._uncommited is True:
            with Timer() as elapsed:
                super().commit()
                _log(self, "Commit", elapsed())

            self._uncommited = False

    def cursor(self, cursor=None):
        """Method cursor

        Return a cursor to execute queries with

        Args:
            cursor (obj): Cursor object.

        Returns:
            cursor object.
        """
        if cursor:
            return cursor(self)

        return self.crsr

    def execute(self, query=None, params=None):
        """Execute SQL Query.

        This is left here for backward compatibility with neutrino,
        which had the execute method on the connection object.

        Args:
            query (str): SQL Query String.
            params (list): Query values as per query string.

        Returns:
            Parsed Results list containing dictionaries
            with field values per row.
        """
        return self.crsr.execute(query, params)

    def fields(self, table):
        """Return table columns.

        Args:
            table (str): Database table.

        Returns a list of columns on specified sql table.
        """
        fields = {}
        result = self.crsr.execute("DESCRIBE %s" % (table,))
        for f in result:
            name = f['Field']
            fields[name] = f
        return fields

    def last_row_id(self):
        """Return last row id.

        This method returns the value generated for an AUTO_INCREMENT
        column by the previous INSERT or UPDATE statement or None
        is no column available or rather AUTO_INCREMENT not used.
        """
        return self.crsr.lastrowid

    def last_row_count(self):
        """Return last row count.

        This method returns the number of rows returned for SELECT statements,
        or the number of rows affected by DML statements such as INSERT
        or UPDATE.
        """

        return self.crsr.rowcount

    def lock(self, table, write=True):
        """Lock specified table.

        MySQL enables client sessions to acquire table locks explicitly for the
        purpose of cooperating with other sessions for access to tables, or to
        prevent other sessions from modifying tables during periods when a
        session requires exclusive access to them. A session can acquire or
        release locks only for itself. One session cannot acquire locks for
        another session or release locks held by another session.

        LOCK TABLES implicitly releases any table locks held by the current
        session before acquiring new locks.

        Args:
            table (str): Database table.
            write (bool):
                * False: The session that holds the lock can read the table
                    (but not write it). Multiple sessions can acquire a READ
                    for the table at the same time. Other sessions can read the
                    the table without explicitly acquiring a READ lock.
                * True: The session that holds the lock can read and write the
                    table. Only the session that holds the lock can access the
                    table. No other session can access it until the lock is
                    released. Lock requests for the table by other sessions
                    block while the WRITE lock is held.
        """
        if write is True:
            lock = "WRITE"
        else:
            lock = "READ"
        query = "LOCK TABLES %s %s" % (table, lock)
        self.crsr.execute(query)
        self.locks = True

    def ping(self):
        """Check if the server is alive.

        Auto-Reconnect if not, and return false when reconnecting.
        """
        if self._sock is None:
            super().ping()
            return False
        else:
            try:
                super().ping()
                return True
            except Exception:
                self.__init__(self.host, self.user,
                              self.password, self.database)
                return False

    def pool_once(self):
        """Ping and set connection/session to UTC timezone.

        UTC specifically for SQL query based functions such as now().
        """
        if self.ping() is False or self.utc_tz is False:
            self.crsr.execute('SET time_zone = %s', '+00:00')
            self.utc_tz = True

    def rollback(self):
        """Rollback Transactional Queries

        If the database and tables support transactions, this rolls back
        (cancels) the current transaction;
        otherwise a NotSupportedError is raised.
        """
        if self._uncommited is True:
            with Timer() as elapsed:
                super().rollback()
                _log(self, "Rollback", elapsed())

    def unlock(self):
        """Unlock tables.

        UNLOCK TABLES explicitly releases any table locks held by the current
        session.
        """
        query = "UNLOCK TABLES"
        self.crsr.execute(query)
        self.locks = False


def connect(*args, **kwargs):
    """Function connect.

    Provides the ability to return a mysql connection
    object by running mysql.connect(), exactly like
    pymysql.connect()

    Returns:
        MysqlConnect object.
    """
    return MysqlConnect(*args, **kwargs)
