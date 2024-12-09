"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS



import stripe
import os
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200


stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@api.route('/create-payment-intent', methods=['OPTIONS', 'POST'])
def create_payment_intent():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        data = request.get_json()
        intent = stripe.PaymentIntent.create(
            amount=data['amount'],  # amount in cents
            currency='usd',
            metadata={'integration_check': 'accept_a_payment'},
        )
        return jsonify({
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        return jsonify(error=str(e)), 403

@api.route('/payout', methods=['POST'])
@jwt_required() 
def create_payout():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()


        # Here you would typically look up the Stripe account ID for the current user
        # This is just an example - replace with your actual logic
        # provider_stripe_account = get_provider_stripe_account(current_user_id)

        # Create a transfer to the connected account
        payout = stripe.Payout.create(
            amount=data['amount'],  # amount in cents
            currency='usd',
            # stripe_account="acct_1Q18mE2ZAO1b3fPQ"
            # stripe_account="acct_1QIydjIKKqBcu9li" #regular stripe acc
            stripe_account="acct_1QIyvyIurh11jVin" #sandbox stripe acc

            # stripe_account=data['providerId']  # Stripe Account ID of the provider
            # stripe_account=provider_stripe_account
        )

        return jsonify({
            'success': True,
            'payoutId': payout.id
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 403

# def get_provider_stripe_account(user_id):
    # This is a placeholder function
    # Implement the logic to retrieve the Stripe account ID for the given user
    # This might involve a database lookup or an API call to your user management system
    # pass

# --------------------------testing---------------
# @api.route('/payout', methods=['POST'])
# def create_payout():
#     try:
#         data = request.get_json()
#         amount = data.get('amount')
#         provider_id = data.get('providerId')

#         if not amount or not provider_id:
#             return jsonify({
#                 'success': False,
#                 'error': 'Missing required fields: amount and providerId'
#             }), 400

#         if provider_id == "test_provider_id":
#             # For testing purposes, we'll simulate a successful payout
#             return jsonify({
#                 'success': True,
#                 'payoutId': 'test_payout_id_12345',
#                 'message': 'This is a simulated successful payout for testing purposes.'
#             })

#         # In a real scenario, you would use the actual Stripe payout here
#         # payout = stripe.Payout.create(
#         #     amount=amount,
#         #     currency='usd',
#         #     stripe_account=provider_id
#         # )

#         # return jsonify({
#         #     'success': True,
#         #     'payoutId': payout.id
#         # })

#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500
# --------------------testing------------------------