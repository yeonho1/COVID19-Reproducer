import json
import requests

class COVIDParser:
    api_key = None
    api_uri = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson'
    api_params = 'numOfRows=200&pageNo=1&startCreateDt=20200309&_type=json'

    def __init__(self, api_key):
        self.api_key = api_key
    
    def request(self, minimum_item_count=10):
        # Returns a tuple containing:
        #     1) Result code
        #         0 : Everything was successful and got expected items.
        #         -1: Could not get info from API because API Key was not
        #             set properly.
        #         -2: API did not send 200 OK status code.
        #         -3: Response contents' type is different with
        #             which we expected.
        #         -4: Response contents' item count was lower than
        #             minimum required count.
        #         -5: Failed to get items from response contents.
        #     2) Data
        #         If the result code is lower than 0
        #             (if any error occured while processing data),
        #             the data will be None.
        #         Otherwise, the data will be a list of dictionaries,
        #             contains the parsed data.
        #         The data count will be equal to minimum_item_count.
        if self.api_key is None:
            print('[COVID-Parser] API Key was not set properly. Aborting')
            return (-1, None)
        response = requests.get(f'{self.api_uri}?serviceKey={self.api_key}&{self.api_params}')
        if response.status_code != 200:
            print('[COVID-Parser] Failed to request data to API. Aborting')
            return (-2, None)
        r_dict = json.loads(response.text)
        try:
            items = r_dict['response']['body']['items']['item']
            if type(items) != list:
                print('[COVID-Parser] Non-expected type of response content. Aborting')
                return (-3, None)
            if len(items) < minimum_item_count:
                print('[COVID-Parser] Item count lower than minimum required count. Aborting')
                return (-4, None)
            result = []
            prev_date = ''
            count = 0
            for i in items:
                if count >= minimum_item_count:
                    break
                if i['createDt'][:10] == prev_date:
                    continue
                prev_date = i['createDt'][:10]
                result.append({
                    'date': prev_date,
                    'confirmed': i['decideCnt'],
                    'clear': i['clearCnt'],
                    'died': i['deathCnt']
                })
                count += 1
            return (0, result)
        except KeyError:
            print('[COVID-Parser] Failed to parse items from API Response. Aborting')
            return (-5, None)
        