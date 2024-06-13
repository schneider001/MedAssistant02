#!/bin/bash

set -e

image_name="medassist-img"
container_name="medassist-cont"
username="user"  
PORT=8001
NGINX_PORT=80

docker volume create pgdata
docker volume create medassistant_images

build_image() {
    docker build --build-arg PORT=$PORT -t $image_name .
}

run_container() {
    if [ $(docker ps -a -f name=$container_name | grep -w $container_name > /dev/null; echo $?) = 0 ]; then
        docker stop $container_name
        docker rm $container_name
    fi
    docker run --name $container_name -v pgdata:/var/lib/postgresql -v medassistant_images:/var/www -p $PORT:$PORT -p $NGINX_PORT:$NGINX_PORT -d $image_name
}

remove_container() {
    if [ $(docker inspect -f '{{.State.Running}}' $container_name) = "true" ]; then
        docker stop $container_name
    fi
    docker rm $container_name
}

show_logs() {
    docker logs $container_name
}

print_help() {
    echo "Usage: $0 [OPTION]..."
    echo "Manage your Docker container for the Medassistent app."
    echo ""
    echo "Options:"
    echo "-r    Remove the Docker container"
    echo "-b    Build and run the Docker container"
    echo "-l    Show the logs of the Docker container"
    echo "-h    Display this help message"
}

while getopts "rblh" opt; do
    case ${opt} in
        r) 
            remove_container
            ;;
        b) 
            build_image
            run_container
            ;;
        l)
            show_logs
            ;;
        h) 
            print_help
            exit 0
            ;;
        \?) 
            echo "Invalid option: $OPTARG" 1>&2
            print_help
            exit 1
            ;;
    esac
done

if [ $OPTIND -eq 1 ]; then
    build_image
    run_container
    while ! docker container inspect --format '{{.State.Health.Status}}' $container_name | grep healthy > /dev/null; do   
		sleep 0.1
	done
	echo "Service started, please open http://127.0.0.1:$PORT in your browser."
fi
