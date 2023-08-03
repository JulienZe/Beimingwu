
import unittest
from scripts import main
import multiprocessing
import context
from context import config as C
import requests
import os
import shutil
from tests import common_test_operations as testops
import time


class TestAuth(unittest.TestCase):

    def setUpClass() -> None:
        unittest.TestCase.setUpClass()
        TestAuth.server_process = multiprocessing.Process(target=main.main)
        TestAuth.server_process.start()
        testops.wait_port_open(C.listen_port, 10)
        context.init_database()
        testops.clear_db()

    def tearDownClass() -> None:
        unittest.TestCase.tearDownClass()
        TestAuth.server_process.kill()

    def test_01_login(self):
        # first we need register a user
        result = testops.url_request(
            'auth/register', 
            {'username': 'test', 'password': 'test', "email": "test@localhost"})

        self.assertEqual(result['code'], 0)

        # then we need login
        result = testops.url_request(
            'auth/login',
            {'email': 'test@localhost', 'password': 'test'})
        
        self.assertEqual(result['code'], 0)

        token = result['data']['token']
        headers = {'Authorization': f'Bearer {token}'}

        result = testops.url_request(
            'auth/get_role',
            {},
            headers=headers)
        
        self.assertEqual(result['code'], 0)
        self.assertEqual(result['data']['role'], 0)
        
        result = testops.url_request(
            'auth/logout',
            {},
            headers=headers)
        
        self.assertEqual(result['code'], 0)

        # logout

        pass

    def test_02_login_by_token(self):

        result = testops.url_request(
            'auth/login',
            {'email': 'test@localhost', 'password': 'test'})
        

        token = result['data']['token']
        headers = {'Authorization': f'Bearer {token}'}

        result = testops.url_request(
            'user/create_token',
            {},
            headers=headers)
        
        token = result['data']['token']

        testops.url_request(
            'auth/logout',
            {},
            headers=headers)
        
        result = testops.url_request(
            'auth/login_by_token',
            {'email': 'test@localhost', 'token': token})
        
        self.assertEqual(result['code'], 0)
        self.assertIsNotNone(result['data']['token'])

        pass

    def test_login_required(self):
        response = testops.url_request(
            'auth/logout',
            {}, return_response=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 11)
        pass

if __name__ == '__main__':
    unittest.main()

