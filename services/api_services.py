# services/api_service.py
import requests


def fetch_schemes(base_url: str, total_results: int, max_size: int, headers: dict) -> tuple[list[str], str]:
    """
    Fetches a paginated list of scheme slugs from an API.

    This function iteratively retrieves data in chunks from the specified API endpoint.

    Args:
        base_url (str): The base URL of the API endpoint.
        total_results (int): The total number of results expected.
        max_size (int): The maximum number of results to fetch per request.
        headers (dict): A dictionary of headers to include in the request.

    Returns:
        tuple: A tuple containing:
            - list[str]: A list of extracted scheme slugs.
            - str (optional): A semicolon-separated string of error messages encountered during fetching,
                or None if no errors occurred.
    """
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
