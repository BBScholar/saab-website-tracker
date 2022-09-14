

ln -s $(pwd)/saab.service /etc/systemd/user/saab.service 
ls -s $(pwd)/saab.timer /etc/systemd/user/saab.timer 
ls -s $(pwd)/saab_website_updates.py /usr/bin/saab_website_updates.py 
ls -s $(pwd)/saab-config.yaml /etc/saab-config.yaml 

systemctl enable saab.service 
systemctl start saab.service
