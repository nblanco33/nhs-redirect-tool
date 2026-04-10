# analyzer.py
import requests
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def analyze_url(url, headers=None):
    """
    Analyze a URL and capture its redirect chain and timing.

    Args:
        url (str): URL to analyze
        headers (dict | None): Optional HTTP headers

    Returns:
        dict: Analysis result
    """
    try:
        start = time.perf_counter()

        response = requests.get(
            url,
            headers=headers or {},
            allow_redirects=True,
            timeout=20,
            verify=False
        )

        end = time.perf_counter()
        total_time_ms = round((end - start) * 1000)

        redirect_chain = []
        redirect_times = []

        for redirect_response in response.history:
            hop_time_ms = round(redirect_response.elapsed.total_seconds() * 1000)
            redirect_times.append(hop_time_ms)

            redirect_chain.append({
                "status": redirect_response.status_code,
                "location": redirect_response.headers.get("Location"),
                "hop_time_ms": hop_time_ms
            })

        final_hop_time_ms = total_time_ms - sum(redirect_times)

        return {
            "url": url,
            "total_redirects": len(response.history),
            "total_time_ms": total_time_ms,
            "final_hop_time_ms": final_hop_time_ms,
            "final_url": response.url,
            "redirects": redirect_chain,
            "error": None
        }

    except Exception as e:
        return {
            "url": url,
            "total_redirects": 0,
            "total_time_ms": None,
            "final_hop_time_ms": None,
            "final_url": None,
            "redirects": [],
            "error": str(e)
        }