import requests
import hashlib

PWNED_URL = "https://api.pwnedpasswords.com/range/"


def request_api_data(pass_str):
    response = requests.get(f"{PWNED_URL}{pass_str}")

    if response.status_code != 200:
        raise RuntimeError(f"Error Fetching: {response.status_code}. Check your API call and try again.")

    return response


def get_leak_count(response, hashed_password):
    searched_prefix = hashed_password[:5]
    hashes = {searched_prefix + line.split(":")[0]: int(line.split(":")[1]) for line in response.text.splitlines()}
    leak_count = 0

    if hashed_password in hashes:
        leak_count = hashes[hashed_password]

    return leak_count


def pwned_api_check(plaintext_password):
    hashed_password = hashlib.sha1(plaintext_password.encode("UTF-8")).hexdigest().upper()
    api_response = request_api_data(hashed_password[:5])
    leak_count = get_leak_count(api_response, hashed_password)
    print(f"{plaintext_password} has been leaked {leak_count} times.")


if __name__ == "__main__":
    pwned_api_check("Password1")
