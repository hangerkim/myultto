# Myultto

## Preparation
1. Build a docker image
    ```
    docker build -t myultto:latest .
    ```
1. Creeate a container
    ```
    docker create --name myultto -p [PORT]:80 -v [MOUNT DIRECTORY]:/app/instance myultto:latest
    ```

## Run
```
docker start myultto
```
