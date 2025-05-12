# modules/sleep_timer.py
import time
import random

def run():
    print("Running sleep timer module...")
    sleep_time = random.randint(5, 15)
    print(f"Sleeping for {sleep_time} seconds...")
    time.sleep(sleep_time)
    print("Sleep complete.")
import time

def run():
    """ Sleep for 5 seconds and return a message """
    time.sleep(5)
    return "Sleep Timer completed after 5 seconds."
