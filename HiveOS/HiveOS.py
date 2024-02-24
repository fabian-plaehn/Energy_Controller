from time import sleep
import json
import requests.exceptions
from requests import request, exceptions


class Hive(object):
    def __init__(self, token, farm_name, available_worker_ids=None):
        self.token = token
        self.farm_id = self.__get_farm_id_by_name(farm_name)
        self.worker_ids = self.__get_worker_ids()
        self.available_worker_ids = available_worker_ids if available_worker_ids is not None else self.worker_ids
        print(self.worker_ids, self.available_worker_ids)
        print([fs["name"] for fs in self.get_all_fs()])
        # self.worker_id = self.__get_worker_id_by_name(config['WORKER_NAME'])

    def api_query(self, method, command, payload=None, params=None):
        if payload is None:
            payload = {}
        if params is None:
            params = {}
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.token
        }

        while True:
            try:
                s = request(method, 'https://api2.hiveos.farm/api/v2' + command, data=payload, params=params,
                            headers=headers, timeout=100)
            except exceptions.ConnectionError:
                print('Oops. Connection failed to HiveOs')
                sleep(15)
                continue
            except exceptions.Timeout:
                print('Oops. Timed out waiting for a response from HiveOs')
                sleep(15)
                continue
            except exceptions.TooManyRedirects:
                print('Oops. Exceeded number of requests from HiveOs, Wait 30 minutes')
                sleep(1800)
                continue
            else:
                api = s.json()
                break

        return api

    def __get_farms(self):
        return self.api_query('GET', '/farms')

    def __get_farm_id_by_name(self, name: str) -> int:
        print('Getting farm id by name')
        farms = self.__get_farms()['data']
        return next(farm for farm in farms if farm['name'] == name)['id']

    def __get_worker_id_by_name(self, name: str) -> int:
        print('Getting worker id by name')
        workers = self.__get_workers_preview()['data']
        return next(worker for worker in workers if worker['name'] == name)['id']

    def __get_worker_ids(self):
        workers = self.__get_workers_preview()['data']
        return [worker["id"] for worker in workers]

    def __get_workers_preview(self) -> dict:
        return self.api_query('GET', f'/farms/{self.farm_id}/workers/preview')

    def get_current_fs(self, worker_id) -> str:
        return self.api_query('GET', f'/farms/{self.farm_id}/workers/{worker_id}')['flight_sheet']['id']

    def get_all_fs(self) -> dict:
        return self.api_query('GET', f'/farms/{self.farm_id}/fs')['data']

    def set_fs_all(self, id):
        fs = {'fs_id': id}
        fs_json = json.dumps(fs)
        for worker_id in self.worker_ids:
            if worker_id not in self.available_worker_ids:
                continue
            if id == self.get_current_fs(worker_id):
                continue
            sleep(0.1)
            try:
                self.api_query('PATCH', f'/farms/{self.farm_id}/workers/{worker_id}', payload=fs_json)
            except requests.exceptions.JSONDecodeError:
                print("EXCEPTION set_fs_all")
                print(self.farm_id, worker_id, fs_json, id)
            sleep(0.1)