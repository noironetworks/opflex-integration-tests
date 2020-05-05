#! /bin/bash
  
echo "Provisioning for Cisco lab environment inside node"

# Lab proxy
cat <<EOF >>/etc/environment
http_proxy=http://proxy.esl.cisco.com:80
https_proxy=http://proxy.esl.cisco.com:80
no_proxy=localhost,127.0.0.1,172.28.184.8,172.28.184.14,172.28.184.18
EOF

# DNS resolution
systemctl disable systemd-resolved.service
systemctl stop systemd-resolved
# Remove the symlink
rm /etc/resolv.conf
cat <<EOF >/etc/resolv.conf
nameserver 172.28.184.18
search noiro.lab
EOF
# Make it immutable
chattr -e /etc/resolv.conf
chattr +i /etc/resolv.conf

