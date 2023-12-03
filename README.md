# DeepRosa: Experimentation Environment for Clustering Algorithms

## Overview

Welcome to DeepRosa, an experimentation environment designed for testing and exploring clustering algorithms. DeepRosa provides a playground for researchers, data scientists, and enthusiasts to experiment with various clustering techniques, visualize data, and analyze algorithm performance.

## Features

- **Clustering Algorithms:** DeepRosa supports a variety of clustering algorithms, allowing users to compare and contrast their effectiveness on different datasets.
  
- **Interactive Data Visualization:** Visualize clustering results and relevant data through interactive plots and charts.

- **Experimentation Workspace:** A dedicated workspace for experimenting with algorithm parameters, input data, and observing real-time results.

- **Export and Share:** Save your experiments, results, and visualizations for further analysis or sharing with others.

## Getting Started

### Installation

1. Clone the DeepRosa repository to your local machine:

   ```bash
   git clone https://github.com/Liveir/DeepRosa.git

2. Navigate to the DeepRosa directory:

   ```bash
   cd DeepRosa
3. Initialize a Python virtual environment:

   ```bash
   python -m venv venv
   venv/scripts/activate
   
4. Install dependencies. Make sure you are using the virtual environment created in the previous step:
   
   ```bash
   pip install -r requirements.txt

5. Package the application into an executable:
   
   ```bash
   pyinstaller --noconfirm --onedir --add-data "venv/Lib/site-packages/customtkinter:customtkinter/" --add-data "Models:models" --add-data "Views:views" --add-data "Server:server" --noconsole --name DeepRosa --icon=Assets/dprosa_icon.ico dprosa.py 

5. The executable is located in the generated dist/ folder.

### Usage

1. Run the script:

   ```bash
   python dprosa.py

2. Or, launch the executable
   ```bash
   dist/DeepRosa/DeepRosa.exe

## Supported Clustering Algorithms

* K-Means Clustering

* Agglomerative Hierarchical Clustering

* Affinity Propagation Clustering

## Future Implementations

* Word Embedding Models

* Recommender System Models

## Contribution Guidelines

We welcome contributions to enhance DeepRosa and make it an even more powerful tool for experimentation. Future directions include the implementation of word embedding models and recommender systems to enhance the clustering and predictive capacities of DProSA.

## License

DeepRosa is licensed under the MIT License.

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.

Happy experimenting with DeepRosa! 🚀




