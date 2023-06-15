import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';
import { Platform } from 'aws-cdk-lib/aws-ecr-assets';

interface EnchantmentsStackProps extends cdk.StackProps {
  sitesTableName: string;
  sitesSnsName: string;
  sitesSubscriptions: string[];
}

export class EnchantmentsStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: EnchantmentsStackProps) {
    super(scope, id, props);

    const snsTopic = this.createSnsTopic(props);
    const ddbTable = this.createDdbTable(props);
    const role = this.createLambdaRole(snsTopic, ddbTable);
    const lambdaFunction = this.createLambda(role);
    this.createLambdaSchedule(lambdaFunction);
  }

  private createLambda(role: iam.Role) {
    return new lambda.DockerImageFunction(this, 'EnchantmentsLambda', {
      functionName: 'enchantments-lambda-v2',
      description: 'Lambda for finding available locations in Enchantments',
      code: lambda.DockerImageCode.fromImageAsset('.', {
        platform: Platform.LINUX_AMD64,
        file: "lambda/Dockerfile"
      }),
      timeout: cdk.Duration.minutes(5),
      memorySize: 1024,
      role: role
    });
  }

  private createLambdaRole(snsTopic: sns.Topic, ddbTable: dynamodb.Table) {
    const role = new iam.Role(this, 'EnchantmentsLambdaRole', {
      description: 'IAM execution role for enchantments lambda',
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
    });

    // Give basic permissions to Lambda like writing to CloudWatch, etc
    role.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'));

    // Enable Lambda to read and write to the DynamoDB table
    ddbTable.grantReadWriteData(role);

    // Enable Lambda to publish events and call sns:CreateTopic, which is used to fetch the topic ARN at runtime
    snsTopic.grantPublish(role);
    role.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      resources: [snsTopic.topicArn],
      actions: ['sns:CreateTopic']
    }));

    return role;
  }

  private createLambdaSchedule(lambda: any): events.Rule {
    const eventRule = new events.Rule(this, 'enchantmentsSchedule', {
      schedule: events.Schedule.cron({ minute: '*/30'}),
    });

    eventRule.addTarget(new targets.LambdaFunction(lambda));

    return eventRule;
  }

  private createSnsTopic(props: EnchantmentsStackProps): sns.Topic {
    const topic = new sns.Topic(this, 'EnchantmentsTopic', {
      topicName: props.sitesSnsName,
      displayName: props.sitesSnsName
    });

    props.sitesSubscriptions.forEach(email => {
      topic.addSubscription(new subscriptions.EmailSubscription(email))
    });

    return topic;
  }

  private createDdbTable(props: EnchantmentsStackProps): dynamodb.Table {
    return new dynamodb.Table(this, 'EnchantmentsTable', {
      tableName: props.sitesTableName,
      partitionKey: { name: 'siteId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'date', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST
    }); 
  }
}
