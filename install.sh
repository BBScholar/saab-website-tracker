mkdir -p /var/lib/saab/
chown saab:saab /var/lib/saab

ln -s $(pwd)/saab.service /etc/systemd/user/saab.service 
ln -s $(pwd)/saab.timer /etc/systemd/user/saab.timer 
ln -s $(pwd)/saab_website_updates.py /usr/bin/saab_website_updates.py 
ln -s $(pwd)/saab-config.yaml /etc/saab-config.yaml 

systemctl enable saab.service 
systemctl start saab.service
