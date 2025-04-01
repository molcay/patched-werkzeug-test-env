# Patched Werkzeug Test Environment

## Usage
- You can run the `create_test_files.py` file with python to create the test files.
- After creating the test files, you can run the following to start the environment:
```bash
docker compose up -d 
```

## Folder Structure
```bash
.
├── app #------------------------------> Application folder root
│   ├── templates #--------------------> HTML templates for UI (file upload form)
│   │   ├── form.html
│   │   └── index.html
│   ├── app.py #-----------------------> entry point for the Werkzeug Application
│   ├── Dockerfile
│   ├── original-requirements.txt #----> dependency file for original werkzeug (Werkzeug v2.2.3) 
│   ├── patched-requirements.txt #-----> dependency file for patched werkzeug (Werkzeug-patched v2.2.4)
│   ├── v2_3_7-requirements.txt #------> dependency file for Werkzeug v2.3.7
│   └── v2_3_8-requirements.txt #------> dependency file for Werkzeug v2.3.8
├── test-files/ #----------------------> Folder to store the test files (will be created automatically)
├── create_test_files.py #-------------> Python script to create the test files
├── docker-compose.yml
├── .dockerignore
├── .gitignore
└── README.md
```