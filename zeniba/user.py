from zeniba.client import Client


def download_stats(client: Client) -> dict | None:
    response = client.get("/papi/user/dstats")

    if response.status_code == 200:
        return response.json()
    return None

def downloaded_books(client: Client) -> dict | None:
    response = client.get("/papi/user/get-downloads")

    if response.status_code == 200:
        return response.json()
    return None