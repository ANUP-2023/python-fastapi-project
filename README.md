# FastAPI Deployment on Ubuntu (Run as Non-root User with systemd)

This guide walks you through deploying a FastAPI application on an Ubuntu EC2 instance, running as the dedicated `ubuntu` user for best practices and using systemd to manage your app. The instructions cover project setup, virtual environment usage, basic FastAPI code, service configuration, endpoint testing, and pushing your code to GitHub using SSH.

---

## 🗂️ 1. Project Setup and Python Environment

<details>
<summary>Why this order?</summary>

1. **Create a project directory** so all files are organized in one place.
2. **Install Python virtual environment package** to isolate your project dependencies from system Python.
3. **Create and activate the virtual environment** inside your project directory.
4. **Install dependencies** (FastAPI, Uvicorn) inside the virtual environment, keeping them isolated.
</details>

---

### Step 1: Switch to `ubuntu` user

```sh
sudo -i -u ubuntu
```

### Step 2: Create your project directory

```sh
cd ~
mkdir fastapi-project
cd fastapi-project
```

> Your code will live in `/home/ubuntu/fastapi-project`.

### Step 3: Install Python and venv tools

```sh
sudo apt update
sudo apt install -y python3-pip python3-venv
```

### Step 4 (Optional): Verify Python/pip

```sh
python3 -V
pip3 -V
which python3
which pip3
```

### Step 5: Create & Activate Virtual Environment

```sh
python3 -m venv venv
source venv/bin/activate
```

### Step 6: Install FastAPI and Uvicorn

```sh
pip install fastapi uvicorn
```

_Check installed packages:_

```sh
pip freeze
pip show fastapi
pip show uvicorn
```

---

## 📝 2. Example FastAPI App

Create the file `app.py`:

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def hello():
    return "Hello from EC2! Running FastAPI Application via systemd!"

@app.get("/health")
def health():
    return JSONResponse(
        content={"status": "healthy", "app": "running"},
        status_code=200
    )
```

Test locally:

```sh
uvicorn app:app --host 0.0.0.0 --port 8000
```

You can now visit `http://localhost:8000` or use `curl` as below.

---

## ⚡ 3. Example Endpoint Tests

Test endpoints while the server is running:

```sh
curl http://localhost:8000/
# Output: Hello from EC2! Running FastAPI Application via systemd!

curl http://localhost:8000/health
# Output: {"status":"healthy","app":"running"}
```

---

## ⚙️ 4. Deploy with systemd

### 4.1. Create a systemd service file

Create `/etc/systemd/system/fastapi.service` (with `sudo`):

```ini
[Unit]
Description=FastAPI application (run as ubuntu via uvicorn)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/fastapi-project
ExecStart=/home/ubuntu/fastapi-project/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

> Adjust the `WorkingDirectory` and `ExecStart` paths if your setup differs.  
> Find the full path to uvicorn by running `which uvicorn` inside your venv.

### 4.2. Reload systemd and start service

```sh
sudo systemctl daemon-reload
sudo systemctl start fastapi.service
sudo systemctl enable fastapi.service
```

Check service status and logs:

```sh
systemctl status fastapi.service
journalctl -u fastapi.service -f
```

Stop the service:

```sh
sudo systemctl stop fastapi.service
```

---

## 🌐 5. Accessing Your API

Test endpoints from your EC2 server:

```sh
curl http://localhost:8000/
curl http://localhost:8000/health
```

To test from outside EC2:

1. Get your public IP:

    ```sh
    curl ifconfig.me
    ```

2. Test from outside (replace `<your-ec2-public-ip>`):

    ```sh
    curl http://<your-ec2-public-ip>:8000/
    curl http://<your-ec2-public-ip>:8000/health
    ```

To get the internal (private) IP (for VPC/internal use):

```sh
hostname -I
curl http://<your-ec2-private-ip>:8000/
curl http://<your-ec2-private-ip>:8000/health
```

---

## 🗃️ 6. Version Control & GitHub SSH Setup

### 6.1. Create `requirements.txt`

```sh
pip freeze > requirements.txt
```

### 6.2. Add `.gitignore`

```sh
cat <<EOF > .gitignore
__pycache__
venv
EOF
```

### 6.3. Initialize Git, SSH Keys, and Set Remote

> **IMPORTANT:** SSH keys are _per user_. If you generate an SSH key as `ubuntu`, only the `ubuntu` user can use it to authenticate to GitHub (the key is stored in `/home/ubuntu/.ssh/`). To use SSH as any other user, generate or copy SSH keys in that user's `~/.ssh/` directory.

**a. Generate a SSH key as `ubuntu`:**

```sh
ssh-keygen
cat /home/ubuntu/.ssh/id_ed25519.pub
```

Add the public key to your GitHub account’s SSH keys.

**b. Test SSH connection:**

```sh
ssh -T git@github.com
```

**c. Init git repo and add remote:**

```sh
git init
git config --global user.name "anup.kumar"
git config --global user.email "anup.kumar01@gmail.com"
git remote add origin git@github.com:ANUP-2023/python-fastapi-project.git # ← update to your repo
git branch -M master
```

**d. Commit and push:**

```sh
git add .
git commit -m "added Fastapi Project and README.md file"
git push -u origin master
```

---

## 📝 Notes

- Replace repository URLs, project paths, and user info as needed.
- Make sure security groups allow inbound access on port 8000 for remote testing.
- For production, consider using a reverse proxy (e.g., Nginx) and HTTPS.

---

> **Summary:**  
> SSH keys are _per user_. If you generate an SSH key as `ubuntu`, only the `ubuntu` user will be able to use it for GitHub authentication (stored in `/home/ubuntu/.ssh/`). To allow access from another user, create (or copy) a key in that user's `~/.ssh/` directory.

