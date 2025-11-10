# Code Analysis Strands Agent

A powerful code analysis agent built with the Strands Agents SDK, deployed as an AWS Lambda function. The agent uses AI to provide comprehensive code analysis including quality assessment, security review, performance optimization, and best practice recommendations.

## Architecture

- **AWS Lambda**: Python 3.12 function with Strands Agents SDK
- **Lambda Layer**: Contains all dependencies including Strands Agents SDK and tools
- **Amazon Bedrock**: AI model provider for code analysis (Amazon Nova Lite)
- **S3 Buckets**: Input bucket for code files, output bucket for analysis results
- **EventBridge**: Triggers Lambda function when files are uploaded to S3
- **CloudWatch**: Logging and monitoring
- **CDK**: Infrastructure as Code using TypeScript

## Project Structure

```
├── bin/
│   └── code-analysis-strands.ts     # CDK app entry point
├── lib/
│   └── code-analysis-strands-stack.ts # CDK stack definition
├── lambda/
│   └── agent_handler.py             # Strands Agent Lambda handler
├── packaging/                       # Lambda deployment packages (gitignored)
│   ├── app.zip                      # Lambda function code
│   ├── dependencies.zip             # Lambda layer dependencies
│   └── _dependencies/               # Installed Python packages
├── test/
│   └── code-analysis-strands.test.ts # CDK unit tests
├── cdk.json                         # CDK configuration
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Features

### 🤖 AI-Powered Code Analysis
- **Quality Assessment**: Identifies code quality issues and improvements
- **Security Review**: Detects potential security vulnerabilities
- **Performance Analysis**: Suggests performance optimizations
- **Best Practices**: Recommends Python and general coding best practices
- **Documentation Review**: Checks for proper documentation and comments

### 🔌 Input Methods
- **Event-driven S3**: Automatic analysis triggered by S3 file uploads (primary method)
- **Direct Lambda invocation**: Manual invocation for testing and development

### 🚀 Event-Driven Architecture
- **S3 Integration**: Dedicated input and output S3 buckets
- **EventBridge**: Automatic triggering when files are uploaded
- **File Type Support**: Supports 25+ programming languages and file types
- **Automatic Processing**: No manual intervention required

### 🏗️ Production-Ready Infrastructure
- **ARM64 Architecture**: Cost-effective Lambda execution
- **Lambda Layers**: Efficient dependency management
- **Auto-scaling**: Serverless scaling based on demand
- **Monitoring**: CloudWatch logs and metrics
- **Security**: IAM roles with least-privilege access

## Prerequisites

- **AWS CLI** configured with appropriate permissions
- **Node.js** 18+ for CDK
- **Python** 3.12+ for Lambda function
- **CDK CLI**: `npm install -g aws-cdk`
- **Amazon Bedrock** model access (Amazon Nova Lite recommended)

## Quick Start

### 1. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies locally (for development)
pip install -r requirements.txt

# Install Python dependencies for Lambda (ARM64 architecture)
pip install -r requirements.txt \
    --python-version 3.12 \
    --platform manylinux2014_aarch64 \
    --target ./packaging/_dependencies \
    --only-binary=:all:
```

### 2. Package Lambda Function

```bash
# Package the Lambda function and dependencies
python bin/package_for_lambda.py
```

### 3. Deploy Infrastructure

```bash
# Bootstrap CDK (first time only)
npx cdk bootstrap

# Build TypeScript
npm run build

# Deploy the stack
npx cdk deploy --require-approval never
```

### 4. Configure Bedrock Access

**Important**: You must enable model access in Amazon Bedrock before the agent will work properly.

