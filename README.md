# Alertbot-V2
<img src="BachehBot.jpeg" alt="Project Logo" width="350"/>

## Overview

Alertbot is an API designed to receive alerts from multiple sources such as Prometheus and Splunk, and then dispatch those alerts to various destinations including Telegram and SMS endpoints. This project aims to streamline the alerting process for operations teams, providing a centralized point of management for alerts and notifications.

## Features

- **Multi-source Alert Reception**: Seamlessly receive alerts from Prometheus, Splunk, and additional monitoring solutions.
- **Versatile Alert Dispatching**: Notify your team via Telegram, SMS, and other potential endpoints.
- **Prometheus Metrics**: Exposing a lot of useful metric providing insights into number of notification.
- **Saving All Alerts**: Saving the alerts to database for long-term overview of our alerts.
- **Scalable Design**: Built to accommodate increasing alert volume without compromising performance.
- **Customizable**: Easily add new alert sources or notification destinations according to your needs.

## Getting Started

### Prerequisites

- You can checkout requirements.txt for it. 

### Installation

1. Clone the repository:

    ```bash
    git clone git@github.com:Erfan-Razzaghi/AlertBot.git
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Configure environment variables. Create a `.env` file in the project src/alertbot and set your configurations:

    ```env
    TG_BOT_TOKEN=<YOU CAN USE ASSET BOT TOKEN>
    TG_GROUP_TEST=-<YOUR_TELEGRAM_TEST_GROUP>
    KAVENEGAR_API_KEY=<KAVEH NEGAR API KEY>
    LOG_LEVEL=INFO
    ENVIRONMENT=STAGING
    ```

4. Start the server:

    ```bash
    python3 main.py
    ```

You can join the test group by using the link [here](https://t.me/+xQjm1LjvWZs0ZmQ0).


5. (Optional) You may also use the docker-compose.yaml file.


## Contributing

1. Fork the project
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
