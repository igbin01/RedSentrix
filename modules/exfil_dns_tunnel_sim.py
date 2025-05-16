# modules/exfil_dns_tunnel_sim.py

import base64
import random
import string

def generate_fake_data():
    """
    Generate a random alphanumeric string, encode it in base32,
    and strip trailing padding.
    """
    data = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    return base64.b32encode(data.encode()).decode().strip('=')

def simulate_dns_exfil(domain='malicious.com'):
    """
    Simulate DNS tunneling by generating fake data chunks
    and printing them as if being sent via DNS subdomains.
    """
    print("[Exfil] Simulating DNS tunnel:")
    for _ in range(5):
        fake_data = generate_fake_data()
        subdomain = f"{fake_data.lower()}.{domain}"
        print(f"-> {subdomain}")
    return "[Exfil] DNS tunneling simulation complete."

def run():
    """
    Main entry point for the RedSentrix framework to invoke this module.
    """
    return simulate_dns_exfil()

