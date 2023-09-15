
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
import json
import zipfile
import tempfile


class TestEngine(unittest.TestCase):

    def setUpClass() -> None:
        unittest.TestCase.setUpClass()
        TestEngine.server_process = multiprocessing.Process(target=main.main)
        TestEngine.server_process.start()
        testops.wait_port_open(C.listen_port, 10)
        context.init_database()
        testops.clear_db()
        testops.url_request(
            'auth/register', 
            {'username': 'test', 'password': 'test', "email": "test@localhost", "confirm_email": False})
        TestEngine.learnware_id = testops.add_test_learnware('test@localhost', 'test')

    def tearDownClass() -> None:
        unittest.TestCase.tearDownClass()
        headers = testops.login('test@localhost', 'test')
        testops.delete_learnware(TestEngine.learnware_id, headers)
        TestEngine.server_process.kill()
        pass

    
    def login(self):
        return testops.login('test@localhost', 'test')


    def test_semantic_specification(self):
        headers = self.login()
        result = testops.url_request(
            'engine/semantic_specification', 
            {}, headers=headers, method='get')

        self.assertEqual(result['code'], 0)
        
        pass

    def test_search_learnware(self):
        headers = self.login()
        sematic_specification = testops.test_learnware_semantic_specification()

        test_learnware_path = os.path.join('tests', 'data', 'test_learnware.zip')

        with tempfile.TemporaryDirectory() as tempdir:
            with zipfile.ZipFile(test_learnware_path, 'r') as zip_ref:
                zip_ref.extract('stat.json', tempdir)
                pass
        
            stat_file = open(os.path.join(tempdir, 'stat.json'), 'rb')
            result = testops.url_request(
                'engine/search_learnware', 
                {'semantic_specification': json.dumps(sematic_specification)}, 
                files={'statistical_specification': stat_file},
                headers=headers)
        
            stat_file.close()
            pass

        print(result)
        self.assertEqual(result['code'], 0)
        print(list(result['data']['learnware_list_single'][0].keys()))
        self.assertGreaterEqual(len(result['data']['learnware_list_single']), 1)
        self.assertIn(TestEngine.learnware_id, [x['learnware_id'] for x in result['data']['learnware_list_single']])
        self.assertGreater(result['data']['learnware_list_single'][0]['last_modify'], '2020-01-01 00:00:00')
        pass

    def test_search_learnware_use_name(self):
        headers = self.login()
        sematic_specification = testops.test_learnware_semantic_specification()

        sematic_specification["Name"]["Values"] = "Test"
        result = testops.url_request(
            'engine/search_learnware', 
            data = {'semantic_specification': json.dumps(sematic_specification)}, 
            headers=headers)
        
        self.assertEqual(result['code'], 0)
        self.assertGreaterEqual(len(result['data']['learnware_list_single']), 1)
        self.assertIn(TestEngine.learnware_id, [x['learnware_id'] for x in result['data']['learnware_list_single']])
        self.assertGreater(result['data']['learnware_list_single'][0]['last_modify'], '2020-01-01 00:00:00')

        sematic_specification["Name"]["Values"] = "Testx"
        result = testops.url_request(
            'engine/search_learnware',
            data = {'semantic_specification': json.dumps(sematic_specification)},
            headers=headers)
        self.assertEqual(result['code'], 0)
        self.assertEqual(len(result['data']['learnware_list_single']), 0)
        pass

    def test_download_learnware(self):
        headers = self.login()
        result = testops.url_request(
            'engine/download_learnware', 
            {'learnware_id': TestEngine.learnware_id}, 
            headers=headers, method='get', return_response=True)
        
        downloaded_filename = os.path.join('tests', 'data', 'download_learnware.zip')
        with open(downloaded_filename, 'wb') as f:
            f.write(result.content)
            pass

        learnware_filename = os.path.join('tests', 'data', 'test_learnware.zip')
        self.assertEqual(
            os.path.getsize(downloaded_filename),
            os.path.getsize(learnware_filename)
        )

        os.remove(downloaded_filename)
        pass

    def test_download_learnware_unverified(self):
        learnware_id = testops.add_test_learnware_unverified('test@localhost', 'test', 'test_learnware.zip')
        headers = self.login()
        result = testops.url_request(
            'engine/download_learnware', 
            {'learnware_id': learnware_id}, 
            headers=headers, method='get', return_response=True)
        
        downloaded_filename = os.path.join('tests', 'data', 'download_learnware.zip')
        with open(downloaded_filename, 'wb') as f:
            f.write(result.content)
            pass

        learnware_filename = os.path.join('tests', 'data', 'test_learnware.zip')
        self.assertEqual(
            os.path.getsize(downloaded_filename),
            os.path.getsize(learnware_filename)
        )

        os.remove(downloaded_filename)
        pass

    def test_learnware_info(self):
        headers = self.login()

        result = testops.url_request(
            'engine/learnware_info', 
            {'learnware_id': TestEngine.learnware_id}, 
            headers=headers, method='get')
        
        self.assertEqual(result['code'], 0)

        self.assertEqual(
            result['data']['learnware_info']['semantic_specification']['Name'],
            testops.test_learnware_semantic_specification()['Name']
        )
        self.assertGreater(
            result['data']['learnware_info']['last_modify'],
            '2020-01-01 00:00:00'
        )
        pass


if __name__ == '__main__':
    unittest.main()
