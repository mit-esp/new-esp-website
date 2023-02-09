# MIT ESP new website
Previous code repository: https://github.com/learning-unlimited/ESP-Website/tree/mit-prod

A website to help manage the logistics of large short-term educational programs. This website was written by the [MIT Educational Studies Program](https://esp.mit.edu) to support [Splash](https://esp.mit.edu/learn/Splash) and other educational programs.

Documentation and setup instructions can be found at https://esp.mit.edu/espider-docs.

## Setup

Before setup, clone this repo, create a branch for yourself, and checkout into that branch:

```
git clone git@github.com:mit-esp/new-esp-website.git
cd new-esp-website
git checkout -b dev-[your name]
git push -u origin dev-[your name] (push your new branch to github)
```

File paths in these instructions are relative with respect to the repo's home directory.

### Docker Setup
Docker containers are a way to create/store environments to run programs consistently.

First, install Docker via whichever method your OS uses.

Once Docker is installed:
```
# Create the environment file, fill in values later
cp code/config/.env.example code/config/.env
```

To view your copy of the website:
```
# Build and run the docker file
docker build . -t espdev
docker run -itp 8000:8000 espdev

# Press Ctrl+C to exit.
```
Depending on how you installed Docker, you may need to run these in `sudo` mode.

Then, go to `localhost:8000` in your browser to see the website.

### Additional local setup
I (songk) have a separate conda environment for this. I haven't experimented with other venvs. 

See `code/README.md` for more

## Navigation
Information will not be saved in between Docker runs.

### Login information
Account type | Username | Password
-------------|----------|----------
   Admin     | admin    | password
   Teacher   | teacher  | password
   Student   | student  | password


