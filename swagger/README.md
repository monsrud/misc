
This was a learning exercise for me on how to use Swagger to generate an REST API client and service.
It uses swagger-codegen and swagger-ui Docker images.

Steps to use it are:

- Install Docker on your system and ensure it is functional.
- Run bash build.sh in the toplevel dirctory of the project.

API URL : http://localhost/practice/1.0.0/ui/


Scratch:

cat /proc/meminfo
cat /proc/cpuinfo
cat /proc/loadavg
docker rm $(docker ps -a -q)
docker rmi $(docker images -a -q)

cd /api/client
python setup.py install
pip3 install .
/api/client
