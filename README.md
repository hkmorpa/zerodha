

# Set enc token
export enctoken=""

# Set expiry
export expiry="105"

# close all positons, use side as a filter
command=close_all side=sell python kite_runner.py

# place new orders
command=place_order Bprice=20 Sprice= quantity=1700 Binstrument=43000PE Sinstrument=42000PE python3 kite_runner.py

# place volatile  orders
command=volatile Bprice= Sprice= quantity=900 Binstrument=43500CE Sinstrument=42500CE*3 python3 kite_runner.py

# place only buy orders
command=buy price=23 quantity=3600 instrument=43500CE  python3 kite_runner.py

# place only sell orders
command=sell price=23 quantity=3600 instrument=43500CE  python3 kite_runner.py


# SL runner: this script will run every 10 seconds, PRESS CTRL + C to stop script
command=sl_runner sl_amount=-2000 python kite_runner.py

# to remove all git local changes
git checkout .

# pull latest code from msater branch
git pull origin master
