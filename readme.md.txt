## PC build assistant

### Purpose
The purpose of this script is to provide users with a website that allows them to select any PC component they want and give them an interactive and realistic view of their ideal PC.

### Logical Architecture & Execution Checks
1. **Cost of scraping & research:** Scour through the internet to figure out the selected components price in AUD
2. **Power capacity calculations:** Calculates component electrical loads under stress. If total calculated wattage(power) exceeds the maximum safe operational threshold defined by the selected PSU payload config, the application flags a dangerous power deficit state.
3. **individual component quality:** Compares compatibility and overall quality of the components among each other(Ex: matching a weak processor with an very good graphics processor) and flags user if components are incompatible