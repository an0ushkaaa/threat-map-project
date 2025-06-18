import requests
import json
import random
import time
import datetime
from sseclient import SSEClient

# Fetch data from CheckPoint ThreatMap API
def fetch_checkpoint_data():
    print("Fetching data from CheckPoint API...")
    url = "https://threatmap-api.checkpoint.com/ThreatMap/api/feed"
    headers = {
        "Accept": "text/event-stream",
        "User-Agent": "Mozilla/5.0",
    }

    response = requests.get(url, headers=headers, stream=True)
    attacks = []
    start_time = time.time()

    if response.status_code == 200:
        client = SSEClient(response)
        for event in client.events():
            try:
                data = json.loads(event.data)
                if "a_n" in data or "a_t" in data:
                    source_country = data.get("s_co", "Unknown")
                    dest_country = data.get("d_co", "Unknown")
                    attack_name = data.get("a_n", "Unknown")

                    print(f"> {attack_name} from {source_country} → {dest_country}")

                    attacks.append({
                        "attack_name": attack_name,
                        "attack_type": data.get("a_t", "Unknown"),
                        "source_country": source_country,
                        "dest_country": dest_country,
                        "latitude": data.get("s_la", 0),
                        "longitude": data.get("s_lo", 0)
                    })

                if time.time() - start_time > 5:  # Limit to ~5 seconds of streaming
                    break
            except json.JSONDecodeError:
                continue
    else:
        print(f"CheckPoint API Error: {response.status_code}")

    return attacks

# Fetch data from Fortinet ThreatMap API
def fetch_fortinet_data():
    print("Fetching data from Fortinet API...")
    url = "https://fortiguard.fortinet.com/api/threatmap/outbreaks"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
    }

    response = requests.get(url, headers=headers)
    attacks = []

    if response.status_code == 200:
        data = response.json()
        for threat in data:
            attacks.append({
                "attack_name": threat.get("tag", "Unknown"),
                "attack_type": "Fortinet Threat",
                "source_country": threat.get("country", "Unknown"),
                "latitude": threat.get("latitude", 0),
                "longitude": threat.get("longitude", 0)
            })
    else:
        print(f"Fortinet API Error: {response.status_code}")

    return attacks

# Fetch data from Radware ThreatMap API
def fetch_radware_data():
    print("Fetching data from Radware API...")
    url = "https://ltm-prod-api.radware.com/map/attacks?limit=10"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
    }

    response = requests.get(url, headers=headers)
    attacks = []

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            for attack in data:
                if isinstance(attack, dict):
                    attacks.append({
                        "attack_name": attack.get("attackType", "Unknown"),
                        "attack_type": "Radware Threat",
                        "source_country": attack.get("sourceCountry", "Unknown"),
                        "latitude": attack.get("sourceLatitude", 0),
                        "longitude": attack.get("sourceLongitude", 0)
                    })
    else:
        print(f"Radware API Error: {response.status_code}")

    return attacks

# Fetch IP geolocation data from multiple services
def fetch_ip_info(ip):
    services = {
        "ip-api": f"http://ip-api.com/json/{ip}",
        "ipinfo": f"https://ipinfo.io/{ip}/json",
        "ipwhois": f"https://ipwhois.app/json/{ip}"
    }

    results = {"IP": ip, "Country": "Unknown", "City": "Unknown", "Latitude": 0, "Longitude": 0}

    for service, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            if "country" in data:
                results["Country"] = data.get("country", "Unknown")
                results["City"] = data.get("city", "Unknown")
                results["Latitude"] = float(data.get("lat", data.get("latitude", 0)))
                results["Longitude"] = float(data.get("lon", data.get("longitude", 0)))
                break
        except requests.exceptions.RequestException:
            continue

    return results

# Fetch IP geolocation for a random set of IPs
def fetch_random_ip_data():
    random_ips = [
        "8.8.8.8", "1.1.1.1", "208.67.222.222", "23.216.100.30",
        "152.52.34.131", "14.142.143.98"
    ]
    ip = random.choice(random_ips)
    print(f"Fetching geolocation for {ip}...")
    return fetch_ip_info(ip)

# Combine all threat & IP geolocation data sources
def get_all_data():
    print("Fetching all data sources...")
    threats = fetch_checkpoint_data() + fetch_fortinet_data() + fetch_radware_data()
    ip_data = fetch_random_ip_data()

    # ✅ Save fetched data for debugging
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open(f"debug_threats_{timestamp}.json", "w") as f:
        json.dump({"threats": threats, "ip_data": ip_data}, f, indent=4)

    return {
        "threats": threats,
        "ip_data": ip_data
    }

# Run standalone for testing
if __name__ == "__main__":
    while True:
        data = get_all_data()
        print(f"\n🛡️ Fetched {len(data['threats'])} total threats")
        print(f"🌍 Random IP Geo: {data['ip_data']}")
        time.sleep(5)
