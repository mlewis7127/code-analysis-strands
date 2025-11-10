#!/usr/bin/env python3
"""
Package Lambda function and dependencies for deployment.
This script creates two ZIP files:
1. dependencies.zip - Contains all Python dependencies for the Lambda layer
2. app.zip - Contains the Lambda function code
"""

import os
import zipfile
import shutil
from pathlib import Path

def create_lambda_package():
    """Create Lambda deployment packages."""
    current_dir = Path.cwd()
    packaging_dir = current_dir / "packaging"
    
    # Directories
    app_dir = current_dir / "lambda"
    dependencies_dir = packaging_dir / "_dependencies"
    
    # Output ZIP files
    app_deployment_zip = packaging_dir / "app.zip"
    dependencies_deployment_zip = packaging_dir / "dependencies.zip"
    
    # Ensure packaging directory exists
    packaging_dir.mkdir(exist_ok=True)
    
    # Clean up existing packages
    if app_deployment_zip.exists():
        app_deployment_zip.unlink()
        print(f"Removed existing {app_deployment_zip}")
    
    if dependencies_deployment_zip.exists():
        dependencies_deployment_zip.unlink()
        print(f"Removed existing {dependencies_deployment_zip}")
    
    # Check if dependencies directory exists
    if not dependencies_dir.exists():
        print(f"Dependencies directory {dependencies_dir} not found.")
        print("Please run the following command first:")
        print("pip install -r requirements.txt --python-version 3.12 --platform manylinux2014_aarch64 --target ./packaging/_dependencies --only-binary=:all:")
        return False
    
    # Package dependencies into Lambda layer format
    print(f"Packaging dependencies from {dependencies_dir}...")
    with zipfile.ZipFile(dependencies_deployment_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(dependencies_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Lambda layers expect dependencies in the 'python' directory
                arcname = Path("python") / os.path.relpath(file_path, dependencies_dir)
                zipf.write(file_path, arcname)
                
    print(f"Created dependencies package: {dependencies_deployment_zip}")
    
    # Package application code
    print(f"Packaging application code from {app_dir}...")
    with zipfile.ZipFile(app_deployment_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(app_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, app_dir)
                zipf.write(file_path, arcname)
                
    print(f"Created application package: {app_deployment_zip}")
    
    # Display package sizes
    deps_size = dependencies_deployment_zip.stat().st_size / (1024 * 1024)
    app_size = app_deployment_zip.stat().st_size / (1024 * 1024)
    
    print(f"\nPackage sizes:")
    print(f"  Dependencies: {deps_size:.2f} MB")
    print(f"  Application:  {app_size:.2f} MB")
    print(f"  Total:        {deps_size + app_size:.2f} MB")
    
    return True

if __name__ == "__main__":
    print("Packaging Lambda function for deployment...")
    success = create_lambda_package()
    if success:
        print("\n✅ Packaging completed successfully!")
        print("\nNext steps:")
        print("1. npx cdk bootstrap  (if not already done)")
        print("2. npx cdk deploy")
    else:
        print("\n❌ Packaging failed!")
        exit(1)