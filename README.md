# DirectoryMinWage

docker build -t name:DictWage ./

docker run -p 8060:8060 -e BIND="0.0.0.0:8060" -v /opt/DirectoryMinWage/data:/app/data name:DictWage