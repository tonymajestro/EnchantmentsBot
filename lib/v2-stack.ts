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

    const lambdaFunction = this.createLambda();
    this.createLambdaSchedule(lambdaFunction);
    this.createSnsTopic(props);
    this.createDdbTable(props);
  }

  private createLambda() {
    return new lambda.DockerImageFunction(this, 'EnchantmentsLambda', {
      functionName: 'enchantments-lambda-v2',
      description: 'Lambda for finding available locations in Enchantments',
      code: lambda.DockerImageCode.fromImageAsset('.', {
        platform: Platform.LINUX_AMD64,
        file: "lambda/Dockerfile"

      }),
      timeout: cdk.Duration.minutes(5),
      memorySize: 1024,
      role: this.createLambdaRole(),
    });
  }

  private createLambdaRole() {
    const role = new iam.Role(this, 'EnchantmentsLambdaRole', {
      description: 'IAM execution role for enchantments lambda',
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
    });

    role.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'));

    role.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      resources: ['*'],
      actions: [
        'sns:*',
        'dynamodb:*',
      ]
    }));

    return role;
  }

  private createLambdaSchedule(lambda: any) {
    const eventRule = new events.Rule(this, 'enchantmentsSchedule', {
      schedule: events.Schedule.cron({ minute: '*/30'}),
    });

    eventRule.addTarget(new targets.LambdaFunction(lambda));
  }

  private createSnsTopic(props: EnchantmentsStackProps) {
    const topic = new sns.Topic(this, 'EnchantmentsTopic', {
      topicName: props.sitesSnsName,
      displayName: props.sitesSnsName
    });

    props.sitesSubscriptions.forEach(email => {
      topic.addSubscription(new subscriptions.EmailSubscription(email))
    });
  }

  private createDdbTable(props: EnchantmentsStackProps) {
    new dynamodb.Table(this, 'EnchantmentsTable', {
      tableName: props.sitesTableName,
      partitionKey: { name: 'siteId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'date', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST
    }); 
  }
}
