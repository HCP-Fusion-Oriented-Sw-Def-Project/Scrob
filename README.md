# Scrob

######
An automated tool to detect GUI changes for Android apps at the screen level.

## Requirement

######
* GUI data - screenshots and xml file.
* Python 3.7.6.
* All the other requirements are listed in the requirements.txt.

## Run Scrob
######
1. Take the script /codes/demo.py for example.
2. Use the function `read_ground_truth` to get the information created by `Scrob UI Viewer` manaully if necessary.
3. Use the function `get_scrob_result` to get result.
   * For non-list nodes, i.e., the nodes outside the slide list in a screen.
     * `re.get_single_nodes_result`
     * `re.save_single_results`
   * For list nodes, i.e., the nodes inside the slide list in a screen.
     * `re.get_list_nodes_result`
     * `re.save_list_results`
4. We can get the GUI change information from the node attributes.
        `self.real_changed_attrs = {
            'class': 0,
            'resource-id': 0,
            'text': 0,
            'content-desc': 0,
            'location': 0,
            'rel_location': 0,
            'size': 0,
            'color': 0
        }`
 5. Show the results the way you want, e.g.,  by `Scrob UI Viewer` or html.
