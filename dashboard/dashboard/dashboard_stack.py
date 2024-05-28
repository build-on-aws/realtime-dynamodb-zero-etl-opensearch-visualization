from aws_cdk import (
    aws_s3 as s3,
    aws_iam as iam,
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_opensearchservice as opensearch,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_cognito as cognito,
    aws_logs as logs,
    aws_osis as osis,
    CfnTag

)
from constructs import Construct

import os

# Obtener el directorio actual
directorio_actual = os.getcwd()
file = f"{directorio_actual}/dashboard/template.txt"

#create the pipeline configuration
def generate_template(file, replace_value):
    """
                Function that reads a text file, replaces values according to a dictionary
                of replacements, and returns the updated content as a string.

                Args:
                    ruta_archivo (str): The path of the text file.
                    reemplazos (dict): A dictionary where the keys are the values to be
                                    replaced and the values are the new values.

                Returns:
                    str: The content of the file with the replaced values.
        """
    try:
        with open(file, 'r') as archivo:
            contenido = archivo.read()
                    
            for clave, valor in replace_value.items():
                contenido = contenido.replace(clave, valor)
            return contenido

    except FileNotFoundError:
        print(f"El archivo {file} no existe.")
        return None
    except IOError:
        print(f"Error al leer el archivo {file}.")
        return None
    

class DashboardStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        REGION_NAME = self.region
        
        # create a cognito pool for opensearch 
        cognito_pool = cognito.UserPool(self, "CognitoUserPool",
                                    sign_in_aliases=cognito.SignInAliases(
                                        email=True,
                                    ),
                                    auto_verify=cognito.AutoVerifiedAttrs(
                                        email=True
                                    ),
                                    standard_attributes=cognito.StandardAttributes(
                                        email=cognito.StandardAttribute(mutable=True, required=True)
                                    ), 
                                    removal_policy=RemovalPolicy.DESTROY
                                    )
        
        # create a user pool client for the cognito pool
        cognito_pool_client = cognito_pool.add_client(
            "CognitoUserPoolClient",
            user_pool_client_name="CognitoUserPoolClient",
            generate_secret=False,
        )
        # create a domain for the cognito pool
        domain = cognito_pool.add_domain("Domain", 
                    cognito_domain=cognito.CognitoDomainOptions(
                        domain_prefix="zeroetldemo"
                    )
                )

        # create a identity pool for opensearch
        cognito_identity_pool = cognito.CfnIdentityPool(self, "CognitoIdentityPool",
                                                    allow_unauthenticated_identities=False,
                                                    cognito_identity_providers=[
                                                        cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                                                            client_id=cognito_pool_client.user_pool_client_id,
                                                            provider_name=cognito_pool.user_pool_provider_name
                                                        )
                                                    ]
                                                    )
        
        #Sets the deletion policy of the resource based on the removal policy DESTROY
        cognito_identity_pool.apply_removal_policy(RemovalPolicy.DESTROY)

        identity_pool_id = cognito_identity_pool.ref

        

        auth_role = iam.Role(self, "authRoleIdentity", 
            assumed_by = iam.FederatedPrincipal(
                federated = 'cognito-identity.amazonaws.com',
                conditions = {
                    "StringEquals": { "cognito-identity.amazonaws.com:aud": identity_pool_id },
                    "ForAnyValue:StringLike": { "cognito-identity.amazonaws.com:amr": "authenticated" }
                },
                assume_role_action= "sts:AssumeRoleWithWebIdentity"
            )
        )

        
        cfn_identity_pool_role_attachment = cognito.CfnIdentityPoolRoleAttachment(
                    self, "IdentityPoolRoleAttachment",
                    identity_pool_id=cognito_identity_pool.ref,
                    roles={
                        "authenticated": auth_role.role_arn
                    }
            )


        # Crea una política de acceso
        auth_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "cognito-identity:GetCredentialsForIdentity",
            ],
            resources=[
                "*",
            ]
        )


        # Add the required permissions to the access role
        auth_role.add_to_policy(auth_policy)

        # Use the ref attribute to get the identity pool ID
        
        cognito_user_pool_id = cognito_pool.user_pool_id
        auth_role_arn = auth_role.role_arn
       

        #identity_pool_id = "us-west-2:"
        #cognito_user_pool_id = "us-west-..."
        #auth_role_arn = "arn:aws:iam::...:role/..."

        # Crea un rol de IAM para acceder al dominio de OpenSearch
        
        access_role = iam.Role(self, "OpenSearchAccessRoleZeroETL",
                       assumed_by=iam.ServicePrincipal("opensearchservice.amazonaws.com"),
                       managed_policies=[
                           iam.ManagedPolicy.from_aws_managed_policy_name("AmazonOpenSearchServiceCognitoAccess"),
                            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonOpenSearchIngestionFullAccess"),
                       iam.ManagedPolicy.from_aws_managed_policy_name("AmazonOpenSearchServiceFullAccess"),
                            ]
                            )

        # Crea una política de acceso
        access_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "es:*",
            ],
            resources=[
                "*",
            ]
        )
        
        # Add the required permissions to the access role
        access_role.add_to_policy(access_policy)
        
     
        #create a Role with access to the opensearch domain, assume that has the necessary permissions to DynamoDB, OpenSearch, and S3. This role should have a trust relationship with osis-pipelines.amazonaws.com and opensearchservice.amazonaws.com
        sts_role = iam.Role(self, "OpenSearchIngestionRoleZeroETL",
                   assumed_by=iam.CompositePrincipal(
                       iam.ServicePrincipal("osis-pipelines.amazonaws.com"),
                       iam.ServicePrincipal("opensearchservice.amazonaws.com")
                   ),
                   managed_policies=[
                       iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess"),
                       iam.ManagedPolicy.from_aws_managed_policy_name("AmazonOpenSearchServiceFullAccess"),
                       iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                       iam.ManagedPolicy.from_aws_managed_policy_name("AmazonOpenSearchIngestionFullAccess")
                   ]
                   )

        # Importar una VPC existente por su ID
          #vpc_id = "vpc-xxx"  # Reemplaza con el ID de tu VPC existente
          #vpc = ec2.Vpc.from_lookup(self, "ImportedVPC", vpc_id=vpc_id, region=REGION_NAME)

        opensearch_domain = opensearch.Domain(self, "ZeroETLDashboardDemoL",
                                   version=opensearch.EngineVersion.OPENSEARCH_1_3,
                                   capacity=opensearch.CapacityConfig(
                                       data_nodes=1,
                                       data_node_instance_type="r5.large.search",
                                       multi_az_with_standby_enabled = False,
                                       #master_nodes=1,
                                       #master_node_instance_type="r5.large.search"
                                   ),
                                   ebs=opensearch.EbsOptions(
                                       volume_size=10, 
                                       volume_type=ec2.EbsDeviceVolumeType.GP3
                                   ),
                                   
                                   cognito_dashboards_auth=opensearch.CognitoOptions(
                                           user_pool_id= cognito_user_pool_id,
                                            identity_pool_id=identity_pool_id,
                                            role=access_role
                                        ),  
                                    removal_policy=RemovalPolicy.DESTROY
                                    )
        
        #https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_elasticsearch/README.html
        opensearch_domain.add_access_policies(
            iam.PolicyStatement(
                actions=["es:*"],
                effect=iam.Effect.ALLOW,
                principals=[iam.AccountPrincipal(self.account), iam.ArnPrincipal(auth_role_arn)],
                resources=[f"{opensearch_domain.domain_arn}/*"]
            )
            )
    
        #https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_opensearchservice/README.html#vpc-support
        
        s3_backup_bucket = s3.Bucket(
            self,
            "OpenSearchDynamoDBIngestionBackupS3Bucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_name=f"opensearch-ddb-ingestion-backup-{self.account}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY
            
        )
        dynamodb_table = dynamodb.Table(
            self,
            "DynamoDBTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.NUMBER
            ),
            table_name="opensearch-ingestion-table",
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            stream=dynamodb.StreamViewType.NEW_IMAGE,
            removal_policy=RemovalPolicy.DESTROY
        )

        
        cloudwatch_logs_group = logs.LogGroup(
            self,
            "OpenSearchIngestionZeroETLPipelineLogGroup",
            log_group_name="/aws/vendedlogs/OpenSearchIntegrationZeroETL/opensearch-dynamodb-ingestion-pipeline",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY
        )

        replace_value = {
                "REGION_NAME": str(REGION_NAME),
                "BUCKET_NAME": str(s3_backup_bucket.bucket_name),
                "DYNAMODB_TABLE_ARN": str(dynamodb_table.table_arn), #modify this value with the ARN of your existing table
                "STS_ROLE_ARN":str(sts_role.role_arn),
                "OpenSearch_DOMAIN":str(opensearch_domain.domain_endpoint),
                }

        pipeline_configuration_body = generate_template(file, replace_value)
        print(pipeline_configuration_body)


        #https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_osis/CfnPipeline.html

        cfn_pipeline = osis.CfnPipeline(self, "OpenSearchZeroETLPipeline",
                                        pipeline_name = "opensearch-dynamodb-etl",
                                        max_units=1,
                                        min_units=1,
                                        pipeline_configuration_body=pipeline_configuration_body,
                                        log_publishing_options = {
                                            "cloudwatchLogGroupArn": cloudwatch_logs_group.log_group_arn,
                                            "enabled": True
                                        },
                                         tags=[
                                                CfnTag(key="Name", value="OpenSearchIngestionZeroETLPipeline"),
                                                CfnTag(key="Description", value="OpenSearch Ingestion Zero ETL Pipeline")
                                            ]
                                        )
        #Sets the deletion policy of the resource based on the removal policy DESTROY
        cfn_pipeline.apply_removal_policy(RemovalPolicy.DESTROY)
