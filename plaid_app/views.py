from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.api import plaid_api
from plaid.configuration import Configuration
from plaid.model.link_token_create_request_update import LinkTokenCreateRequestUpdate
import plaid
from datetime import datetime, timedelta
from .models import PlaidItem, BankAccount

# Initialize Plaid API
configuration = Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        "client_id": settings.PLAID_CLIENT_ID,
        "secret": settings.PLAID_SECRET,
    }
)

api_client = plaid_api.PlaidApi(configuration)

@login_required
def create_link_token(request):
    # Create a Link token for the user
    try:
        request = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name="Money Rhythm",
            country_codes=[CountryCode("US")],
            language="en",
            user=LinkTokenCreateRequestUser(
                client_user_id=str(request.user.id),
            )
        )
        response = api_client.link_token_create(request)
        return JsonResponse({"link_token": response.link_token})
    except plaid.ApiException as e:
        return JsonResponse({"error": str(e)}, status=400)
    

@csrf_exempt
@login_required
def exchange_public_token(request):
    # Exchange the public token for an access token
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        public_token = request.POST.get('public_token')
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = api_client.item_public_token_exchange(request)

        # Save the access token and item ID to the database
        PlaidItem.objects.create(
            access_token=response.item_access_token,
            item_id=response.item_id,
            user=request.user
        )

        # Fetch initial accounts
        fetch_accounts(request.user, response.access_token)

        return JsonResponse({'success': True})
    except plaid.ApiException as e:
        return JsonResponse({'error': str(e)}, status=400)
    

def fetch_accounts(user, access_token):
    try:
        response = api_client.accounts_get({
            'access_token': access_token,
            })
        
        for account in response.accounts:
            BankAccount.objects.create(
                account_id=account.account_id,
                name=account.name,
                is_active=True,
                current_balance=account.balance.current or 0.00,
                available_balance=account.balance.available or 0.00,
                plaid_item=PlaidItem.objects.get(access_token=access_token)
            )
    except plaid.ApiException as e:
        print(f"Error fetching accounts: {str(e)}")