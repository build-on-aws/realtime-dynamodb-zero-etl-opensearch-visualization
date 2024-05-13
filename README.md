# Real-time Data Visualization with OpenSearch and Amazon DynamoDB: A Zero-ETL Pipeline

[Amazon OpenSearch](https://docs.aws.amazon.com/es_es/opensearch-service/latest/developerguide/what-is.html) Service and Amazon DynamoDB provide a powerful combination for real-time data visualization without the need for complex Extract, Transform, Load (ETL) processes. This blog post introduces an AWS Cloud Development Kit (CDK) stack that deploys a serverless architecture for efficient, real-time data ingestion using the [OpenSearch Ingestion](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/ingestion.html) service (OSIS).

By leveraging OSIS, you can process and transform data from DynamoDB streams directly into OpenSearch, enabling near-instant visualization and analysis. This zero-ETL pipeline eliminates the overhead of traditional data transformation workflows, allowing you to focus on deriving insights from your data.

The CDK stack provisions key components such as Amazon Cognito for authentication, IAM roles for secure access, an OpenSearch domain for indexing and visualization, an S3 bucket for data backups, and a DynamoDB table as the data source. OpenSearch Ingestion acts as the central component, efficiently processing data based on a declarative YAML configuration.

## How Does This Application Work?
![Authentication](imagen/diagram.jpg)

The flow starts with data stored in Amazon DynamoDB, a managed and scalable NoSQL database. Then, the data is transmitted to [Amazon S3](https://docs.aws.amazon.com/es_es/AmazonS3/latest/userguide/Welcome.html), a highly durable and scalable object storage service.

From the data in S3, it is indexed using Amazon OpenSearch, a service that enables real-time search and analysis on large volumes of data. OpenSearch indexes the data and makes it easily accessible for fast queries.

The next component is Amazon Cognito, a service that enables user identity and access management. Cognito authenticates and authorizes users to access the necessary resources.

Lastly, [AWS Identity and Access Management Roles](https://docs.aws.amazon.com/es_es/IAM/latest/UserGuide/id_roles.html) is used to define access roles and permissions. IAM ensures that only authorized users and services can interact with the components of the architecture.

The final result is visualized in Amazon OpenSearch Dashboard, an interface that allows intuitive exploration, visualization, and analysis of the indexed data.

The advantage of this "zero ETL" approach is that it eliminates the need for complex data transformation processes. Data flows directly from the source (DynamoDB) to its final destination (OpenSearch) without requiring intermediate transformations. This simplifies the architecture, reduces latency, and enables real-time data analysis.

## Prerequisites

- [AWS Account](https://aws.amazon.com/resources/create-account/?sc_channel=el&sc_campaign=datamlwave&sc_content=cicdcfnaws&sc_geo=mult&sc_country=mult&sc_outcome=acq) 
-  [Foundational knowledge of Python](https://catalog.us-east-1.prod.workshops.aws/workshops/3d705026-9edc-40e8-b353-bdabb116c89c/) 

## Walkthrough



- Deploying the CDK stack
- Configuring OpenSearch Ingestion Service (OSIS)
- Setting up Amazon Cognito authentication
- Populating the DynamoDB table with sample data
- Visualizing data in OpenSearch

## Conclusion

In this post, we explored how the combination of Amazon OpenSearch and Amazon DynamoDB enables real-time data visualization without the complexities of traditional ETL processes. By leveraging the OpenSearch Ingestion Service (OSIS) and the AWS CDK, you can easily deploy a serverless architecture that efficiently processes and transforms data from DynamoDB streams directly into OpenSearch.

The provided CDK stack simplifies the provisioning and configuration of key components, including Amazon Cognito for authentication, IAM roles for secure access, an OpenSearch domain for indexing and visualization, an S3 bucket for data backups, and a DynamoDB table as the data source. This comprehensive solution empowers you to focus on deriving insights from your data rather than managing the underlying infrastructure.

Whether you're building real-time dashboards, analyzing log data, or monitoring IoT events, this zero-ETL pipeline offers a scalable and agile approach to data ingestion and visualization. By eliminating the need for complex data transformation workflows, you can achieve near-instant access to your data and make informed decisions based on up-to-date information.

We encourage you to clone the repository, customize the configuration to meet your specific requirements, and deploy the stack in your AWS account. Embrace the power of OpenSearch and DynamoDB to unlock real-time data visualization capabilities and gain valuable insights from your data.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

