
#clone repository
git clone https://github.com/khoado1/cpsc_488_assign_02.git

# build image, jackdo/cpsc488-higgs:1.0 personal repository
docker buildx build --platform linux/amd64 --load -t jackdo/cpsc488-higgs:1.0 .

#test locally
docker run --rm jackdo/cpsc488-higgs:1.0

docker push jackdo/cpsc488-higgs:1.0
kubectl apply -f deployment.yaml

brew install kubectl
brew install int128/kubelogin/kubelogin

kubectl version --client
kubectl oidc-login --help

#setup oidc_login 
mkdir -p ~/.kube
curl -fL https://nrp.ai/config -o ~/.kube/config
kubectl config get-contexts

#trigger login to nrp.ai
kubectl get nodes

#check namespace access: csuf-ecs-ryu
kubectl get pods -n csuf-ecs-ryu
kubectl auth can-i create jobs -n csuf-ecs-ryu

#deploy and run yaml
docker push jackdo/cpsc488-higgs:1.0
kubectl apply -f deployment.yaml
kubectl get jobs -n csuf-ecs-ryu
kubectl get pods -n csuf-ecs-ryu

#refresh and try again
kubectl oidc-login clean
cd /Users/albundy/dev/cpsc_488_assign_02
kubectl apply -f deployment.yaml

#new namespace: csuf-llm
kubectl get pods -n csuf-llm
kubectl auth can-i create jobs -n csuf-llm

kubectl apply -f deployment.yaml
kubectl get jobs -n csuf-llm
kubectl get pods -n csuf-llm

#collect logs



python3 -m venv .venv

#Step 5: Activate and use the environment
source .venv/bin/activate

python --version
which python

#To exit the environment when you are finished, simply run: [1] (https://www.youtube.com/watch?v=ApH52AIxqXU), [2] (https://www.youtube.com/watch?v=aBZ5pao8pKQ)
deactivate

# Navigate to your project folder
cd /path/to/your/local/project

# Initialize a local Git repository
git init

# Add all project files to the staging area
git add .

# Commit the files with an initial message
git commit -m "Initial commit"

# Rename your default branch to 'main' (standard for GitHub)
git branch -M main

# Link the remote repository as 'origin'
git remote add origin <PASTE_YOUR_GITHUB_URL_HERE>
branch: https://github.com/khoado1/cpsc_488_assign_01.git
git remote add origin https://github.com/khoado1/cpsc_488_assign_01.git

# Verify the remote URL is mapped correctly
git remote -v

git add .
git commit -m "Your commit message here"
git push -u origin main

python -m pip install python-dotenv openai

#run program
python verify_nautilus_llm_connection.py

OLD OLD OLD:
#setup python environment
brew install pyenv

#Step 2: Configure your shell
#check .zshrc first
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc


#Apply the changes to your current terminal session: [1] (https://www.youtube.com/watch?v=u62MifBPI5g)
source ~/.zshrc

#Step 3: Install the older Python version
#list first
pyenv install -l

#install target version
pyenv install 3.11.16

#Step 4: Create the isolated environment (venv)
cd /path/to/your/project
pyenv local 3.11.16
