from strands import Agent
from strands_tools import http_request
from typing import Dict, Any
import json
import logging
import time
import boto3
import os
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define a code analysis system prompt
CODE_ANALYSIS_SYSTEM_PROMPT = """You are a code analysis assistant with HTTP capabilities. You can:

1. Analyze code files from S3 buckets
2. Identify code quality issues, security vulnerabilities, and best practices
3. Generate detailed analysis reports
4. Make HTTP requests to external APIs for additional context

When analyzing code:
1. Focus on code quality, security, performance, and maintainability
2. Identify potential bugs, security vulnerabilities, and anti-patterns
3. Suggest improvements and best practices
4. Provide clear, actionable recommendations
5. Format your analysis in a structured, readable format

Always provide constructive feedback and explain the reasoning behind your recommendations.
"""

def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler for code analysis requests using Strands Agent.
    
    Args:
        event: Lambda event containing the analysis request
        context: Lambda context
        
    Returns:
        Dict: Response with analysis results
    """
    start_time = time.time()
    request_id = context.aws_request_id if context else "unknown"
    
    logger.info(f"Processing code analysis request {request_id}")
    
    try:
        # Handle EventBridge S3 events (primary use case)
        if 'source' in event and event['source'] == 'eventbridge':
            return handle_s3_event(event, context, start_time)
        
        # Handle direct Lambda invocation with prompt (for testing)
        elif 'prompt' in event:
            return handle_prompt_analysis(event, context, start_time)
        
        # Default response
        else:
            processing_time = time.time() - start_time
            return {
                'status': 'success',
                'message': 'Code Analysis Strands Agent invoked',
                'request_id': request_id,
                'processing_time_seconds': round(processing_time, 3),
                'version': '1.0.0-strands'
            }
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            'status': 'error',
            'message': f"Internal server error: {str(e)}",
            'request_id': request_id
        }

def handle_prompt_analysis(event: Dict[str, Any], context, start_time: float) -> Dict[str, Any]:
    """Handle prompt-based code analysis using Strands Agent."""
    request_id = context.aws_request_id if context else "unknown"
    prompt = event.get('prompt', '')
    
    logger.info(f"Processing prompt analysis for request {request_id}")
    
    try:
        # Create Strands Agent with explicit Bedrock model
        from strands.models import BedrockModel
        
        # Use Amazon Nova Lite which doesn't require marketplace subscription
        bedrock_model = BedrockModel(
            model_id="us.amazon.nova-lite-v1:0",
            temperature=0.3,
            max_tokens=4000,
        )
        
        code_analysis_agent = Agent(
            model=bedrock_model,
            system_prompt=CODE_ANALYSIS_SYSTEM_PROMPT,
            tools=[http_request],
        )
        
        # Process the prompt through the agent
        response = code_analysis_agent(prompt)
        analysis_result = str(response)
        
        processing_time = time.time() - start_time
        
        return {
            'status': 'success',
            'message': 'Code analysis completed',
            'request_id': request_id,
            'analysis': analysis_result,
            'processing_time_seconds': round(processing_time, 3),
            'input_prompt': prompt
        }
            
    except Exception as e:
        logger.error(f"Error in Strands Agent analysis: {str(e)}")
        return {
            'status': 'error',
            'message': f"Analysis failed: {str(e)}",
            'request_id': request_id
        }

def handle_s3_event(event: Dict[str, Any], context, start_time: float) -> Dict[str, Any]:
    """Handle S3 events from EventBridge."""
    request_id = context.aws_request_id if context else "unknown"
    
    logger.info(f"Processing S3 event for request {request_id}")
    logger.info(f"Event data: {json.dumps(event)}")
    
    try:
        # Extract S3 information from EventBridge event
        bucket_name = event.get('bucket')
        object_key = event.get('key')
        output_bucket = event.get('outputBucket')
        
        if not bucket_name or not object_key:
            error_msg = "Missing bucket name or object key in S3 event"
            logger.error(error_msg)
            return {'status': 'error', 'message': error_msg}
        
        logger.info(f"Analyzing file: s3://{bucket_name}/{object_key}")
        
        # Read the file from S3
        s3_client = boto3.client('s3')
        
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            file_content = response['Body'].read().decode('utf-8')
            file_size = response['ContentLength']
            
            logger.info(f"Successfully read file: {object_key} ({file_size} bytes)")
            
        except Exception as e:
            error_msg = f"Failed to read file from S3: {str(e)}"
            logger.error(error_msg)
            return {'status': 'error', 'message': error_msg}
        
        # Determine file type from extension
        file_extension = object_key.split('.')[-1].lower() if '.' in object_key else 'unknown'
        
        # Create analysis prompt
        analysis_prompt = f"""
        Analyze this {file_extension} code file: {object_key}
        
        File size: {file_size} bytes
        
        Code content:
        ```{file_extension}
        {file_content}
        ```
        
        Please provide a comprehensive analysis including:
        1. Code quality assessment
        2. Security vulnerabilities
        3. Performance considerations
        4. Best practices recommendations
        5. Specific improvements with code examples
        """
        
        # Create Strands Agent with explicit Bedrock model
        from strands.models import BedrockModel
        
        bedrock_model = BedrockModel(
            model_id="us.amazon.nova-lite-v1:0",
            temperature=0.3,
            max_tokens=4000,
        )

        code_analysis_agent = Agent(
            model=bedrock_model,
            system_prompt=CODE_ANALYSIS_SYSTEM_PROMPT,
            tools=[http_request],
        )
        
        # Process the analysis
        logger.info("Starting AI analysis...")
        response = code_analysis_agent(analysis_prompt)
        analysis_result = str(response)
        
        # Generate output file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_key = f"analysis/{object_key.replace('/', '_')}_{timestamp}_analysis.md"
        
        # Save analysis result to output bucket
        if output_bucket:
            try:
                s3_client.put_object(
                    Bucket=output_bucket,
                    Key=output_key,
                    Body=analysis_result,
                    ContentType='text/markdown',
                    Metadata={
                        'source-bucket': bucket_name,
                        'source-key': object_key,
                        'analysis-timestamp': timestamp,
                        'file-type': file_extension,
                        'request-id': request_id
                    }
                )
                logger.info(f"Analysis saved to: s3://{output_bucket}/{output_key}")
                
            except Exception as e:
                logger.error(f"Failed to save analysis to S3: {str(e)}")
                # Continue processing even if save fails
        
        processing_time = time.time() - start_time
        
        result = {
            'status': 'success',
            'message': 'S3 code analysis completed',
            'request_id': request_id,
            'input': {
                'bucket': bucket_name,
                'key': object_key,
                'file_size': file_size,
                'file_type': file_extension
            },
            'output': {
                'bucket': output_bucket,
                'key': output_key if output_bucket else None,
                'analysis_length': len(analysis_result)
            },
            'processing_time_seconds': round(processing_time, 3),
            'analysis_preview': analysis_result[:500] + "..." if len(analysis_result) > 500 else analysis_result
        }
        
        logger.info(f"S3 analysis completed successfully in {processing_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"Error in S3 event analysis: {str(e)}")
        return {
            'status': 'error',
            'message': f"S3 analysis failed: {str(e)}",
            'request_id': request_id
        }