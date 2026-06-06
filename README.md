# Overview
This is a script to pull [OsmAnd](https://www.osmand.net) maps files in batch from [OsmAnd's Local Indexes List](https://download.osmand.net/list.php). You can then copy these from the downloaded location into the directory on your mobile device(s). Allowing you to only download the maps once for multiple devices versus on each device every update. When I go on road trips, camping, hiking; I'll typically have a backup device in water resistant bag with OsmAnd for offline maps. This allows me to update both devices once. 

# Notes on Function
This uses BeautifulSoup4 and regular expressions to grab relevant zip files, downloads them, and then extracts them to a files folder. Since this uses regular expressions you can create a batch by providing it northamerica, europe, canada, us_, us_california, etc. A seperate file ```osmAndBatch.py``` for crafting your own list of specific maps is included. 

# Getting started
To get going with this do the following in order notes for both linux and windows are shown. This was run on windows 11 machine with python 3.14.

1. Setup your virtual envrionment:
   - Windows -> ```python -m venv .venv```
   - Linux -> ```python -m venv .venv```

2. Source the environment:
   - Windows -> ```.\\.venv\Scripts\activate```
     -  Note you may need set execution policy by running ```Set-ExecutionPolicy Unrestricted -Scope Process```
   - Linux -> ```source .venv/bin/activate```

3. Install python packages:
   - Both -> ```pip install -r requirements.txt```

4. Run from command line and grab a small state to test:
   - Windows -> ```python .\osmAnd.py us_rhode```
   - Linux -> ```python osmAnd2.py us_rhode```