1. Go to the [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to "Model access" in the left sidebar
3. Click "Enable specific models"
4. Enable access to **Amazon Nova Lite** (`us.amazon.nova-lite-v1:0`)
5. Wait for the access to be granted (usually takes a few minutes)

**Note**: The agent is configured to use Amazon Nova Lite which doesn't require marketplace subscriptions, making it easier to get started.

## Usage

After deployment, you can interact with the agent in multiple ways:

### 🔄 Event-Driven S3 Analysis (Recommended)

Simply upload code files to the input S3 bucket and analysis will happen automatically:

```bash
# Upload a code file for automatic analysis
aws s3 cp your_code.py s3://code-analysis-strands-input-dev-YOUR_ACCOUNT_ID/

# Check the output bucket for results
aws s3 ls s3://code-analysis-strands-output-dev-YOUR_ACCOUNT_ID/analysis/
```

**Supported File Types**: `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.cs`, `.php`, `.rb`, `.go`, `.rs`, `.kt`, `.swift`, `.scala`, `.r`, `.sql`, `.sh`, `.yaml`, `.yml`, `.json`, `.xml`, `.html`, `.css`, `.md`, `.txt`



### Direct Lambda Invocation

```bash
aws lambda invoke \
  --function-name code-analysis-strands-agent-dev \
  --cli-binary-format raw-in-base64-out \
  --payload '{"prompt": "What are Python best practices?"}' \
  output.json

cat output.json | jq .
```



## Development

### Local Testing

```bash
# Run CDK tests
npm test

# Validate CDK template
npx cdk synth

# Compare with deployed stack
npx cdk diff
```

### Adding New Features

1. **Update Lambda Handler**: Modify `lambda/agent_handler.py`
2. **Add Dependencies**: Update `requirements.txt`
3. **Update Infrastructure**: Modify `lib/code-analysis-strands-stack.ts`
4. **Repackage**: Run packaging script (when available)
5. **Deploy**: Run `npx cdk deploy`

### Monitoring

- **CloudWatch Logs**: `/aws/lambda/code-analysis-strands-agent-dev`

- **Lambda Metrics**: Duration, errors, invocations

## Configuration

### Environment Variables

The Lambda function uses these environment variables:

- `ENVIRONMENT`: Deployment environment (dev/staging/prod)

### Permissions

The Lambda function has the following AWS permissions:

- **Bedrock**: `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`
- **S3**: `s3:GetObject`, `s3:PutObject`, `s3:ListBucket` (for future S3 integration)
- **CloudWatch**: Basic execution role for logging

## Troubleshooting

### Common Issues

**1. "Model access is denied" Error**
- **Cause**: Bedrock model access not enabled
- **Solution**: Enable model access in Bedrock console (see step 4 above)

**2. "No module named 'strands'" Error**
- **Cause**: Dependencies not properly packaged
- **Solution**: Re-run `python bin/package_for_lambda.py` and redeploy

**3. Lambda Timeout**
- **Cause**: Complex analysis taking too long
- **Solution**: Increase timeout in CDK stack (currently 60 seconds)

**4. Memory Issues**
- **Cause**: Large dependencies or complex analysis
- **Solution**: Increase memory size in CDK stack (currently 1024 MB)

### Debugging

1. **Check CloudWatch Logs**:
   ```bash
   aws logs tail /aws/lambda/code-analysis-strands-agent-dev --follow
   ```

2. **Test Lambda Directly**:
   ```bash
   aws lambda invoke --function-name code-analysis-strands-agent-dev \
     --payload '{"prompt": "test"}' output.json
   ```

3. **Validate Dependencies**:
   ```bash
   unzip -l packaging/dependencies.zip | grep strands
   ```

## Cost Optimization

- **ARM64 Architecture**: ~20% cost savings vs x86_64
- **Lambda Layers**: Reduces deployment package size
- **Efficient Memory**: 1024 MB balances performance and cost
- **Pay-per-use**: Only pay for actual analysis requests

## Security

- **IAM Roles**: Least-privilege access principles
- **VPC**: Can be deployed in VPC for additional security
- **HTTPS**: All API communication encrypted in transit
- **Input Validation**: Request validation and sanitization

## Cleanup

Remove all AWS resources:

```bash
npx cdk destroy --force
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review CloudWatch logs for error details
3. Consult the [Strands Agents documentation](https://strandsagents.com/)
4. Open an issue in the repository

---

**Built with ❤️ using Strands Agents SDK and AWS CDK**