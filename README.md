# Overview
This is a script to pull [OsmAnd](https://www.osmand.net) maps files in batch from [OsmAnd's Local Indexes List](https://download.osmand.net/list.php). You can then copy these from the downloaded location into the directory on your mobile device(s). Allowing you to only download the maps once for multiple devices versus on each device every update. When I go on road trips, camping, hiking; I'll typically have a backup device in water resistant bag with OsmAnd for offline maps. This allows me to update both devices once. 

I was able to vibe code, test, and deploy this in an afternoon with [duckai](https://duck.ai/) using GPT-5 mini and [VS Code](https://code.visualstudio.com/) for an editor. 

# Notes on Function
This uses [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/) and regular expressions to grab relevant zip files, downloads them, and then extracts them to a files folder. Since this uses regular expressions you can create a batch by providing it northamerica, europe, canada, us_, us_california, etc. A seperate file ```osmAndBatch.py``` for crafting your own list of specific maps is included. Progress bars for dowloading and extraction are implemented with [tqdm](https://pypi.org/project/tqdm/). Functions without tqdm are left commented out, but uncommenting these and updating the calls to point to them will allow you turn off the progress bar visualization .

This only pulls down the obf zip files and does not get the srtm files which give the topographical data. You will still need to manually download and manually run updates for these from within the app on each device.

# Getting started
To get going with this do the following in order. Notes for both linux and windows are shown. This was tested on a windows 11 machine with python 3.14 and an andorid phone.

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

5. For an android phone you will need to paste the contents of the created files folder to ```Android\data\net.osmand.plus\files``` either on the internal memory or sd card depending on which you use. 
