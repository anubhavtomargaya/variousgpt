###
Link : https://microsoft.github.io/autogen/docs/installation/Docker/#step-1-install-docker

###  Install docker 
- download docker desktop -> installs docker engine 
- add path for cmd
``` Add Visual Studio Code (code)
export PATH="$PATH:/Applications/Visual Studio Code.app/Contents/Resources/app/bin"
 Add Docker Desktop for Mac (docker)
export PATH="$PATH:/Applications/Docker.app/Contents/Resources/bin/"```

- start desktop to start docker daemon
`docker build -f .devcontainer/Dockerfile -t autogen_base_img https://github.com/microsoft/autogen.git#main`