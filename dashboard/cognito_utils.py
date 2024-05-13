import boto3


def get_existing_cognito_resources(user_pool_name, identity_pool_name):
    cognito_idp = boto3.client('cognito-idp')
    cognito_identity = boto3.client('cognito-identity')

    try:
        user_pools = cognito_idp.list_user_pools(MaxResults=60)['UserPools']
        identity_pools = cognito_identity.list_identity_pools(MaxResults=60)['IdentityPools']

        user_pool_id = next((pool['Id'] for pool in user_pools if pool['Name'] == user_pool_name), None)
        identity_pool_id = next((pool['IdentityPoolId'] for pool in identity_pools if pool['IdentityPoolName'] == identity_pool_name), None)

        return user_pool_id, identity_pool_id
    except Exception as e:
        print(f"Error getting Cognito resources: {e}")
        return None, None
