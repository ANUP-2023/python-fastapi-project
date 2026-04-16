# Python FastAPI Project: Clone, Docker Build, ECR Push, and Run Container Guide

This guide provides step-by-step instructions for cloning your FastAPI application repository, building a Docker image, pushing it to AWS ECR, deploying the container, and verifying your application's endpoints both from the host and within the container.

---

## 1. Prerequisites

Ensure you have an Ubuntu server with sudo privileges.

### Install Required Packages

```sh
sudo apt update
sudo apt install git docker.io unzip net-tools -y
```

### Install AWS CLI

```sh
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

---

## 2. Clone Your FastAPI Project at the Correct Location

Clone the FastAPI repository before building the Docker image and running the container. Ensure all commands are executed from within the project directory.

### Generate SSH Keys (if needed)

SSH keys are needed if the FastAPI project's GitHub repository uses SSH-based authentication. Generate an SSH key pair and add the public key to your GitHub account or repository to enable passwordless, secure access for `git clone`. This is important for private or internal repositories.

```sh
ssh-keygen
cat ~/.ssh/id_ed25519.pub
```
> **Note:** Add the above public key to your GitHub account under SSH keys or in the repository's deploy keys section to allow this server to access the repository via SSH.

### Test SSH Connection to GitHub

```sh
ssh -T git@github.com
```

### Clone the FastAPI Project

Clone the repository into an appropriate directory (e.g., `~/fastapi-app`):

```sh
cd ~
git clone -b docker git@github.com:ANUP-2023/python-fastapi-project.git fastapi-app
cd fastapi-app
```

(Optional) List files and check your Dockerfile is in the correct location:

```sh
ls -l
```

Example output:
```
total 36
drwxr-xr-x 3 root root 4096 Apr 16 18:26 ./
drwx------ 7 root root 4096 Apr 16 18:26 ../
drwxr-xr-x 8 root root 4096 Apr 16 18:26 .git/
-rw-r--r-- 1 root root   17 Apr 16 18:26 .gitignore
-rw-r--r-- 1 root root  207 Apr 16 18:26 Dockerfile
-rw-r--r-- 1 root root 5712 Apr 16 18:26 README.md
-rw-r--r-- 1 root root  333 Apr 16 18:26 app.py
-rw-r--r-- 1 root root  234 Apr 16 18:26 requirements.txt
```

View the contents of your Dockerfile:
```sh
cat Dockerfile
```

Sample `Dockerfile`:
```
FROM python:3.10-slim

WORKDIR /app

COPY app.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```
# Note: Add a `.dockerignore` file to your project root
**Why is `.dockerignore` important?**

Create a `.dockerignore` file in your project root directory. This tells Docker which files and directories to exclude when building your image. Using `.dockerignore` helps to:

- Prevent large files or unnecessary directories (like `.git`, `__pycache__`, `.gitignore`, or local data) from being copied into your Docker image, making it smaller and more secure.
- Avoid leaking sensitive files or credentials into the image by accident.
- Speed up the Docker build process.

Example `.dockerignore`:
```
.git
__pycache__/
*.pyc
*.pyo
*.pyd
*.env
*.DS_Store
```

---

## 3. Build Docker Image (In the Cloned Project Directory)

Make sure you are inside the cloned project directory before running the Docker build command.

```sh
# You should be in ~/fastapi-app/
pwd  # Confirm you are in the right place
docker build -t fastapi:v1 .
docker images
```
> Confirm that `fastapi:v1` appears in the output list.

---

## 4. Create AWS ECR Repository

Create the repository in ECR (only needed once):

```sh
aws ecr create-repository --repository-name fastapi --image-tag-mutability IMMUTABLE --image-scanning-configuration scanOnPush=true
```

---

## 5. Authenticate Docker to AWS ECR

```sh
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 659587495719.dkr.ecr.ap-south-1.amazonaws.com
```

---

## 6. Tag and Push the Image to ECR

**Tag your image:**

```sh
docker tag fastapi:v1 659587495719.dkr.ecr.ap-south-1.amazonaws.com/fastapi:latest
docker images
```
_Verify both local and ECR-tagged images are listed._

**Push the image:**

```sh
docker push 659587495719.dkr.ecr.ap-south-1.amazonaws.com/fastapi:latest
```

---

## 7. Run the Docker Container (from ECR Image)

Run the container (ensure any port mappings or volumes are as per your project’s needs):

```sh
docker run -d --name fastapi-api --restart on-failure -p 8000:8000 659587495719.dkr.ecr.ap-south-1.amazonaws.com/fastapi:latest
```

Verify it's running:

```sh
docker ps -a
docker logs -f fastapi-api
```

---

## 8. Debugging and Troubleshooting

To enter the running container for debugging (as root):

```sh
docker exec -it -u root fastapi-api bash
# (Inside the container:)
apt update && apt install net-tools curl -y
netstat -tunlp | grep 8000
curl http://localhost:8000/
curl http://localhost:8000/health
```

Or, as the default user:

```sh
docker exec -it fastapi-api bash
netstat -tunlp | grep 8000
curl http://localhost:8000/
curl http://localhost:8000/health
```

_Note: If Bash isn't available, you may need to use `sh` instead._

---

## 9. API Health Checks

### Test endpoints from the server (outside the container)

Verify the service is working with curl:

```sh
curl http://localhost:8000/
# Example output: Hello from EC2! Running FastAPI Application via systemd!

curl http://localhost:8000/health
# Example output: {"status":"healthy","app":"running"}
```

### Test endpoints from inside the running container

```sh
docker exec -it fastapi-api bash
curl http://localhost:8000/
# Example output: Hello from EC2! Running FastAPI Application via systemd!

curl http://localhost:8000/health
# Example output: {"status":"healthy","app":"running"}
```

Testing both inside and outside the container ensures that the container and network setup are correct.

---

## Testing Endpoints from Outside the EC2 Server (from Your Browser)

You can check that your FastAPI app is accessible over the Internet using a web browser:

1. **Find your EC2 instance's public IP address:**

    ```sh
    curl ifconfig.me
    ```

2. **In your browser** (not from the server), navigate to:

    - `http://<your-ec2-public-ip>:8000/`
    - `http://<your-ec2-public-ip>:8000/health`

   You should see:
   - The greeting message at `/`
   - The JSON health status at `/health`

> _Note: You can't use `curl` from your local machine unless you have a compatible shell environment. Simply open the URLs above in your browser. If your security group (firewall) blocks port 8000, you may need to open it in AWS._

If your EC2 has a private IP for VPC/internal access:

1. **Get the private IP on the EC2 server:**

    ```sh
    hostname -I
    ```

2. **From another host in the same VPC**, open:

    - `http://<your-ec2-private-ip>:8000/`
    - `http://<your-ec2-private-ip>:8000/health`

---

## Notes

- Always clone your repo to the intended directory before running Docker build/run.
- Store environment variables and secrets securely.
- Remove unused containers/images to save disk space.
- Integrate automation or CI/CD for repeatable deployments.

---

_Cloning the repo at the correct location, then building and running the Docker container in that directory, ensures repeatable, portable deployments of your Python FastAPI app with AWS ECR._

