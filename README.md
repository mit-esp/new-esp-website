# MIT ESP
Previous code repository: https://github.com/learning-unlimited/ESP-Website/tree/mit-prod

A website to help manage the logistics of large short-term educational programs. This website was written by the [MIT Educational Studies Program](https://esp.mit.edu) to support [Splash](https://esp.mit.edu/learn/Splash) and other educational programs.

Before setup, clone this repo. File paths in these instructions are relative with respect to the repo's home directory.

## Docker Setup
First, install Docker via whichever method your OS uses.
```
# Create the environment file, fill in values later
cp code/config/.env.example code/config/.env

# Build and run the docker file
docker build . -t espdev
docker run -itp 8000:8000 espdev

# Press Ctrl+C to exit.
```
Go to `localhost:8000` in your browser to see the website.

## Local Setup
Go to code/README.md to run the site locally outside of Docker.
