docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' redis-instance
