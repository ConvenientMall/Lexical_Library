# Lexical Libary

Lexical Libary is a webapp for conlang documentation. Allow users to create public and private dictionaries that can be filled with invented vocabulary.  

### Prerequisites

Py4web and vue.js needed.

## Deployment
<sub>Taken from [py4web documentation](https://py4web.com/_documentation/static/en/chapter-03.html)</sub>

Login into the Gcloud console and create a new project. You will obtain a project id that looks like “{project_name}-{number}”.

In your local file system make a new working folder and cd into it:
```
mkdir gae
cd gae
```
Copy the files from py4web (assuming you have the source from github)
```
cp /path/to/py4web/development_tools/gcloud/* ./
```
Copy or symlink your apps folder into the gae folder, or maybe make a new apps folder containing an empty __init__.py and symlink the individual apps you want to deploy. You should see the following files/folders:
```
Makefile
apps
  __init__.py
  ... your apps ...
lib
app.yaml
main.py
```
Install the Google SDK, py4web and setup the working folder:
```
make install-gcloud-linux
make setup
gcloud config set {your email}
gcloud config set {project id}
```
(replace {your email} with your google email account and {project id} with the project id obtained from Google).

Now every time you want to deploy your apps, simply do:
```
make deploy
```
You may want to customize the Makefile and app.yaml to suit your needs. You should not need to edit main.py.

## Built With
* [py4web](https://py4web.com/_documentation/static/en/chapter-01.html) - The web framework used
* [vue.js](https://vuejs.org/guide/introduction.html) - JavaScript framework used
