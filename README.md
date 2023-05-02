# PI2: End-to-end Interactive Interface Generation from Queries

[![License](https://www.gnu.org/graphics/gplv3-127x51.png)](https://www.gnu.org/licenses/gpl-3.0.en.html)

> Give me your task query, I will give you an interactive interface app!

Interactive visualization interfaces (or simply interfaces) are critical in nearly every stage of data management—including data cleaning, wrangling, modeling, exploration and communication. It requires considerable expertise and trial-and-error to design and implement an interface. ***PI2 is a system which helps you automatically generate interactive visualization from SQL queries - [the PI2 paper](https://dl.acm.org/doi/pdf/10.1145/3514221.3526166) or Natural Language queries - [the NL2INTERFACE paper](https://arxiv.org/pdf/2209.08834.pdf).*** It helps designers help designers more quickly and effectively translate analysis tasks into interfaces.
 

# Glance on the DEMO (Sound On)

https://user-images.githubusercontent.com/13096451/235589850-26987b4f-6b6c-40e9-9a89-8f52afb2e5ea.mp4


# Environment Setup

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

- Optional: Set up OpenAI API key to enable natural language queries.

      export OPENAI_APIKEY="YOUR_OPENAPI_API_KEY"
        

# Run PI2
You can choose to try using PI2 on a webpage or in a jupyter notebook setting. The default database is located at `examples/pi.db`. 

## Run web demo

To run the web demo, start a server locally and visit `https://localhost:8000/`

    cd pi-server
    python server.py

You can type in queries and PI2 will generate interfaces.  `examples/logs` lists some example queies for your reference. 

## Run Jupyter Lab

To run PI with jupyter lab, you need to start two terminal windows. 

In one terminal, start the PI server.

    cd pi-server
    python server.py   

In the other terminal, start the jupyter lab server.

    # under PI root folder
    jupyter lab

You can try the jupyter demo `examples/covid_demo.ipynb` or type in your own queries.
       
### Troubleshot

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
    
    
    
## Paper and Citation
* Yiru Chen, and Eugene Wu. "PI2: End-to-end interactive visualization interface generation from queries." Proceedings of the 2022 International Conference on Management of Data. 2022.
* Yiru Chen, Ryan Li, Austin Mac, Tianbao Xie, Tao Yu and Eugene Wu. “NL2INTERFACE: Interactive Visualization Interface Generation from Natural Language Queries.” IEEE Visualization Conference NLVIZ Workshop, 2022
* Jeffrey Tao, Yiru Chen, and Eugene Wu. "Demonstration of PI2: Interactive visualization interface generation for sql analysis in notebook." Proceedings of the 2022 International Conference on Management of Data. 2022.
* Yiru Chen, and Eugene Wu. “Monte Carlo Tree Search for Generating Interactive Data Analysis Interfaces.” Proceedings of the AAAI-20 Workshop on Intelligent Process Automation. 2020


