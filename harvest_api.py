from decouple import config
from tapioca.exceptions import ClientError, ServerError
from tapioca_harvest import Harvest


class APIConnectionError(Exception):
    '''
        Exception to be raised when the API responds with an error
    '''


class HarvestClient:

    def __init__(self):
        self.api = Harvest(
            token=config('HARVEST_API_TOKEN'),
            account_id=config('HARVEST_ACCOUNT_ID'),
            user_agent=config('HARVEST_APP_NAME')
        )

    def get_all_pages(self, resource_name, search_params):
        try:
            api_resource = getattr(self.api, resource_name)()
            response = api_resource.get(params=search_params)
            content = response._data[resource_name]
            page = response._data['page']

            while page < response._data['total_pages']:
                page += 1
                search_params['page'] = page
                response = api_resource.get(params=search_params)
                content.extend(response._data[resource_name])

            return content

        except (ClientError, ServerError):
            raise APIConnectionError('The Harvest API returned an error')

    def filter_resource(self, resource_name, **kwargs):
        return self.get_all_pages(resource_name, kwargs)