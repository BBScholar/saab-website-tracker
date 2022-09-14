

ln -s /etc/systemd/user/saab.service $(pwd)/saab.service 
ls -s /etc/systemd/user/saab.timer $(pwd)/saab.timer 
ls -s /usr/bin/saab_website_updates.py $(pwd)/saab_website_updates.py
ls -s /etc/saab-config.yaml $(pwd)/saab-config.yaml

systemctl enable saab.service 
systemctl start saab.service
