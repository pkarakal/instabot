<h1 align="center">instabot</h1>

This is an experimental Instagram bot created to be used to help users tag
their friends in posts. It uses the Instagram API to make HTTPS requests and
doesn't need either Selenium or a browser to be used. 

## Requirements
* Python
* Docker (optional)

## Instructions
*  First clone the project
    ```shell
   $ git clone git@github.com:pkarakal/instabot.git
    ``` 
   
### Natively
If you choose to run this natively, follow the below instructions:

*  Install python libraries necessary
    ```shell
   $ pip install -r requirements.txt
    ```
*  Replace the necessary fields in file.yaml with your desired values
*  Run the program using
   ```shell
   $ python -m instabot -f file.yaml
   ```
*  Alternatively, you can use cli arguments, but it isn't recommended mostly
   for security reasons. To see the arguments the program takes, type
   ```shell
   $ python -m instabot --help
   ```
   
### Docker
If you choose to run this in a container, follow the instructions below.
*  Replace the necessary fields in file.yaml with your desired values
*  Build the image
   ```shell
   $ docker build -t instabot:latest . 
   ```
*  Create and run the container
   ```shell
  $ docker run --name instabot -d instabot:latest
   ```
*  If you choose to go with cli arguments, just build the dockerfile with cli using
   ```shell
   $ docker build -t instabot:cli -f Dockerfile.cli .
   ```
*  Create and run the container
   ```shell
  $ docker run --name instabot -d instabot:latest python -m instabot [ARGS]
   ```
