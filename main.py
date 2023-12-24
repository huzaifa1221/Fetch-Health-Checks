import requests
import time
from collections import defaultdict
import yaml



def check_health(url, method="GET", headers={}, body=None):
    """
    Check the health of an HTTP endpoint.

    Args:
        url: The URL of the endpoint.
        method: The HTTP method to use (GET, POST, etc.).
        headers: Optional headers to send with the request.
        body: Optional body to send with the request.

    Returns:
        True if the endpoint is healthy, False otherwise.
    """
    try:
        response = requests.request(
            method, url, headers=headers, data=body
        )

        latency_time = get_response_latency(url=url)
        # print(f"for url{url} latency time = {latency_time} and status code = {response.status_code}")

        if 200 >= response.status_code <300 and latency_time<0.5:
            return True
        else:
            # print(f"WARNING: Endpoint {url} returned code {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Failed to connect to {url}: {e}")
        return False

def get_response_latency(url):
    try:
        # Record the start time
        start_time = time.time()

        # Send an HTTP GET request to the specified URL
        response = requests.get(url)

        # Record the end time
        end_time = time.time()

        # Calculate the response latency
        latency = end_time - start_time

        # Return the latency in seconds
        return latency
    
    except requests.RequestException as e:
        # Handle any exceptions that might occur during the request
        print(f"Error: {e}")
        return None
    
def main ():
     
    with open("endpoints.yaml", "r") as f:
        endpoints = yaml.safe_load(f)

    domain_availability = defaultdict(lambda: [0, 0])

    try:
        while True:
            # Check the health of each endpoint
            for endpoint in endpoints:
                url = endpoint["url"]
                method = endpoint.get("method", "GET")
                headers = endpoint.get("headers", {})
                body = endpoint.get("body", None)
                name = endpoint.get("name", url)

                is_healthy = check_health(url=url, method=method, headers=headers, body=body)

                domain = url.split("/")[2]
                total_requests, successful_requests = domain_availability[domain]
                total_requests += 1
                if is_healthy:
                    successful_requests += 1
                domain_availability[domain] = [total_requests, successful_requests]

            for domain, data in domain_availability.items():
                total_requests, successful_requests = data
                percentage = 100 * successful_requests / total_requests
                # print(f"\033[1m{domain}: has {percentage:.0f}% availability percentage\033[0m")
                print(f"{domain}: has {percentage:.0f}% availability percentage ")
            
            print()
            time.sleep(15)
    except KeyboardInterrupt:
        for domain, data in domain_availability.items():
            total_requests, successful_requests = data
            # print(f"{domain}: {successful_requests}/{total_requests} successful")
        print("Exiting program...")


if __name__ == "__main__":
    main()
