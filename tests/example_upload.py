#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json

import requests


# Main program ================================================================
if __name__ == '__main__':
    metadata = {
        "nazev": "Story of mighty azgabash",
        "poradi_vydani": "1",
        "misto_vydani": "Praha",
        "rok_vydani": "1989",
        "zpracovatel_zaznamu": "/me",
        "nazev_souboru": "story_of_mighty_azgabash.pdf",
    }

    resp = requests.post(
        "http://localhost:8080/api/v1/submit",
        data={"json_metadata": json.dumps(metadata)},
        auth=requests.auth.HTTPBasicAuth('user', 'pass'),
        files={'file': open(__file__, 'rb')}
    )
    print resp.text
