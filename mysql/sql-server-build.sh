docker run --name mysql \
            -p 3306:3306 \
            -e MYSQL_ROOT_PASSWORD='123456' \
            -e MYSQL_USER='scoring_engine' \
            -e MYSQL_PASSWORD='Changeme1!' \
            -d mysql:latest