#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { CodeAnalysisStrandsStack } from '../lib/code-analysis-strands-stack';

const app = new cdk.App();
new CodeAnalysisStrandsStack(app, 'CodeAnalysisStrandsStack-dev', {
  environment: 'dev',
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});