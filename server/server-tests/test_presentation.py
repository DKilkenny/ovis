import unittest
import sys
import os.path
import json
import smtplib
from bson.json_util import dumps
from minimock import Mock
from tornado.testing import AsyncHTTPTestCase

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))
import main


class TestPresentationLayer(AsyncHTTPTestCase):
    def get_app(self):
        return main.get_app()

    def _connect_sellar_grouped(self):
        file_path = os.path.join(os.path.dirname(__file__),
                                 'sellar_grouped_py2.db')
        body = {'location': file_path}
        response = self.fetch('/connect', method='POST',
                              body=json.dumps(body))
        return response

    def test_connect(self):
        response = self._connect_sellar_grouped()
        self.assertEqual(response.code, 200)

    def test_logout(self):
        response = self.fetch('/logout')
        self.assertEqual(response.code, 200)

    def test_case_handler_get(self):
        response = self.fetch('/case')
        self.assertEqual(response.code, 400)

    def test_case_handler_post(self):
        response = self.fetch('/case', method='POST', body='{"token": 123}')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(body['case_id'], -1)

    def test_case_handler_del(self):
        response = self.fetch('/case', method='DELETE')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(body['status'], 'Failed')

    def test_case_handler_patch(self):
        response = self.fetch('/case', method='PATCH', body='{}')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(body['status'], 'Failed')

    def test_get_layout(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/layout')
        self.assertEqual(response.code, 200)
        self.assertIsNotNone(response.body)

    def test_driver_iteration_get(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/driver_iterations')
        self.assertEqual(response.code, 200)
        self.assertIsNotNone(response.body)

    def test_driver_iteration_get_var(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/driver_iterations/pz.z')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIsNotNone(response.body)
        self.assertEqual(len(body), 7)

    def test_driver_iteration_post(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/driver_iterations',
                              method='POST', body='{}')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')

    def test_driver_iteration_delete(self):
        self._connect_sellar_grouped()
        response = self.fetch(
            '/case/0/driver_iterations', method='DELETE')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')

    def test_driver_metadata_get(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/driver_metadata')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIsNotNone(response.body)
        self.assertEqual(len(body), 1)

    def test_driver_metadata_post(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/driver_metadata',
                              method='POST', body='{}')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')

    def test_driver_metadata_delete(self):
        self._connect_sellar_grouped()
        response = self.fetch(
            '/case/0/driver_metadata', method='DELETE')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')

    def test_global_iterations_get(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/global_iterations')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIsNotNone(response.body)

    def test_global_iterations_post(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/global_iterations',
                              method='POST', body='{}')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')

    def test_global_iterations_delete(self):
        self._connect_sellar_grouped()
        response = self.fetch(
            '/case/0/global_iterations', method='DELETE')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')

    def test_solver_iterations_get(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/solver_iterations')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIsNotNone(response.body)

    def test_solver_iterations_post(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/solver_iterations',
                              method='POST', body='{}')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')

    def test_solver_iterations_delete(self):
        self._connect_sellar_grouped()
        response = self.fetch(
            '/case/0/solver_iterations', method='DELETE')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')

    def test_solver_metadata_get(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/solver_metadata')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIsNotNone(response.body)

    def test_solver_metadata_post(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/solver_metadata',
                              method='POST', body='{}')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')

    def test_solver_metadata_delete(self):
        self._connect_sellar_grouped()
        response = self.fetch(
            '/case/0/solver_metadata', method='DELETE')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')

    def test_system_iteration_get(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/system_iterations')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIsNotNone(response.body)

    def test_system_iteration_post(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/system_iterations',
                              method='POST', body='{}')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')

    def test_system_iteration_delete(self):
        self._connect_sellar_grouped()
        response = self.fetch(
            '/case/0/system_iterations', method='DELETE')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')

    def test_system_metadata_get(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/system_metadata')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIsNotNone(response.body)

    def test_system_metadata_post(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/system_metadata',
                              method='POST', body='{}')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')

    def test_system_metadata_delete(self):
        self._connect_sellar_grouped()
        response = self.fetch(
            '/case/0/system_metadata', method='DELETE')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')

    def test_metadata_get(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/metadata')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIsNotNone(response.body)

    def test_metadata_post(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/metadata',
                              method='POST', body='{}')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')

    def test_metadata_delete(self):
        self._connect_sellar_grouped()
        response = self.fetch(
            '/case/0/metadata', method='DELETE')
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')

    def test_create_token(self):
        response = self.fetch('/token', method='POST',
                              body='{"name": "test", "email": "test@testcom"}')
        body = json.loads(response.body)
        self.assertEqual(body['status'], 'Failed')
        self.assertEqual(response.code, 200)

    def test_login(self):
        response = self.fetch('/login', method='POST', body='{"token":"123"}')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(body['status'], 'Failed')

    def test_get_desvars(self):
        self._connect_sellar_grouped()
        response = self.fetch('/case/0/allvars')
        body = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertIsNotNone(body)


def cleanup():
    pass


if __name__ == "__main__":
    try:
        unittest.main()
    except Exception as e:
        print("Error: " + str(e))
    finally:
        cleanup()
