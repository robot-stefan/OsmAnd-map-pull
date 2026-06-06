from osmAnd import fetch_and_process

# File to process a list for downloading.
# batch = ["us_","canada_","mexico_", "denmark_", "germany_", "france_", "_centralamerica", "spain_", "italy_", "portugal_", "gb_", "greenland_", "austria_", "netherlands_", 

batch = ["northamerica", "centralamerica", "world"]

def process_batch(batchList):
    results_all = []
    for name in batchList:
        print(f"Processing: {name}")
        results = fetch_and_process(name)
        results_all.extend(results)
    return results_all

process_batch(batch)