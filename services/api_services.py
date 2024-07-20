# services/api_service.py

import requests
from typing import List, Tuple


def fetch_schemes(base_url: str, total_results: int, max_size: int, headers: dict) -> Tuple[List[str], str]:
    slugs = []
    error_messages = []

    for start in range(0, total_results, max_size):
        url = f"{base_url}{max_size}&from={start}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data['status'] == 'Success':
                items = data['data']['hits']['items']
                for item in items:
                    slugs.append(item['fields']['slug'])
            else:
                error_message = f"Error fetching data for start={start}: {data['errorDescription']}"
                error_messages.append(error_message)

        except requests.RequestException as e:
            error_message = f"Request failed for start={start}: {e}"
            error_messages.append(error_message)

    return slugs, "; ".join(error_messages) if error_messages else None
