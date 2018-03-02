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
        """
        if self.connection is not None:
            self.connection.close()
        self.connection = None

    def connect(self, location):
        """ connect method

        Creates the connection to the SQLite DB.
        """
        self.filename = location

        if not self.is_valid_sqlite3_db(location):
            return False

        if self.connection is not None:
            self.connection.close()

        self.connection = sqlite3.connect(self.filename)
        with self.connection:
            self.cursor = self.connection.cursor()
            self.cursor.execute("create table if not exists layouts\
                                 (id integer PRIMARY KEY, layout text)")

        return True

    def update_layout(self, body, case_id):
        """ update_layout method

        Updates the layout for a given case. Creates new layout if
        one does not already exist.abs

        Args:
            body (JSON): the body of the POST request
            case_id (string): the case to be updated
        Returns:
            True if success, False otherwies
        """
        with self.connection:
            self.cursor = self.connection.cursor()
            self.cursor.execute("INSERT OR REPLACE INTO layouts VALUES (?,?)",
                                (0, json.dumps(body)))

        return True

    def generic_get(self, collection_name, case_id='',
                    token='', get_many=True):
        """ generic_get method

        Performs a generic 'get' request, which attempts to query and return
        all documents with the given case_id from the given collection.

        Args:
            collection_name (string): the collection to query
            case_id (string || int): ID to be used for querying
            token (string): the token to be used for authentication
            get_many (bool): whether you should query to get one or all
                             instances
        Returns:
            JSON array of documents returned from the query
        """
        if collection_name is collections.DRIVER_ITERATIONS:
            return self._get_driver_iterations()
        elif collection_name is collections.DRIVER_METADATA:
            return self._get_driver_metadata()
        elif collection_name is collections.LAYOUTS:
            return self._get_layout()
        else:
            return []

    def get_driver_iteration_data(self, case_id):
        """ get_driver_iteration_data method

        Grabs all data for all driver iterations for a given case

        Args:
            case_id (string): the case to use for querying
        Returns:
            Array of data
        """
        return self._get_driver_iterations()

    def is_new_data(self, case_id, count):
        """ is_new_data method

        Determines if there's new data based on the count

        Args:
            case_id (string): the case to use for querying
            count (int): the current max counter value
        Returns:
            True if new data is available, False otherwise
        """
        rows = None

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

        TODO: move this to a util file?
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

    def _get_driver_iterations(self):
        """ _get_driver_iterations method

        Grabs all of the driver iterations in the current DB and returns
        them as JSON.

        Returns
        -------
        [JSON] :
            the list of all driver iterations as JSON
        """
        if self.connection is None:
            return []

        ret = []
        with self.connection:
            self.cursor = self.connection.cursor()
            self.cursor.execute(
                "SELECT iteration_coordinate, timestamp, success, msg, desvars,\
                 responses, objectives, constraints, sysincludes, counter\
                 FROM driver_iterations")
            rows = self.cursor.fetchall()

            for row in rows:
                n_row = {}
                n_row['iteration_coordinate'] = row[0]
                n_row['timestamp'] = row[1]
                n_row['success'] = row[2]
                n_row['msg'] = row[3]
                n_row['desvars'] = self.blob_to_array(row[4])
                n_row['responses'] = self.blob_to_array(row[5])
                n_row['objectives'] = self.blob_to_array(row[6])
                n_row['constraints'] = self.blob_to_array(row[7])
                n_row['sysincludes'] = self.blob_to_array(row[8])
                n_row['counter'] = row[9]

                ret.append(n_row)

        final_ret = []
        for data in ret:
            desvars_array = []
            responses_array = []
            objectives_array = []
            constraints_array = []
            sysincludes_array = []
            if data['desvars']:
                for name in data['desvars'].dtype.names:
                    desvars_array.append({
                        'name': name,
                        'values': self.convert_to_list(data['desvars'][name])
                    })

            if data['responses']:
                for name in data['responses'].dtype.names:
                    responses_array.append({
                        'name': name,
                        'values': self.convert_to_list(data['responses'][name])
                    })

            if data['objectives']:
                for name in data['objectives'].dtype.names:
                    objectives_array.append({
                        'name': name,
                        'values': self.convert_to_list(
                            data['objectives'][name])
                    })

            if data['constraints']:
                for name in data['constraints'].dtype.names:
                    constraints_array.append({
                        'name': name,
                        'values': self.convert_to_list(
                            data['constraints'][name])
                    })

            if data['sysincludes']:
                for name in data['sysincludes'].dtype.names:
                    sysincludes_array.append({
                        'name': name,
                        'values': self.convert_to_list(
                            data['sysincludes'][name])
                    })

            final_ret.append({
                'iteration_coordinate': data['iteration_coordinate'],
                'timestamp': data['timestamp'],
                'success': data['success'],
                'msg': data['msg'],
                'counter': data['counter'],
                "desvars": [] if len(desvars_array) is 0
                else desvars_array,
                "responses": [] if len(responses_array) is 0
                else responses_array,
                "objectives": [] if len(objectives_array) is 0
                else objectives_array,
                "constraints": [] if len(constraints_array) is 0
                else constraints_array,
                "sysincludes": [] if len(sysincludes_array) is 0
                else sysincludes_array
            })

        return final_ret

    def _get_driver_metadata(self):
        """ _get_driver_metadata(self):

        returns the driver metadata as JSON

        Returns
        -------
        String :
            The JSON driver metadata
        """
        ret = {}
        with self.connection:
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT model_viewer_data\
                                 FROM driver_metadata")
            row = self.cursor.fetchone()
            if row is None:
                return []

            ret = self.blob_to_array(row[0])

        return json.dumps([{'model_viewer_data': ret}])

    def _get_layout(self):
        """ _get_layout method

        returns the layout as JSON, if one exists

        Returns
        -------
        JSON :
            the layout for this case if one exists, [] otherwise
        """
        ret = []
        with self.connection:
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT layout FROM layouts WHERE id=0")
            row = self.cursor.fetchone()
            if row is None:
                ret = []
            else:
                ret = json.dumps([json.loads(row[0])])

        return ret
