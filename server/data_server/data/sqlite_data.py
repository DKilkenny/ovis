import sqlite3
import os
import json
import io
import numpy as np
from six import PY2, PY3, iteritems
from data_server.data.data import BaseData
import data_server.shared.collection_names as collections

if PY2:
    import cPickle as pickle
if PY3:
    import pickle


class SqliteData(BaseData):
    """ SqliteData class

    Class that manages the SQLite connection. Can query, insert and delete
    in any table.
    """

    def __init__(self):
        """ init method

        Initialize.
        """
        super(SqliteData, self).__init__()
        self.connection = None
        self.filename = ''

    def __del__(self):
        """ del method

        Closes the DB connection if it is still open
        """
        self.disconnect()

    def disconnect(self):
        """ disconnect method

        Closes the DB connection if it is still open

        Returns:
            bool: True if success, False otherwise
        """
        if self.connection is not None:
            self.connection.close()
        self.connection = None
        return True

    def connect(self, location):
        """ connect method

        Creates the connection to the SQLite DB.
        """
        self.filename = location

        if not self.is_valid_sqlite3_db(location):
            return False

        if self.connection is not None:
            self.disconnect()

        self.connection = sqlite3.connect(self.filename)
        with self.connection:
            self.cursor = self.connection.cursor()
            self.cursor.execute("create table if not exists layouts\
                                 (id integer PRIMARY KEY, layout text)")

            self.cursor.execute(
                "SELECT abs2prom, prom2abs, abs2meta FROM metadata")
            row = self.cursor.fetchone()

            if PY2:
                self.abs2prom = pickle.loads(
                    str(row[0])) if row[0] is not None else None
                self.prom2abs = pickle.loads(
                    str(row[1])) if row[1] is not None else None
                self.abs2meta = pickle.loads(
                    str(row[2])) if row[2] is not None else None
            if PY3:
                try:
                    self.abs2prom = pickle.loads(
                        row[0]) if row[0] is not None else None
                    self.prom2abs = pickle.loads(
                        row[1]) if row[1] is not None else None
                    self.abs2meta = pickle.loads(
                        row[2]) if row[2] is not None else None
                except: # case where this DB was generated with python 2
                    self.abs2prom = pickle.loads(
                        bytes(row[0], 'utf-8')) if row[0] is not None else None
                    self.prom2abs = pickle.loads(
                        bytes(row[1], 'utf-8')) if row[1] is not None else None
                    self.abs2meta = pickle.loads(
                        bytes(row[2], 'utf-8')) if row[2] is not None else None

        return True

    def update_layout(self, body):
        """ update_layout method

        Updates the layout for a given case. Creates new layout if
        one does not already exist.

        Args:
            body (string): the layout as a JSON string
        Returns:
            True if success, False otherwies
        """
        if self.connection is None:
            return False

        with self.connection:
            self.cursor = self.connection.cursor()
            self.cursor.execute("INSERT OR REPLACE INTO layouts VALUES (?,?)",
                                (0, body))

        return True

    def generic_get(self, collection_name, get_many=True):
        """ generic_get method

        Performs a generic 'get' request, which attempts to query and return
        all documents from the given collection.

        Args:
            collection_name (string): the collection to query
            get_many (bool): whether you should query to get one or all
                             instances
        Returns:
            JSON array of documents returned from the query
        """
        if collection_name is collections.DRIVER_ITERATIONS:
            return self._get_driver_iterations(get_many)
        elif collection_name is collections.DRIVER_METADATA:
            return self._get_driver_metadata()
        elif collection_name is collections.LAYOUTS:
            return self._get_layout()
        elif collection_name is collections.METADATA:
            return self._get_metadata()
        else:
            return []

    def get_driver_iteration_data(self):
        """ get_driver_iteration_data method

        Grabs all data for all driver iterations for a given case

        Returns:
            Array of data
        """
        return self._get_driver_iterations()

    def is_new_data(self, count):
        """ is_new_data method

        Determines if there's new data based on the count

        Args:
            count (int): the current max counter value
        Returns:
            True if new data is available, False otherwise
        """
        rows = None

        if self.connection is None:
            return False

        with self.connection:
            self.cursor = self.connection.cursor()
            self.cursor.execute(
                "SELECT counter FROM driver_iterations WHERE counter > " +
                str(count))
            rows = self.cursor.fetchall()

        if len(rows) > 0:
            return True
        return False

    def is_valid_sqlite3_db(self, filename):
        """
        Return true if the given filename contains a valid SQLite3
        database file.

        Parameters
        ----------
        filename : str
            The path to the file to be tested

        Returns
        -------
        bool :
            True if the filename specifies a valid SQLite3 database.
        """
        if not os.path.isfile(filename):
            return False
        if os.path.getsize(filename) < 100:
            # SQLite database file header is 100 bytes
            return False

        with open(filename, 'rb') as fd:
            header = fd.read(100)

        return header[:16] == b'SQLite format 3\x00'

    def blob_to_array(self, blob):
        """
        Convert sqlite BLOB to numpy array.
        """
        out = io.BytesIO(blob)
        out.seek(0)
        return np.load(out)

    def convert_to_list(self, obj):
        """
        Convert object to list (so that it may be sent as JSON).

        Parameters
        ----------
        obj <Object>
            the object to be converted to a list
        """
        if isinstance(obj, np.ndarray):
            return self.convert_to_list(obj.tolist())
        elif isinstance(obj, (list, tuple)):
            return [self.convert_to_list(item) for item in obj]
        elif obj is None:
            return []
        else:
            return obj

    def _get_driver_iterations(self, get_many=True):
        """ _get_driver_iterations method

        Grabs all of the driver iterations in the current DB and returns
        them as JSON.

        Args:
        -----
        get_many (bool): if True, grabs all, otherwise grabs first

        Returns
        -------
        [JSON] :
            the list of all driver iterations as JSON
        """
        ret = []

        if self.connection is None:
            return []

        with self.connection:
            self.cursor = self.connection.cursor()
            self.cursor.execute(
                "SELECT iteration_coordinate, timestamp, success, msg, \
                 inputs, outputs, counter FROM driver_iterations")
            rows = self.cursor.fetchall()

            # format the rows so we can use them most easily
            for row in rows:
                n_row = {}
                n_row['iteration_coordinate'] = row[0]
                n_row['timestamp'] = row[1]
                n_row['success'] = row[2]
                n_row['msg'] = row[3]
                n_row['inputs'] = self.blob_to_array(row[4])
                n_row['outputs'] = self.blob_to_array(row[5])
                n_row['counter'] = row[6]

                ret.append(n_row)

        # gather desvars, objectives, constraints, sysincludes, and inputs
        final_ret = []
        for data in ret:
            desvars_array = []
            objectives_array = []
            constraints_array = []
            sysincludes_array = []
            inputs_array = []
            for name in data['outputs'].dtype.names:
                types = self.abs2meta[name]['type']

                if 'desvar' in types:
                    desvars_array.append({
                        'name': name,
                        'values': self.convert_to_list(data['outputs'][name])[0]
                    })
                elif 'objective' in types:
                    objectives_array.append({
                        'name': name,
                        'values': self.convert_to_list(data['outputs'][name])[0]
                    })
                elif 'constraint' in types:
                    constraints_array.append({
                        'name': name,
                        'values': self.convert_to_list(data['outputs'][name])[0]
                    })
                else:
                    sysincludes_array.append({
                        'name': name,
                        'values': self.convert_to_list(data['outputs'][name])[0]
                    })

            for name in data['inputs'].dtype.names:
                inputs_array.append({
                    'name': name,
                    'values': self.convert_to_list(data['inputs'][name])[0]
                })

            final_ret.append({
                'iteration_coordinate': data['iteration_coordinate'],
                'timestamp': data['timestamp'],
                'success': data['success'],
                'msg': data['msg'],
                'counter': data['counter'],
                "desvars": [] if len(desvars_array) is 0
                else desvars_array,
                "objectives": [] if len(objectives_array) is 0
                else objectives_array,
                "constraints": [] if len(constraints_array) is 0
                else constraints_array,
                "sysincludes": [] if len(sysincludes_array) is 0
                else sysincludes_array,
                "inputs": [] if len(inputs_array) is 0 else inputs_array
            })

        if get_many:
            return final_ret
        elif len(final_ret) > 0:
            return [final_ret[0]]
        else:
            return []

    def _get_driver_metadata(self):
        """ _get_driver_metadata(self):

        returns the driver metadata as JSON

        Returns
        -------
        JSON :
            The JSON driver metadata
        """
        ret = {}

        if self.connection is None:
            return {}

        with self.connection:
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT model_viewer_data\
                                 FROM driver_metadata")
            row = self.cursor.fetchone()
            if row is None:
                return {}

            ret = self.blob_to_array(row[0])

        return [{'model_viewer_data': ret}]

    def _get_metadata(self):
        """ _get_metadata

        returns the stored metadata

        Returns
        -------
        Dictionary :
            Dictionary storing abs2prom and prom2abs
        """
        ret = {
            'abs2prom': {},
            'prom2abs': {},
        }
        
        if self.connection is None:
            return {}

        with self.connection:
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT abs2prom, prom2abs FROM metadata")
            row = self.cursor.fetchone()
            if row is None:
                return ret
            if PY2:
                ret['abs2prom'] = pickle.loads(
                    str(row[0])) if row[0] is not None else None
                ret['prom2abs'] = pickle.loads(
                    str(row[1])) if row[1] is not None else None
            if PY3:
                try:
                    ret['abs2prom'] = pickle.loads(
                        row[0]) if row[0] is not None else None
                    ret['prom2abs'] = pickle.loads(
                        row[1]) if row[1] is not None else None
                except:
                    ret['abs2prom'] = pickle.loads(
                        bytes(row[0], 'utf-8')) if row[0] is not None else None
                    ret['prom2abs'] = pickle.loads(
                        bytes(row[1], 'utf-8')) if row[1] is not None else None

        return ret

    def _get_layout(self):
        """ _get_layout method

        returns the layout as JSON, if one exists

        Returns
        -------
        JSON :
            the layout for this case if one exists, [] otherwise
        """
        ret = None

        if self.connection is None:
            return []

        with self.connection:
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT layout FROM layouts WHERE id=0")
            row = self.cursor.fetchone()
            if row is None:
                ret = []
            else:
                ret = [json.loads(row[0])]

        return ret
