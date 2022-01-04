#!/bin/sh


echo ". current custom services in firewalld: ls -al /etc/firewalld/services/"
ls -al /etc/firewalld/services/

for i in my-*.xml; do
  echo ". adding via firewall-cmd a new-service via $i:"
  firewall-cmd --permanent --new-service-from-file=$i
done

firewall-cmd --reload

echo "#fin"

