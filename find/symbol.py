from google.cloud import datastore

from find.pdf import search

manufacturers = {
    "efinix-inc.":"Block Diagram",
    # none "xilinx-inc.":"",
    # first page "rochester-electronics-llc": ""
    "microchip-technology": "Functional Block Diagram",
    # ? "intel":"",
    # on first page "system-on-chip-(soc)-technologies-inc.":"",
    "texas-instruments":"Pin Configuration and Functions",
    "broadcom-limited":"Pin Configuration and Descriptions",
    "analog-devices-inc.":"Functional Block Diagram",
    "silicon-labs":"pin assignments",
    "diodes-incorporated":"Block Diagram",
    "silicon-labs0":"Pin Assignments",
}


def symbol(path, man):
    if man in manufacturers:
        return search(path, manufacturers[man])


if __name__ == "__main__":
    print(symbol("/home/seb/Downloads/ZL40264-Data-Sheet.pdf", "microchip-technology"))