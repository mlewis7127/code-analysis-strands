import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import * as CodeAnalysisStrands from '../lib/code-analysis-strands-stack';

test('Strands Agent Lambda Function Created', () => {
  const app = new cdk.App();
  const stack = new CodeAnalysisStrands.CodeAnalysisStrandsStack(app, 'MyTestStack');
  const template = Template.fromStack(stack);

  // Test that Lambda function is created with correct properties
  template.hasResourceProperties('AWS::Lambda::Function', {
    Runtime: 'python3.12',
    Handler: 'agent_handler.handler',
    FunctionName: 'code-analysis-strands-agent-dev',
    Architectures: ['arm64'],
    MemorySize: 1024,
    Timeout: 60,
  });
});

test('S3 Buckets Created', () => {
  const app = new cdk.App();
  const stack = new CodeAnalysisStrands.CodeAnalysisStrandsStack(app, 'MyTestStack');
  const template = Template.fromStack(stack);

  // Test that S3 buckets are created
  template.resourceCountIs('AWS::S3::Bucket', 2);
});

test('EventBridge Rule Created', () => {
  const app = new cdk.App();
  const stack = new CodeAnalysisStrands.CodeAnalysisStrandsStack(app, 'MyTestStack');
  const template = Template.fromStack(stack);

  // Test that EventBridge rule is created
  template.hasResourceProperties('AWS::Events::Rule', {
    Description: 'Trigger code analysis when files are uploaded to S3'
  });
});

test('Lambda Layer Created', () => {
  const app = new cdk.App();
  const stack = new CodeAnalysisStrands.CodeAnalysisStrandsStack(app, 'MyTestStack');
  const template = Template.fromStack(stack);

  // Test that Lambda layer is created
  template.hasResourceProperties('AWS::Lambda::LayerVersion', {
    Description: 'Strands Agents SDK and dependencies for code analysis',
    CompatibleRuntimes: ['python3.12'],
  });
});

test('IAM Permissions for Bedrock', () => {
  const app = new cdk.App();
  const stack = new CodeAnalysisStrands.CodeAnalysisStrandsStack(app, 'MyTestStack');
  const template = Template.fromStack(stack);

  // Test that Lambda function has IAM policy with Bedrock permissions
  const policies = template.findResources('AWS::IAM::Policy');
  const hasBedrockPermissions = Object.values(policies).some((policy: any) => {
    const statements = policy.Properties.PolicyDocument.Statement;
    return statements.some((statement: any) => 
      statement.Action.includes('bedrock:InvokeModel') &&
      statement.Action.includes('bedrock:InvokeModelWithResponseStream')
    );
  });
  expect(hasBedrockPermissions).toBe(true);
});

test('Lambda Layer has Correct Properties', () => {
  const app = new cdk.App();
  const stack = new CodeAnalysisStrands.CodeAnalysisStrandsStack(app, 'MyTestStack');
  const template = Template.fromStack(stack);

  // Test that Lambda layer has correct runtime compatibility
  template.hasResourceProperties('AWS::Lambda::LayerVersion', {
    Description: 'Strands Agents SDK and dependencies for code analysis',
    CompatibleRuntimes: ['python3.12'],
  });
});

test('Lambda Function has Environment Variables', () => {
  const app = new cdk.App();
  const stack = new CodeAnalysisStrands.CodeAnalysisStrandsStack(app, 'MyTestStack');
  const template = Template.fromStack(stack);

  // Test that Lambda function has correct environment variables
  template.hasResourceProperties('AWS::Lambda::Function', {
    Environment: {
      Variables: {
        ENVIRONMENT: 'dev'
      }
    }
  });
});