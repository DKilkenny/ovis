import unittest
import sys
import os.path
import json
from bson.json_util import dumps
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from data_server.logic import logic
from data_server.shared import collections

token = logic.create_token('Unit Test', 'UnitTestLogic4@fake.com')

def cleanup():
    logic.delete_token(token)

class TestLogic(unittest.TestCase):
    
    def create_system_iteration(self):
        ret = {}
        ret['iteration_coordinate'] = 'it|1'
        ret['counter'] = 1
        ret['inputs'] = [{'name': 'var1'},]
        ret['outputs'] = [{'name': 'var2'}]
        ret['residuals'] = [{'name': 'var3'}]
        return ret

    def create_driver_iteration(self):
        ret = {}
        ret['iteration_coordinate'] = 'it|2'
        ret['counter'] = 1
        ret['desvars'] = [{'name': 'var1'}]
        ret['objectives'] = [{'name': 'var2'}]
        ret['constraints'] = [{'name': 'var3'}]
        return ret

    def test_create_token(self):
        self.assertNotEqual(token, -1)

    def test_create_case(self):
        body = {}
        case = logic.create_case(body, token)
        self.assertNotEqual(case, -1)

    def test_case_exists1(self):
        body = {}
        case = logic.create_case(body, token)
        case_obj = json.loads(logic.get_case_with_id(case['case_id'], token))
        self.assertEqual(case_obj['users'][0], token)

    def test_cleanup(self):
        new_token = logic.create_token('Unit Test Cleanup', 'blah@fake4.com')
        try:
            new_case = logic.create_case({}, new_token)
            self.assertEqual(logic.token_exists(new_token), True)
            self.assertNotEqual(logic.get_case_with_id(new_case['case_id'], new_token), {})
            logic.delete_token(new_token)
            self.assertEqual(logic.token_exists(new_token), False)
            self.assertEqual(logic.get_case_with_id(new_case['case_id'], new_token), {})
        finally:
            logic.delete_token(new_token)

    def test_delete_case(self):
        new_case = logic.create_case({}, token)
        self.assertNotEqual(logic.get_case_with_id(new_case['case_id'], token), {})
        logic.delete_case_with_id(new_case['case_id'], token)
        self.assertEqual(logic.get_case_with_id(new_case['case_id'], token), {})

    def test_get_all_cases_empty(self):
        new_token = logic.create_token('test cases empty', 'TestCasesEmpty@fake.com')
        try:
            self.assertEqual(logic.get_all_cases(new_token), [])
        finally:
            logic.delete_token(new_token)

    def test_get_all_cases_not_empty(self):
        new_token = logic.create_token('test cases not empty', 'TestCasesNotEmpty@fake.com')
        try:
            case1 = logic.create_case({}, new_token)
            case2 = logic.create_case({}, new_token)
            case3 = logic.create_case({}, new_token)
            self.assertEqual(len(logic.get_all_cases(new_token)), 3)
        finally:
            logic.delete_token(new_token)

    def test_get_case_with_id(self):
        new_case = logic.create_case({}, token)
        self.assertEqual(json.loads(logic.get_case_with_id(new_case['case_id'], token))['case_id'], new_case['case_id'])

    def test_get_case_with_id_no_token(self):
        new_case = logic.create_case({}, token)
        self.assertEqual(logic.get_case_with_id(new_case['case_id'], 'badToken'), {})

    def test_get_case_with_id_bad_token(self):
        new_token = logic.create_token('test get case with bad token', 'TestGetCaseBadToken@fake.com')
        try:
            new_case = logic.create_case({}, token)
            self.assertEqual(logic.get_case_with_id(new_case['case_id'], new_token), {})
        finally:
            logic.delete_token(new_token)

    def test_delete_case_with_id(self):
        new_case = logic.create_case({}, token)
        self.assertTrue(logic.delete_case_with_id(new_case['case_id'], token))

    def test_delete_case_no_token(self):
        new_case = logic.create_case({}, token)
        self.assertFalse(logic.delete_case_with_id(new_case['case_id'], 'bad token'))

    def test_delete_case_bad_token(self):
        new_token = logic.create_token('test delete with bad token', 'TestDeleteBadToken@fake.com')
        try:
            new_case = logic.create_case({}, token)
            self.assertFalse(logic.delete_case_with_id(new_case['case_id'], new_token))
        finally:
            logic.delete_token(new_token)

    def test_generic_create(self):
        new_case = logic.create_case({}, token)
        self.assertTrue(logic.generic_create(collections.DRIVER_ITERATIONS, {'test':1}, new_case['case_id'], token, 'False'))

    def test_generic_create2(self):
        new_case = logic.create_case({}, token)
        logic.generic_create(collections.DRIVER_ITERATIONS, {'test':1}, new_case['case_id'], token, 'False')
        driv_iter = json.loads(logic.generic_get(collections.DRIVER_ITERATIONS, new_case['case_id'], token, False))
        self.assertEqual(driv_iter['test'], 1)

    def test_update(self):
        new_case = logic.create_case({}, token)
        logic.generic_create(collections.DRIVER_ITERATIONS, {'test':1}, new_case['case_id'], token, 'False')
        logic.generic_create(collections.DRIVER_ITERATIONS, {'test':2}, new_case['case_id'], token, 'True')
        driv_iter = json.loads(logic.generic_get(collections.DRIVER_ITERATIONS, new_case['case_id'], token, False))
        self.assertEqual(driv_iter['test'], 2)        
    
    def test_generic_create_bad_token(self):
        new_case = logic.create_case({}, token)
        result = logic.generic_create(collections.DRIVER_ITERATIONS, {'test':1}, new_case['case_id'], 'bad token', 'False')
        self.assertFalse(result)

    def test_generic_get(self):
        new_case = logic.create_case({}, token)
        logic.generic_create(collections.DRIVER_ITERATIONS, {'test':True}, new_case['case_id'], token, 'False')
        driv_iter = json.loads(logic.generic_get(collections.DRIVER_ITERATIONS, new_case['case_id'], token, False))
        self.assertTrue(driv_iter['test'])

    def test_generic_get_bad_token(self):
        new_case = logic.create_case({}, token)
        logic.generic_create(collections.DRIVER_ITERATIONS, {'test':1}, new_case['case_id'], 'bad token', 'False')
        driv_iter = json.loads(logic.generic_get(collections.DRIVER_ITERATIONS, new_case['case_id'], 'bad token', False))
        self.assertEqual(driv_iter, None)

    def test_generic_delete(self):
        new_case = logic.create_case({}, token)
        logic.generic_create(collections.DRIVER_ITERATIONS, {'test':True}, new_case['case_id'], token, 'False')
        self.assertTrue(logic.generic_delete(collections.DRIVER_ITERATIONS, new_case['case_id'], token))

    def test_generic_delete2(self):
        new_case = logic.create_case({}, token)
        logic.generic_create(collections.DRIVER_ITERATIONS, {'test':True}, new_case['case_id'], token, 'False')
        logic.generic_delete(collections.DRIVER_ITERATIONS, new_case['case_id'], token)
        result = logic.generic_get(collections.DRIVER_ITERATIONS, new_case['case_id'], token)
        self.assertEqual(result, '[]')

    def test_delete_bad_token(self):
        new_case = logic.create_case({}, token)
        logic.generic_create(collections.DRIVER_ITERATIONS, {'test':True}, new_case['case_id'], token, 'False')
        self.assertFalse(logic.generic_delete(collections.DRIVER_ITERATIONS, new_case['case_id'], 'bad token'))

    def test_token_exists(self):
        self.assertTrue(logic.token_exists(token))

    def test_token_does_not_exist(self):
        self.assertFalse(logic.token_exists('bad token'))

    def test_empty_system_iteration_data(self):
        new_case = logic.create_case({}, token)
        self.assertEqual(logic.get_system_iteration_data(new_case['case_id'], 'test'), '[]')

    def test_empty_get_variables(self):
        new_case = logic.create_case({}, token)
        self.assertEqual(logic.get_variables(new_case['case_id']), '[]')

    def test_empty_get_driver_iteration(self):
        new_case = logic.create_case({}, token)
        self.assertEqual(logic.get_driver_iteration_data(new_case['case_id'], 'test'), '[]')

    def test_empty_get_desvars(self):
        new_case = logic.create_case({}, token)
        self.assertEqual(logic.get_desvars(new_case['case_id']), '[]')

    def test_get_system_iteration_data(self):
        new_case = logic.create_case({}, token)
        logic.generic_create(collections.SYSTEM_ITERATIONS, self.create_system_iteration(), new_case['case_id'], token, False)
        sys_data1 = json.loads(logic.get_system_iteration_data(new_case['case_id'], 'var1'))
        sys_data2 = json.loads(logic.get_system_iteration_data(new_case['case_id'], 'var2'))
        sys_data3 = json.loads(logic.get_system_iteration_data(new_case['case_id'], 'var3'))
        got_input = False
        got_output = False
        got_resid = False
        for i in sys_data1:
            if i['type'] == 'input':
                got_input = True
        for i in sys_data2:
            if i['type'] == 'output':
                got_output = True
        for i in sys_data3:
            if i['type'] == 'residual':
                got_resid = True
        self.assertTrue(got_input)
        self.assertTrue(got_output)
        self.assertTrue(got_resid)
        self.assertEqual(sys_data1[0]['name'], 'var1')
        self.assertEqual(sys_data2[0]['name'], 'var2')
        self.assertEqual(sys_data3[0]['name'], 'var3')

    def test_get_driver_iteration_data(self):
        new_case = logic.create_case({}, token)
        logic.generic_create(collections.DRIVER_ITERATIONS, self.create_driver_iteration(), new_case['case_id'], token, False)
        sys_data1 = json.loads(logic.get_driver_iteration_data(new_case['case_id'], 'var1'))
        sys_data2 = json.loads(logic.get_driver_iteration_data(new_case['case_id'], 'var2'))
        sys_data3 = json.loads(logic.get_driver_iteration_data(new_case['case_id'], 'var3'))
        got_desvars = False
        got_objectives = False
        got_constraints = False
        for i in sys_data1:
            if i['type'] == 'desvar':
                got_desvars = True
        for i in sys_data2:
            if i['type'] == 'objective':
                got_objectives = True
        for i in sys_data3:
            if i['type'] == 'constraint':
                got_constraints = True
        self.assertTrue(got_desvars)
        self.assertTrue(got_objectives)
        self.assertTrue(got_constraints)
        self.assertEqual(sys_data1[0]['name'], 'var1')
        self.assertEqual(sys_data2[0]['name'], 'var2')
        self.assertEqual(sys_data3[0]['name'], 'var3')

    def test_get_variables(self):
        new_case = logic.create_case({}, token)
        logic.generic_create(collections.SYSTEM_ITERATIONS, self.create_system_iteration(), new_case['case_id'], token, False)
        variables = json.loads(logic.get_variables(new_case['case_id']))
        got_var1 = False
        got_var2 = False
        for i in variables:
            if i == 'var1':
                got_var1 = True
            elif i == 'var2':
                got_var2 = True
        self.assertTrue(got_var1)
        self.assertTrue(got_var2)

    def test_get_desvars(self):
        new_case = logic.create_case({}, token)
        logic.generic_create(collections.DRIVER_ITERATIONS, self.create_driver_iteration(), new_case['case_id'], token, False)
        variables = json.loads(logic.get_desvars(new_case['case_id']))
        got_var1 = False
        got_var2 = False
        got_var3 = False
        for i in variables:
            if i == 'var1':
                got_var1 = True
            elif i == 'var2':
                got_var2 = True
            elif i == 'var3':
                got_var3 = True
        self.assertTrue(got_var1)
        self.assertTrue(got_var2)
        self.assertTrue(got_var3)

if __name__ == "__main__":
    try:
        unittest.main()
    finally:
        cleanup()
