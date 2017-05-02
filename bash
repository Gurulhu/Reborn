export init_key_0=Database
export init_value_0=ds015915.mlab.com,15915,heroku_ztxn2tqm,gurulhu_slave,slave4U

export init_key_1=Main
export init_value_1=medheav.ddns.net, 13031

python3 slave.py
while [ $? -ne 0 ]; do
  python3 slave.py
done
