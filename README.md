For linux:
- sudo apt update
- sudo apt install docker.io docker-compose
- sudo systemctl enable --now docker
- For macOS/Windows: Install Docker Desktop.

Build the Docker Image
- docker compose build
- docker compose up

Performance:
- Scraped 100 entries in 14.64 seconds (~6.83 req/s) using Selenium
- Scraped 100 entries in 1.90 seconds (~52.59 req/s) using json
