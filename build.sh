docker stop $(docker ps -a -q -f since=mysql); 
count=$(docker ps -a -q -f since=mysql | wc -l)
if (($count >= 5)); then
    echo "Before starting. Cleaning up workbench"
    docker system prune -f 
fi
docker build . -t scoring; docker run -dp 80:5000 -p 5001:5001 scoring:latest
