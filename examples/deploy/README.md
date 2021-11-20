# Deploy API within colab
* [CV streamlit examples](CV)
* [NLP streamlit examples](NLP)
* [Tabular streamlit examples](Tabular)

## How to use these templates

### In Jupyter / Colab

1. Install & import the necessary dependencies and unpackai code
```python
!pip install unpackai[deploy]
from unpackai.deploy.app import deploy_app
```
2. Create your app (in a dedicated cell)
```python
%%writefile app.py
# copy-paste here the code of the template
# and modify it to match your need
```
3. Launch the app (in a new cell)
```python
deploy_app()
```

Note: if you want to save your app to a filename other than *app.py*
(we assume you want to save to *myapp.py*),
you can do so by changing following lines:
```python
%%writefile myapp.py
...
deploy_app("myapp.py")
```

> _**Note**: you can update the code of your app in Google Colab by going to the file explorer (menu on the left) and double-ing on the file of the app.
> A window will be opened on the right side where you can edit and save your modifications_


### Directly locally

You can simply:

1. Copy-paste the template to the location you want to use it (we assume it is saved in path *myapp/app.py*)
2. Modify if needed
3. Launch `streamlit` with the following command line (from any terminal or Windows "cmd"): `streamlit run myapp/app.py`

Streamlit will open a window of your browser to show the app.

Once it is running, you can modify the code of the app, and it can be updated easily in the browser.
