# MedAssistant02

## English

### Prerequisites

1. **Docker**: Docker must be installed on your system. You can download Docker from the official website.
2. **Firefox**: The script opens Firefox to display the Django application. If Firefox is not installed or you prefer a different browser, you will need to open `http://127.0.0.1:8000` manually.

### How to use `run_docker.sh`

The `run_docker.sh` script is used to manage a Docker container for the Medassistent app.

Here are the options you can use with the script:

- `-r`: Remove the Docker container.
- `-b`: Build and run the Docker container.
- `-l`: Show the logs of the Docker container.
- `-h`: Display this help message.

If no options are passed, the script will build (or rebuild) the Docker image and container, check if the application is up, and open Firefox at `http://127.0.0.1:8000` if it's installed.

## Русский

### Предварительные условия

1. **Docker**: Docker должен быть установлен на вашей системе. Docker можно скачать с официального сайта.
2. **Firefox**: Скрипт открывает Firefox для отображения приложения Django. Если Firefox не установлен или вы предпочитаете другой браузер, вам нужно будет вручную открыть `http://127.0.0.1:8000`.

### Как использовать `run_docker.sh`

Скрипт `run_docker.sh` используется для управления контейнером Docker для приложения Medassistent.

Вот опции, которые вы можете использовать со скриптом:

- `-r`: Удалить контейнер Docker.
- `-b`: Собрать и запустить контейнер Docker.
- `-l`: Показать логи контейнера Docker.
- `-h`: Показать это сообщение.

Если опции не передаются, скрипт будет собирать (или пересобирать) образ Docker и контейнер, проверять, работает ли приложение, и открывать Firefox по адресу `http://127.0.0.1:8000`, если он установлен.
