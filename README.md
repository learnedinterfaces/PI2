# Precision Interfaces

This is the repo for the Precision Interfaces pipeline.

> Give me your query log, I will give you an interactive app!

The codebase consists of three components:

* [pi-server](./pi-server): contains the Python3 code that implements the current monte-carlo tree-based search algorithm for precision interfaces.
* [pi-client](./pi-client): contains the javascript front-end engine, which takes an interface specification as input, and renders+executes it in the browser.
* [pi-jupyer](./pi-jupyter): contains the jupyter lab extension of PI.


# Environmen Setup

- Install `conda`: https://docs.conda.io/en/latest/miniconda.html
- Create conda environment:

        conda create -n pi --override-channels --strict-channel-priority -c conda-forge -c nodefaults jupyterlab=3 cookiecutter nodejs jupyter-packaging git
        conda activate pi

- In `src/pi-client`, run:

      npm install .
      npm run build
      npm run build-library
      jlpm link
      
- In `src/pi-jupyter`, run:

      npm install .
      jlpm link pi-client
      jlpm run build
      jlpm run watch
      (press <ctrl-c> to kill `jlpm run watch` when observe "webpack xxx compiled successfully")
      
- In `src/pi-server`, run:

      pip install -r requirements.txt

- Optional: Set up OpenAI API key to enable NL to query.

      export OPENAI_APIKEY="YOUR_OPENAPI_API_KEY"
        

# Run Presision Interface

## Run web demo

To run the web demo, start a server locally and visit `https://localhost:8000/`

    cd pi-server
    python server.py

You can try the demo with SQL logs from `examples/logs`.

## Run Jupyter Lab

To run PI with jupyter lab, you need to start two terminal windows. 

In one terminal, start the PI server.

    cd pi-server
    python server.py   

In the other terminal, start the jupyter lab server.

    # under PI root folder
    jupyter lab

You can try the jupyter demo `examples/covid_demo.ipynb`.
       
# Misc

If the Cell Toolbars block the checkboxes for generating interface, edit Jupyter configuration to delete the toolbar buttons. The configuration file is typically located at `~/miniconda3/envs/pi/share/jupyter/lab/schemas/@jupyterlab/cell-toolbar-extension/plugin.json`.

Change

    "Cell": [
      {
        "name": "duplicate-cell",
        "command": "notebook:duplicate-below"
      },
      { "name": "move-cell-up", "command": "notebook:move-cell-up" },
      { "name": "move-cell-down", "command": "notebook:move-cell-down" },
      {
        "name": "insert-cell-above",
        "command": "notebook:insert-cell-above"
      },
      {
        "name": "insert-cell-below",
        "command": "notebook:insert-cell-below"
      },
      {
        "command": "notebook:delete-cell",
        "icon": "ui-components:delete",
        "name": "delete-cell"
      }
    ]

To

    "Cell": [
    ]
