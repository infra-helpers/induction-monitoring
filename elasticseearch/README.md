ElasticSearch (ES) Cluster Setup on Proxmox LXC Containers
==========================================================

[![Beige, yellow, and blue loom bands, by Michael Walter on Unsplash](../img/michael-walter-12fspxQ387g-unsplash.jpg)](https://unsplash.com/photos/12fspxQ387g)

# Overview
That
[README](https://github.com/infra-helpers/induction-monitoring/tree/master/elasticseearch/README.md)
is part of a [broader tutorial about
monitoring](https://github.com/infra-helpers/induction-monitoring),
and gives details on how to setup a two-node ElasticSearch (ES) cluster
on LXC containers of a Proxmox host, secured by an SSH gateway,
also acting as an Nginx-based reverse proxy.

For the installation of the Proxmox host and LXC containers themselves,
refer to the [dedicated tutorial on
GitHub](https://github.com/cloud-helpers/kubernetes-hard-way-bare-metal/blob/master/proxmox/README.md),
itself a full tutorial on Kubernetes (k8s). Only a summary is given here
for the differences with Kubernetes clusters.

# Table of Content (ToC)
- [ElasticSearch (ES) Cluster Setup on Proxmox LXC Containers](#elasticsearch--es--cluster-setup-on-proxmox-lxc-containers)
- [Overview](#overview)
- [Table of Content (ToC)](#table-of-content--toc-)
- [References](#references)
  * [LXC Containers on Proxmox](#lxc-containers-on-proxmox)
  * [ElasticSearch (ES)](#elasticsearch--es-)
    + [Security](#security)
- [Host preparation](#host-preparation)
  * [Get the latest CentOS templates](#get-the-latest-centos-templates)
  * [Kernel modules](#kernel-modules)
    + [Overlay module](#overlay-module)
    + [`nf_conntrack`](#-nf-conntrack-)
- [SSH gateway and reverse proxy](#ssh-gateway-and-reverse-proxy)
- [Elasticsearch (ES) cluster](#elasticsearch--es--cluster)
  * [Kibana](#kibana)
- [Access to ES from outside through proxy8 with SSH](#access-to-es-from-outside-through-proxy8-with-ssh)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>

# References

## LXC Containers on Proxmox
* [Setup of a Proxmox host](https://github.com/cloud-helpers/kubernetes-hard-way-bare-metal/blob/master/proxmox/README.md)
* [Setup of LXC containers on a Proxmox](https://github.com/cloud-helpers/kubernetes-hard-way-bare-metal/blob/master/lxc/README.md)

## ElasticSearch (ES)
* [Elasticsearch geo-point](https://www.elastic.co/guide/en/elasticsearch/reference/current/geo-point.html)
* https://www.howtoforge.com/how-to-install-elastic-stack-on-centos-8/
* https://stackoverflow.com/a/22165235/798053
* https://stackoverflow.com/a/57819014/798053
* https://www.elastic.co/blog/indexing-csv-elasticsearch-ingest-node
* https://www.elastic.co/guide/en/elasticsearch/reference/master/simulate-pipeline-api.html
* https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html

### Security
The following documentations are mentioned for reference only. In this
repository, the ES cluster is secured through a reverse proxy/SSH gateway
mechanism only.
* https://www.elastic.co/guide/en/elasticsearch/reference/current/configuring-tls.html
* https://www.elastic.co/guide/en/elasticsearch/reference/current/security-api.html#security-user-apis
* https://www.elastic.co/guide/en/elasticsearch/reference/current/native-realm.html
* https://www.elastic.co/guide/en/elasticsearch/reference/current/configuring-security.html


# Host preparation
In that section, it is assumed that we are logged on the Proxmox host
as `root`.

The following parameters are used in the remaining of the guide, and may be
adapted according to your configuration:
* IP of the routing gateway on the host (typically ends with `.254`:
  `HST_GTW_IP`
* (Potentially virtual) MAC address of the ElasticSearch (ES) cluster gateway:
  `GTW_MAC`
* IP address of the ES cluster gateway: `GTW_IP`
* VM ID of that ES cluster gateway: `103`
* For the LXC container-based setup, the private IP addresses
  are summarized as below:

| VM ID | Private IP  |  Host name (full)   | Short name  |
| ----- | ----------- | ------------------- | ----------- |
|  104  | 10.30.2.4   | proxy8.example.com  | proxy8      |
|  191  | 10.30.2.191 | es-in1.example.com  | es-int1     |
|  192  | 10.30.2.192 | es-in2.example.com  | es-int2     |
|  194  | 10.30.2.194 | kfk-in1.example.com | kfk-int1    |
|  195  | 10.30.2.195 | kfk-in2.example.com | kfk-int2    |

* Extract of the host network configuration:
```bash
root@proxmox:~$ cat /etc/network/interfaces
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

# The loopback network interface
auto lo
iface lo inet loopback

auto eno1
iface eno1 inet manual

auto eno2
iface eno2 inet manual

auto bond0
iface bond0 inet manual
        bond-slaves eno1 eno2
        bond-miimon 100
        bond-mode active-backup

# vmbr0: Bridging. Make sure to use only MAC adresses that were assigned to you.
auto vmbr0
iface vmbr0 inet static
        address ${HST_IP}
        netmask 255.255.255.0
        gateway ${HST_GTW_IP}
        bridge_ports bond0
        bridge_stp off
        bridge_fd 0

auto vmbr2
iface vmbr2 inet static
        address 10.30.2.2
        netmask 255.255.255.0
        bridge-ports none
        bridge-stp off
        bridge-fd 0
        post-up echo 1 > /proc/sys/net/ipv4/ip_forward
        post-up iptables -t nat -A POSTROUTING -s '10.30.2.0/24' -o vmbr0 -j MASQUERADE
        post-down iptables -t nat -D POSTROUTING -s '10.30.2.0/24' -o vmbr0 -j MASQUERADE

root@proxmox:~$ cat /etc/systemd/network/50-default.network
# This file sets the IP configuration of the primary (public) network device.
# You can also see this as "OSI Layer 3" config.
# It was created by the OVH installer, please be careful with modifications.
# Documentation: man systemd.network or https://www.freedesktop.org/software/systemd/man/systemd.network.html

[Match]
Name=vmbr0

[Network]
Description=network interface on public network, with default route
DHCP=no
Address=${HST_IP}/24
Gateway=${HST_GTW_IP}
IPv6AcceptRA=no
NTP=ntp.ovh.net
DNS=127.0.0.1
DNS=8.8.8.8

[Address]
Address=${HST_IPv6}

[Route]
Destination=2001:0000:0000:34ff:ff:ff:ff:ff
Scope=link

root@proxmox:~$ cat /etc/systemd/network/50-public-interface.link
# This file configures the relation between network device and device name.
# You can also see this as "OSI Layer 2" config.
# It was created by the OVH installer, please be careful with modifications.
# Documentation: man systemd.link or https://www.freedesktop.org/software/systemd/man/systemd.link.html

[Match]
Name=vmbr0

[Link]
Description=network interface on public network, with default route
MACAddressPolicy=persistent
NamePolicy=kernel database onboard slot path mac
#Name=eth0	# name under which this interface is known under OVH rescue system
#Name=eno1	# name under which this interface is probably known by systemd
```

* The maximal virtual memory needs to be increased on the host:
```bash
$ sysctl -w vm.max_map_count=262144
$ cat >> /etc/sysctl.conf << _EOF

###########################
# Elasticsearch in VM
vm.max_map_count = 262144

_EOF
```

## Get the latest CentOS templates
* List [available templates supported by Proxmox](http://download.proxmox.com/images/system/):
```bash
root@proxmox:~$ pveam update
root@proxmox:~$ pveam available
```

* Download locally a remotely available template:
```bash 
root@proxmox:~$ pveam download local centos-8-default_20191016_amd64.tar.xz
root@proxmox:~$ pveam list local
root@proxmox:~$ # Which should give the same result as:
root@proxmox:~$ ls -lFh /var/lib/vz/template/cache
```

* (not needed here) Download the latest template from the
  [Linux containers site](https://us.images.linuxcontainers.org/images/centos/7/amd64/default/)
  (change the date and time-stamp according to the time you download that
  template):
```bash
root@proxmox:~$ wget https://us.images.linuxcontainers.org/images/centos/8/amd64/default/20200411_07:08/rootfs.tar.xz -O /vz/template/cache/centos-8-default_20200411_amd64.tar.xz
```

## Kernel modules

### Overlay module
```bash
root@proxmox:~$ modprobe overlay && \
  cat > /etc/modules-load.d/docker-overlay.conf << _EOF
overlay
_EOF
```

### `nf_conntrack`
* The `hashsize` parameter should be set to at least 32768.
  We can set it tp 65536. But the Proxmox firewall resets the value every
  so often to 16384. The following shows how that parameter may be set
  when the module is loaded:
```bash
root@proxmox:~$ modprobe nf_conntrack hashsize=65536 && \
  cat > /etc/modules-load.d/nf_conntrack.conf << _EOF
options nf_conntrack hashsize=65536
_EOF
root@proxmox:~$ # echo "65536" > /sys/module/nf_conntrack/parameters/hashsize
root@proxmox:~$ cat /sys/module/nf_conntrack/parameters/hashsize
65536
```

* However, as the Proxmox (PVE) firewall resets that value periodically,
  a work around (to make that change permanent) is to alter
  the PVE firewall script:
```bash
root@proxmox:~$ sed -i -e 's|my $hashsize = int($max/4);|my $hashsize = $max;|g' /usr/share/perl5/PVE/Firewall.pm
root@proxmox:~$ systemctl restart pve-firewall.service
root@proxmox:~$ cat /sys/module/nf_conntrack/parameters/hashsize
65536
```

# SSH gateway and reverse proxy
* The goal is both to set up an SSH gateway and to create an end-point
  for Kibana (https://kibana.example.com)

* All the traffic from the internet to the ES cluster is then forced through
  through the gateway (SSH) and/or the reverse proxy (HTTP/HTTPS)

* The IP address of the web end-point is the gateway's one (`GTW_IP`)

* Add a few DNS `A` records in the `example.com` domain:
  + New record: `es-int1.example.com`
    - Target: `10.30.2.191`
  + New record: `es-int2.example.com`
    - Target: `10.30.2.192`
  + New record: `kibana.example.com`
    - Target: `GTW_IP` (public IP of `proxy8.example.com`, needed for SSL)

* Create the LXC container for the SSH gateway:
```bash
root@proxmox:~$ pct create 104 local:vztmpl/centos-8-default_20191016_amd64.tar.xz --arch amd64 --cores 1 --hostname proxy8.example.com --memory 16134 --swap 32268 --net0 name=eth0,bridge=vmbr0,firewall=1,gw=${HST_GTW_IP},hwaddr=${GTW_MAC},ip=${GTW_IP}/32,type=veth --net1 name=eth1,bridge=vmbr2,ip=10.30.2.4/24,type=veth --onboot 1 --ostype centos
root@proxmox:~$ pct resize 104 rootfs 10G
root@proxmox:~$ ls -laFh /var/lib/vz/images/104/vm-104-disk-0.raw
-rw-r----- 1 root root 10G Apr 12 00:00 /var/lib/vz/images/104/vm-104-disk-0.raw
root@proxmox:~$ cat /etc/pve/lxc/104.conf 
arch: amd64
cores: 2
hostname: proxy8.example.com
memory: 16134
net0: name=eth0,bridge=vmbr0,firewall=1,gw=${HST_GTW_IP},hwaddr=${GTW_MAC},ip=${GTW_IP}/32,type=veth
net1: name=eth1,bridge=vmbr2,hwaddr=<some-mac-addr>,ip=10.30.2.4/24,type=veth
onboot: 1
ostype: centos
rootfs: local:104/vm-104-disk-0.raw,size=10G
swap: 32268
```

* As of April 2020, the LXC templates for (Fedora and) CentOS 8
  do not come with NetworkManager (more specifically, `nmcli` for the tool
  and `NeetworkManager-tui` for the RPM package).
  And to install it, the network needs to be set up, manually first.
  Once NetworkManager has been installed, the network is then setup
  automatically at startup times.

* Manual setup of the network for CentOS 8:
```bash
root@proxmox:~$ pct start 104 && pct enter 104
[root@proxy8]# mkdir ~/bin && cat > ~/bin/netup.sh << _EOF
#!/bin/sh

ip addr add ${HST_GTW_IP}/5 dev eth0
ip link set eth0 up
ip route add default via ${GTW_IP} dev eth0

ip addr add 10.30.2.4/24 dev eth1
ip link set eth1 up

_EOF
[root@proxy8]# chmod 755 ~/bin/netup.sh
[root@proxy8]# ~/bin/netup.sh
[root@proxy8]# dnf -y upgrade
[root@proxy8]# dnf -y install epel-release
[root@proxy8]# dnf -y install NetworkManager-tui
[root@proxy8]# systemctl start NetworkManager.service \
	&& systemctl status NetworkManager.service \
	&& systemctl enable NetworkManager.service
[root@proxy8]# nmcli con # to check the name of the connection
[root@proxy8]# nmcli con up "System eth0"
[root@proxy8]# exit
```

* Complement the installation on the SSH gateway/reverse proxy container.
  For security reason, it may be a good idea to change the SSH port
  from `22` to, say `7022`:
```bash
root@proxmox:~$ pct enter 104
[root@proxy8]# dnf -y install hostname rpmconf dnf-utils wget curl net-tools tar
[root@proxy8]# hostnamectl set-hostname proxy8.example.com
[root@proxy8]# dnf -y install htop less screen bzip2 dos2unix man man-pages
[root@proxy8]# dnf -y install sudo whois ftp rsync vim git-all patch mutt
[root@proxy8]# dnf -y install java-11-openjdk-headless
[root@proxy8]# dnf -y install nginx python3-pip
[root@proxy8]# pip-3 install certbot-nginx
[root@proxy8]# rpmconf -a
[root@proxy8]# ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime
[root@proxy8]# setenforce 0
[root@proxy8]# dnf -y install openssh-server
root@proxy8# sed -i -e 's/#Port 22/Port 7022/g' /etc/ssh/sshd_config
[root@proxy8]# systemctl start sshd.service \
	&& systemctl status sshd.service \
	&& systemctl enable sshd.service
[root@proxy8]# mkdir ~/.ssh && chmod 700 ~/.ssh
[root@proxy8]# cat > ~/.ssh/authorized_keys << _EOF
ssh-rsa AAAA<Add-Your-own-SSH-public-key>BLAgU first.last@example.com
_EOF
[root@proxy8]# chmod 600 ~/.ssh/authorized_keys
[root@proxy8]# passwd -d root
[root@proxy8]# rpm --import http://wiki.psychotic.ninja/RPM-GPG-KEY-psychotic
[root@proxy8]# rpm -ivh http://packages.psychotic.ninja/7/base/x86_64/RPMS/keychain-2.8.0-3.el7.psychotic.noarch.rpm
```

* SSL certificates.
  If `certbot` is not available in `/usr/local/bin` (from the installation
  by `pip-3` above), it can get installed thanks to
  https://certbot.eff.org/lets-encrypt/centosrhel8-nginx.html
```bash
[root@proxy8]# /usr/local/bin/certbot renew
```

* Some convenient additional setup:
```bash
[root@proxy8]# cat > ~/.screenrc << _EOF
hardstatus alwayslastline "%{.kW}%-w%{.B}%n %t%{-}%{=b kw}%?%+w%? %=%c %d/%m/%Y" #B&W & date&time
startup_message off
defscrollback 1024
_EOF
[root@proxy8]# cat > /etc/hosts << _EOF
# Local VM
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6

# ES cluster
10.30.2.191     es-int1.example.com     es-int1
10.30.2.192     es-int2.example.com     es-int2

_EOF
```

* A few handy aliases:
```bash
root@proxy8:~# cat >> ~/.bashrc << _EOF

# Source aliases
if [ -f ~/.bash_aliases ]
then
        . ~/.bash_aliases
fi

_EOF
root@proxy8:~$ cat ~/.bash_aliases << _EOF
# User specific aliases and functions
alias dir='ls -laFh --color'
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

_EOF
root@proxy8:~# . ~/.bashrc
root@proxy8:~# exit
```

* Configure Nginx as a reverse proxy for Kibana:
```bash
root@proxmox:~$ pct enter 104
[root@proxy8]# cat > /etc/nginx/conf.d/ties.conf << _EOF
server {
  server_name kibana.example.com;
  access_log  /var/log/nginx/ties.access.log;

  location / {
      proxy_set_header  Host \$host;
      proxy_set_header  X-Real-IP \$remote_addr;
      proxy_set_header  X-Forwarded-For \$proxy_add_x_forwarded_for;
      proxy_set_header  X-Forwarded-Proto \$scheme;

      # Fix the "It appears that your reverse proxy set up is broken" error.
      proxy_pass         http://10.30.2.191:5601;
      proxy_read_timeout 90;

      proxy_redirect     http://10.30.2.191 https://\$host;
  }
}

_EOF
[root@proxy8]# htpasswd -c /etc/nginx/.kibana-user <kibana-user>
New password: 
Re-type new password: 
Adding password for user <kibana-user>>
[root@proxy8]# /usr/local/bin/certbot --nginx
[root@proxy8]# nginx -t
[root@proxy8]# nginx -s reload
[root@proxy8]# exit
```

# Elasticsearch (ES) cluster
* Create the container for node 1:
```bash
root@proxmox:~$ pct create 191 local:vztmpl/centos-8-default_20191016_amd64.tar.xz --arch amd64 --cores 2 --hostname es-int1.example.com --memory 16134 --swap 32268 --net0 name=eth0,bridge=vmbr2,gw=10.30.2.2,ip=10.30.2.191/24,type=veth --onboot 1 --ostype centos
root@proxmox:~$ pct resize 191 rootfs 50G
root@proxmox:~$ ls -laFh /var/lib/vz/images/191/vm-191-disk-0.raw
-rw-r----- 1 root root 50G Dec 19 22:27 /var/lib/vz/images/191/vm-191-disk-0.raw
root@proxmox:~$ cat /etc/pve/lxc/191.conf
arch: amd64
cores: 2
hostname: es-int1.example.com
memory: 16134
net0: name=eth0,bridge=vmbr2,gw=10.30.2.2,hwaddr=1A:EC:7F:9E:90:34,ip=10.30.2.191/24,type=veth
onboot: 1
ostype: centos
rootfs: local:191/vm-191-disk-0.raw,size=50G
swap: 32268
```

* Create the container for node 2:
```bash
root@proxmox:~$ pct create 192 local:vztmpl/centos-8-default_20191016_amd64.tar.xz --arch amd64 --cores 2 --hostname es-int2.example.com --memory 16134 --swap 32268 --net0 name=eth0,bridge=vmbr2,gw=10.30.2.2,ip=10.30.2.192/24,type=veth --onboot 1 --ostype centos
root@proxmox:~$ pct resize 192 rootfs 50G
root@proxmox:~$ ls -laFh /var/lib/vz/images/192/vm-192-disk-0.raw
-rw-r----- 1 root root 50G Dec 19 22:27 /var/lib/vz/images/192/vm-192-disk-0.raw
root@proxmox:~$ cat /etc/pve/lxc/192.conf
arch: amd64
cores: 2
hostname: es-int2.example.com
memory: 16134
net0: name=eth0,bridge=vmbr2,gw=10.30.2.2,hwaddr=A6:31:DF:33:9A:64,ip=10.30.2.192/24,type=veth
onboot: 1
ostype: centos
rootfs: local:192/vm-192-disk-0.raw,size=50G
swap: 32268
```

* Manual setup of the network for node 1:
```bash
root@proxmox:~$ pct start 191 && pct enter 191
[root@es-int1]# mkdir ~/bin && cat > ~/bin/netup.sh << _EOF
#!/bin/sh

ip addr add 10.30.2.191/24 dev eth0
ip link set eth0 up
ip route add default via 10.30.2.2 dev eth0

_EOF
[root@es-int1]# chmod 755 ~/bin/netup.sh
[root@es-int1]# ~/bin/netup.sh
[root@es-int1]# dnf -y upgrade
[root@es-int1]# dnf -y install epel-release
[root@es-int1]# dnf -y install NetworkManager-tui
[root@es-int1]# systemctl start NetworkManager.service \
	&& systemctl status NetworkManager.service \
	&& systemctl enable NetworkManager.service
[root@es-int1]# nmcli con # to check the name of the connection
[root@es-int1]# nmcli con up "System eth0"
[root@es-int1]# exit
```

* Manual setup of the network for node 2:
```bash
root@proxmox:~$ pct start 192 && pct enter 192
[root@es-int2]# mkdir ~/bin && cat > ~/bin/netup.sh << _EOF
#!/bin/sh

ip addr add 10.30.2.192/24 dev eth0
ip link set eth0 up
ip route add default via 10.30.2.2 dev eth0

_EOF
[root@es-int2]# chmod 755 ~/bin/netup.sh
[root@es-int2]# ~/bin/netup.sh
[root@es-int2]# dnf -y upgrade
[root@es-int2]# dnf -y install epel-release
[root@es-int2]# dnf -y install NetworkManager-tui
[root@es-int2]# systemctl start NetworkManager.service \
	&& systemctl status NetworkManager.service \
	&& systemctl enable NetworkManager.service
[root@es-int2]# nmcli con # to check the name of the connection
[root@es-int2]# nmcli con up "System eth0"
[root@es-int2]# exit
```

* Complement the installation of node 1:
```bash
root@proxmox:~$ pct enter 191
[root@es-int1]# dnf -y install hostname rpmconf dnf-utils wget curl net-tools tar
[root@es-int1]# hostnamectl set-hostname es-int1.example.com
[root@es-int1]# dnf -y install htop less screen bzip2 dos2unix man man-pages
[root@es-int1]# dnf -y install sudo whois ftp rsync vim git-all patch mutt
[root@es-int1]# dnf -y install nginx python3-pip
[root@es-int1]# rpmconf -a
[root@es-int1]# ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime
[root@es-int1]# setenforce 0
[root@es-int1]# dnf -y install openssh-server
[root@es-int1]# systemctl start sshd.service \
	&& systemctl status sshd.service \
	&& systemctl enable sshd.service
[root@es-int1]# mkdir ~/.ssh && chmod 700 ~/.ssh
[root@es-int1]# cat > ~/.ssh/authorized_keys << _EOF
ssh-rsa AAAA<Add-Your-own-SSH-public-key>BLAgU first.last@example.com
_EOF
[root@es-int1]# chmod 600 ~/.ssh/authorized_keys
[root@es-int1]# passwd -d root
[root@es-int1]# rpm --import http://wiki.psychotic.ninja/RPM-GPG-KEY-psychotic
[root@es-int1]# rpm -ivh http://packages.psychotic.ninja/7/base/x86_64/RPMS/keychain-2.8.0-3.el7.psychotic.noarch.rpm
[root@es-int1]# cat > ~/.screenrc << _EOF
hardstatus alwayslastline "%{.kW}%-w%{.B}%n %t%{-}%{=b kw}%?%+w%? %=%c %d/%m/%Y" #B&W & date&time
startup_message off
defscrollback 1024
_EOF
[root@es-int1]# exit
```

* Complement the installation of node 2:
```bash
root@proxmox:~$ pct enter 192
[root@es-int2]# dnf -y install hostname rpmconf dnf-utils wget curl net-tools tar
[root@es-int2]# hostnamectl set-hostname es-int2.example.com
[root@es-int2]# dnf -y install htop less screen bzip2 dos2unix man man-pages
[root@es-int2]# dnf -y install sudo whois ftp rsync vim git-all patch mutt
[root@es-int2]# dnf -y install nginx python3-pip
[root@es-int2]# rpmconf -a
[root@es-int2]# ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime
[root@es-int2]# setenforce 0
[root@es-int2]# dnf -y install openssh-server
[root@es-int2]# systemctl start sshd.service \
	&& systemctl status sshd.service \
	&& systemctl enable sshd.service
[root@es-int2]# mkdir ~/.ssh && chmod 700 ~/.ssh
[root@es-int2]# cat > ~/.ssh/authorized_keys << _EOF
ssh-rsa AAAA<Add-Your-own-SSH-public-key>BLAgU first.last@example.com
_EOF
[root@es-int2]# chmod 600 ~/.ssh/authorized_keys
[root@es-int2]# passwd -d root
[root@es-int2]# rpm --import http://wiki.psychotic.ninja/RPM-GPG-KEY-psychotic
[root@es-int2]# rpm -ivh http://packages.psychotic.ninja/7/base/x86_64/RPMS/keychain-2.8.0-3.el7.psychotic.noarch.rpm
[root@es-int2]# cat > ~/.screenrc << _EOF
hardstatus alwayslastline "%{.kW}%-w%{.B}%n %t%{-}%{=b kw}%?%+w%? %=%c %d/%m/%Y" #B&W & date&time
startup_message off
defscrollback 1024
_EOF
[root@es-int2]# exit
```

* Add an entry on the SSH client (_e.g._, on a laptop):
```bash
user@laptop$ cat >> ~/.ssh/config << _EOF
# Elasticsearch (ES)
Host tiproxy8
  HostName proxy8.example.com
  Port 7022
  ForwardAgent yes
Host ties1
  HostName es-int1.example.com
  ProxyCommand ssh -W %h:22 root@tiproxy8
Host ties2
  HostName es-int2.example.com
  ProxyCommand ssh -W %h:22 root@tiproxy8
_EOF
```

* Elasticsearch (ES) and its dependencies:
```bash
root@proxmox:~$ pct enter 191
[root@es-int]# dnf -y install java-11-openjdk-headless
[root@es-int]# rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch
[root@es-int]# cat > /etc/yum.repos.d/elasticsearch.repo << _EOF
[elasticsearch-7.x]
name=Elasticsearch repository for 7.x packages
baseurl=https://artifacts.elastic.co/packages/7.x/yum
gpgcheck=1
gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
enabled=1
autorefresh=1
type=rpm-md
_EOF
[root@es-int]# dnf -y install elasticsearch
[root@es-int]# sed -i -e 's/#cluster.name: my-application/cluster.name: titsc-escluster/' /etc/elasticsearch/elasticsearch.yml
[root@es-int]# sed -i -e 's/#node.name: node-1/node.name: node-1/' /etc/elasticsearch/elasticsearch.yml
# The following two lines may be added (both nodes participate to master election)
node.master: true
node.data: true
transport.host: 10.30.2.191/192
transport.tcp.port: 9300
discovery.seed_hosts: ["10.30.2.191:9300", "10.30.2.192:9300"]
[root@es-int]# sed -i -e 's/#network.host: 192.168.0.1/network.host: 0.0.0.0/' /etc/elasticsearch/elasticsearch.yml
[root@es-int]# sed -i -e 's/#http.port: 9200/http.port: 9200/' /etc/elasticsearch/elasticsearch.yml
[root@es-int]# sed -i -e 's/#cluster.initial_master_nodes/cluster.initial_master_nodes/' /etc/elasticsearch/elasticsearch.yml
# If necessary, increase the maximum memory of the heap size for ES
[root@es-int]# sed -i -e 's/-XX:+UseConcMarkSweepGC/#-XX:+UseConcMarkSweepGC/' /etc/elasticsearch/jvm.options
[root@es-int]# # sed -i -e 's/-Xmx1g/-Xmx4g/' /etc/elasticsearch/jvm.options
[root@es-int]# systemctl daemon-reload
[root@es-int]# systemctl start elasticsearch \
	&& systemctl enable elasticsearch \
	&& systemctl status elasticsearch
[root@es-int]# curl -XGET 'http://localhost:9200/?pretty'
{
  "name" : "node-1/2",
  "cluster_name" : "titsc-escluster",
  "cluster_uuid" : "29nOWLHZRMOQWfkOjEWLcA",
  "version" : {
    "number" : "7.6.2",
    "build_flavor" : "default",
    "build_type" : "rpm",
    "build_hash" : "ef48eb35cf30adf4db14086e8aabd07ef6fb113f",
    "build_date" : "2020-03-26T06:34:37.794943Z",
    "build_snapshot" : false,
    "lucene_version" : "8.4.0",
    "minimum_wire_compatibility_version" : "6.8.0",
    "minimum_index_compatibility_version" : "6.0.0-beta1"
  },
  "tagline" : "You Know, for Search"
}
```

* Add ElasticSearch to the `PATH` on all the nodes:
```bash
[root@es-int]# cat >> ~/.bashrc << _EOF

# Elastic
ES_HOME="/usr/share/elasticsearch"
export PATH="\${PATH}:\${ES_HOME}/bin"

_EOF
[root@es-int]# . ~/.bashrc
```

## Kibana
* Install Kibana on a single node, `es-int1.example.com`
  (`10.30.2.191`). Edit `/etc/kibana/kibana.yml` and change the
  `server.host` value from `localhost` into `0.0.0.0`:
```bash
[root@es-int1]$ sed -i -e 's/#server.host: "localhost"/server.host: "0.0.0.0"/g' /etc/kibana/kibana.yml
[root@es-int1]$ systemctl enable kibana \
	&& systemctl restart kibana && systemctl status kibana
```

* Setup Kibana:
```bash
[root@es-int]# dnf -y install kibana
[root@es-int]# sed -i -e 's/#server.port: 5601/server.port: 5601/' /etc/kibana/kibana.yml
[root@es-int]# sed -i -e 's/#server.host: "localhost"/server.host: "10.30.2.191"/' /etc/kibana/kibana.yml
[root@es-int]# sed -i -e 's/#elasticsearch.hosts: \["http:\/\/localhost:9200"\]/elasticsearch.hosts: ["http:\/\/localhost:9200"]/' /etc/kibana/kibana.yml
[root@es-int]# systemctl start kibana && systemctl enable kibana && systemctl status kibana
[root@es-int]# netstat -plntu
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      25686/sshd          
tcp        0      0 10.30.2.191:5601        0.0.0.0:*               LISTEN      27503/node          
tcp6       0      0 :::22                   :::*                    LISTEN      25686/sshd          
tcp6       0      0 127.0.0.1:9200          :::*                    LISTEN      27236/java          
tcp6       0      0 127.0.0.1:9300          :::*                    LISTEN      27236/java          
[root@es-int]# exit
```

* On `proxy8`:
```bash
root@proxmox:~$ pct enter 104
[root@proxy8]# curl -XGET https://kibana.example.com && echo
Kibana server is not ready yet
[root@proxy8]# curl -X DELETE "localhost:9200/.kibana_1?pretty"
[root@proxy8]# curl -X DELETE "localhost:9200/.kibana_task_manager_1?pretty"
[root@proxy8]# systemctl restart kibana
[root@proxy8]# exit
```

* Point a browser onto https://kibana.example.com
  (login with `<kibana-user>` and the password which have been setup above
  with the `htpasswd -c` command)

## Access to ES from outside through proxy8 with SSH
* From Travis CI:
```bash
build@travis-ci$ ssh root@tiproxy8 -f -L9400:10.30.2.191:9200 sleep 5; curl -XGET "http://localhost:9400/"|jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   533  100   533    0     0   4845      0 --:--:-- --:--:-- --:--:--  4845
{
  "name": "node-1",
  "cluster_name": "titsc-escluster",
  "cluster_uuid" : "29nOWLHZRMOQWfkOjEWLcA",
  "version": {
    "number": "7.6.2",
    "build_flavor": "default",
    "build_type": "rpm",
    "build_hash": "ef48eb35cf30adf4db14086e8aabd07ef6fb113f",
    "build_date": "2020-03-26T06:34:37.794943Z",
    "build_snapshot": false,
    "lucene_version": "8.4.0",
    "minimum_wire_compatibility_version": "6.8.0",
    "minimum_index_compatibility_version": "6.0.0-beta1"
  },
  "tagline": "You Know, for Search"
}
```

# Kafka
* References:
  + https://docs.confluent.io/current/quickstart/index.html
    - https://docs.confluent.io/current/installation/installing_cp/rhel-centos.html#systemd-rhel-centos-install
    - https://tecadmin.net/install-apache-kafka-centos-8/
  + https://linux.jadoel.info/
  + Kafka releases: https://downloads.apache.org/kafka/

* Add two `A` records in the
  [`example.com` domain](https://www.ovh.com/manager/web/index.html#/configuration/domain/example.com?tab=ZONE):
  + New record: `kfk-int1.example.com`
  + Target: `10.30.2.194`
  + New record: `kfk-int2.example.com`
  + Target: `10.30.2.195`
  + New record: `kafka.example.com`
  + Target: `GTW_IP` (public IP of `proxy8`, needed for SSL)

* Create the container for node 1:
```bash
root@proxmox:~$ pct create 194 local:vztmpl/centos-8-default_20191016_amd64.tar.xz --arch amd64 --cores 2 --hostname kfk-int1.example.com --memory 16134 --swap 32268 --net0 name=eth0,bridge=vmbr2,gw=10.30.2.2,ip=10.30.2.194/24,type=veth --onboot 1 --ostype centos
root@proxmox:~$ pct resize 194 rootfs 50G
root@proxmox:~$ ls -laFh /var/lib/vz/images/194/vm-194-disk-0.raw
-rw-r----- 1 root root 50G Apr 13 14:42 /var/lib/vz/images/194/vm-194-disk-0.raw
root@proxmox:~$ cat /etc/pve/lxc/194.conf
arch: amd64
cores: 2
hostname: kfk-int1.example.com
memory: 16134
net0: name=eth0,bridge=vmbr2,gw=10.30.2.2,hwaddr=DA:4C:AB:06:0F:2A,ip=10.30.2.194/24,type=veth
onboot: 1
ostype: centos
rootfs: local:194/vm-194-disk-0.raw,size=50G
swap: 32268
```

* Create the container for node 2:
```bash
root@proxmox:~$ pct create 195 local:vztmpl/centos-8-default_20191016_amd64.tar.xz --arch amd64 --cores 2 --hostname kfk-int2.example.com --memory 16134 --swap 32268 --net0 name=eth0,bridge=vmbr2,gw=10.30.2.2,ip=10.30.2.195/24,type=veth --onboot 1 --ostype centos
root@proxmox:~$ pct resize 195 rootfs 50G
root@proxmox:~$ ls -laFh /var/lib/vz/images/195/vm-195-disk-0.raw
-rw-r----- 1 root root 50G Apr 13 14:44 /var/lib/vz/images/195/vm-195-disk-0.raw
root@proxmox:~$ cat /etc/pve/lxc/195.conf
arch: amd64
cores: 2
hostname: kfk-int2.example.com
memory: 16134
net0: name=eth0,bridge=vmbr2,gw=10.30.2.2,hwaddr=0A:75:1B:03:A5:39,ip=10.30.2.195/24,type=veth
onboot: 1
ostype: centos
rootfs: local:195/vm-195-disk-0.raw,size=50G
swap: 32268
```

* Manual setup of the network for node 1:
```bash
root@proxmox:~$ pct start 194 && pct enter 194
[root@kfk-int1]# mkdir ~/bin && cat > ~/bin/netup.sh << _EOF
#!/bin/sh

ip addr add 10.30.2.194/24 dev eth0
ip link set eth0 up
ip route add default via 10.30.2.2 dev eth0

_EOF
[root@kfk-int1]# chmod 755 ~/bin/netup.sh
[root@kfk-int1]# ~/bin/netup.sh
[root@kfk-int1]# dnf -y upgrade
[root@kfk-int1]# dnf -y install epel-release
[root@kfk-int1]# dnf -y install NetworkManager-tui
[root@kfk-int1]# systemctl start NetworkManager.service && systemctl status NetworkManager.service && systemctl enable NetworkManager.service
[root@kfk-int1]# nmcli con # to check the name of the connection
[root@kfk-int1]# nmcli con up "System eth0"
[root@kfk-int1]# exit
```

* Manual setup of the network for node 2:
```bash
root@proxmox:~$ pct start 195 && pct enter 195
[root@kfk-int2]# mkdir ~/bin && cat > ~/bin/netup.sh << _EOF
#!/bin/sh

ip addr add 10.30.2.195/24 dev eth0
ip link set eth0 up
ip route add default via 10.30.2.2 dev eth0

_EOF
[root@kfk-int2]# chmod 755 ~/bin/netup.sh
[root@kfk-int2]# ~/bin/netup.sh
[root@kfk-int2]# dnf -y upgrade
[root@kfk-int2]# dnf -y install epel-release
[root@kfk-int2]# dnf -y install NetworkManager-tui
[root@kfk-int2]# systemctl start NetworkManager.service && systemctl status NetworkManager.service && systemctl enable NetworkManager.service
[root@kfk-int2]# nmcli con # to check the name of the connection
[root@kfk-int2]# nmcli con up "System eth0"
[root@kfk-int2]# exit
```

* Complement the installation of node 1:
```bash
root@proxmox:~$ pct enter 194
[root@kfk-int1]# dnf -y install hostname rpmconf dnf-utils wget curl net-tools tar
[root@kfk-int1]# hostnamectl set-hostname kfk-int1.example.com
[root@kfk-int1]# dnf -y install htop less screen bzip2 dos2unix man man-pages
[root@kfk-int1]# dnf -y install sudo whois ftp rsync vim git-all patch mutt
[root@kfk-int1]# dnf -y install nginx python3-pip
[root@kfk-int1]# rpmconf -a
[root@kfk-int1]# ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime
[root@kfk-int1]# setenforce 0
[root@kfk-int1]# dnf -y install openssh-server
[root@kfk-int1]# systemctl start sshd.service && systemctl status sshd.service && systemctl enable sshd.service
[root@kfk-int1]# mkdir ~/.ssh && chmod 700 ~/.ssh
[root@kfk-int1]# cat > ~/.ssh/authorized_keys << _EOF
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCeiMpaINdFvswOkq1zahnslmh6E1RjyvgVfbiTbFPwjEE+7WmCeD2fo7QekXiP0PTDZh8pN5Xs2v067L6/tzL8KTH4aY6GDD6H71LZa5jYFGA8fmgv7y0eeAhar/Cn331LolWdkR3qBkf+nvN6WrsA8XxYhK9mdUtG0h6bZtJZEnEYejvg/AuXJGMjMDpMq+iYnMaw0NHyDmag3VmQiXTLbqmQKw/p14qtBYR3fhgESnXnXImZGogo9GUhiRsaimiEiM/zBunnL8Do0dlLqDQYQmhlm08TFosuO8kSz8nQVXnuakmH0ePYNnST3WYwx0Ii0xuip29jO+8vDrXAHIrV denis.arnaud_fas2017@m4x.org
_EOF
[root@kfk-int1]# chmod 600 ~/.ssh/authorized_keys
[root@kfk-int1]# passwd -d root
[root@kfk-int1]# rpm --import http://wiki.psychotic.ninja/RPM-GPG-KEY-psychotic
[root@kfk-int1]# rpm -ivh http://packages.psychotic.ninja/7/base/x86_64/RPMS/keychain-2.8.0-3.el7.psychotic.noarch.rpm
[root@kfk-int1]# cat > ~/.screenrc << _EOF
hardstatus alwayslastline "%{.kW}%-w%{.B}%n %t%{-}%{=b kw}%?%+w%? %=%c %d/%m/%Y" #B&W & date&time
startup_message off
defscrollback 1024
_EOF
[root@kfk-int1]# exit
```

* Complement the installation of node 2:
```bash
root@proxmox:~$ pct enter 195
[root@kfk-int2]# dnf -y install hostname rpmconf dnf-utils wget curl net-tools tar
[root@kfk-int2]# hostnamectl set-hostname kfk-int2.example.com
[root@kfk-int2]# dnf -y install htop less screen bzip2 dos2unix man man-pages
[root@kfk-int2]# dnf -y install sudo whois ftp rsync vim git-all patch mutt
[root@kfk-int2]# dnf -y install nginx python3-pip
[root@kfk-int2]# rpmconf -a
[root@kfk-int2]# ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime
[root@kfk-int2]# setenforce 0
[root@kfk-int2]# dnf -y install openssh-server
[root@kfk-int2]# systemctl start sshd.service && systemctl status sshd.service && systemctl enable sshd.service
[root@kfk-int2]# mkdir ~/.ssh && chmod 700 ~/.ssh
[root@kfk-int2]# cat > ~/.ssh/authorized_keys << _EOF
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCeiMpaINdFvswOkq1zahnslmh6E1RjyvgVfbiTbFPwjEE+7WmCeD2fo7QekXiP0PTDZh8pN5Xs2v067L6/tzL8KTH4aY6GDD6H71LZa5jYFGA8fmgv7y0eeAhar/Cn331LolWdkR3qBkf+nvN6WrsA8XxYhK9mdUtG0h6bZtJZEnEYejvg/AuXJGMjMDpMq+iYnMaw0NHyDmag3VmQiXTLbqmQKw/p14qtBYR3fhgESnXnXImZGogo9GUhiRsaimiEiM/zBunnL8Do0dlLqDQYQmhlm08TFosuO8kSz8nQVXnuakmH0ePYNnST3WYwx0Ii0xuip29jO+8vDrXAHIrV denis.arnaud_fas2017@m4x.org
_EOF
[root@kfk-int2]# chmod 600 ~/.ssh/authorized_keys
[root@kfk-int2]# passwd -d root
[root@kfk-int2]# rpm --import http://wiki.psychotic.ninja/RPM-GPG-KEY-psychotic
[root@kfk-int2]# rpm -ivh http://packages.psychotic.ninja/7/base/x86_64/RPMS/keychain-2.8.0-3.el7.psychotic.noarch.rpm
[root@kfk-int2]# cat > ~/.screenrc << _EOF
hardstatus alwayslastline "%{.kW}%-w%{.B}%n %t%{-}%{=b kw}%?%+w%? %=%c %d/%m/%Y" #B&W & date&time
startup_message off
defscrollback 1024
_EOF
[root@kfk-int2]# exit
```

* Add an entry on the SSH client:
```bash
user@laptop$ cat >> ~/.ssh/config << _EOF

# Kafka
Host tikfk1
  HostName kfk-int1.example.com
  ProxyCommand ssh -W %h:22 root@tiproxy8
  ForwardAgent yes
Host tikfk2
  HostName kfk-int2.example.com
  ProxyCommand ssh -W %h:22 root@tiproxy8
  ForwardAgent yes

_EOF
```

## Kafka specificities
The following tasks have to be performed on every node.

Zookeeper is bundled with the Kafka tar-ball.

* Install Java:
```bash
root@proxmox:~$ pct enter 194 # pct enter 195
[root@kfk-intN]# dnf -y install java-11-openjdk-headless
```

* Download and extract the Kafka tar-ball:
```bash
[root@kfk-intN]# mkdir -p /opt/kafka/archives && cd /opt/kafka
[root@kfk-intN]# wget https://downloads.apache.org/kafka/2.4.1/kafka_2.13-2.4.1.tgz
[root@kfk-intN]# tar zxf kafka_2.13-2.4.1.tgz && mv kafka_2.13-2.4.1.tgz archives/
[root@kfk-intN]# mv kafka_2.13-2.4.1 /usr/local && cd /usr/local && ln -s kafka_2.13-2.4.1 kafka
```

* Setup Zookeeper:
```bash
[root@kfk-intN]# mkdir -p /usr/share/zookeeper/data
[root@kfk-intN]# sed -i -e 's|dataDir=/tmp/zookeeper|dataDir=/usr/share/zookeeper/data|g' /usr/local/kafka/config/zookeeper.properties
[root@kfk-intN]# sed -i -e 's|maxClientCnxns=0|maxClientCnxns=10|g' /usr/local/kafka/config/zookeeper.properties
```

* Setup `systemd` for Zookeeper:
```bash
[root@kfk-intN]# cat > /etc/systemd/system/zookeeper.service << _EOF
[Unit]
Description=Apache Zookeeper server
Documentation=http://zookeeper.apache.org
Requires=network.target remote-fs.target
After=network.target remote-fs.target

[Service]
Type=simple
ExecStart=/usr/local/kafka/bin/zookeeper-server-start.sh /usr/local/kafka/config/zookeeper.properties
ExecStop=/usr/local/kafka/bin/zookeeper-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
_EOF
```

* Test that Zookeeper is working:
```bash
[root@kfk-intN]# zookeeper-shell.sh 10.30.2.194:2181 ls /brokers/ids
Connecting to 10.30.2.194:2181

WATCHER::

WatchedEvent state:SyncConnected type:None path:null
Node does not exist: /brokers/ids
```

* Setup Kafka:
```bash
[root@kfk-intN]# mkdir -p /usr/share/kafka/data /var/log/kafka
[root@kfk-intN]# sed -i -e 's|broker.id=0|broker.id=N|g' /usr/local/kafka/config/server.properties
[root@kfk-intN]# sed -i -e 's|log.dirs=/tmp/kafka-logs|log.dirs=/var/log/kafka|g' /usr/local/kafka/config/server.properties
[root@kfk-intN]# sed -i -e 's|offsets.topic.replication.factor=1|offsets.topic.replication.factor=2|g' /usr/local/kafka/config/server.properties
[root@kfk-intN]# sed -i -e 's|transaction.state.log.replication.factor=1|transaction.state.log.replication.factor=2|g' /usr/local/kafka/config/server.properties
[root@kfk-intN]# sed -i -e 's|zookeeper.connect=localhost:2181|zookeeper.connect=10.30.2.194:2181|g' /usr/local/kafka/config/server.properties
```

* Setup `systemd` for Kafka:
```bash
[root@kfk-intN]# cat > /etc/systemd/system/kafka.service << _EOF
[Unit]
Description=Apache Kafka Server
Documentation=http://kafka.apache.org/documentation.html
Requires=zookeeper.service

[Service]
Type=simple
Environment="JAVA_HOME=/usr/lib/jvm/jre-11-openjdk"
ExecStart=/usr/local/kafka/bin/kafka-server-start.sh /usr/local/kafka/config/server.properties
ExecStop=/usr/local/kafka/bin/kafka-server-stop.sh

[Install]
WantedBy=multi-user.target
_EOF
[root@kfk-intN]# systemctl daemon-reload
[root@kfk-intN]# systemctl start zookeeper && systemctl status zookeeper && systemctl enable zookeeper
[root@kfk-intN]# systemctl start kafka && systemctl status kafka && systemctl enable kafka
```

* Add Kafka to the `PATH`:
```bash
[root@kfk-intN]# cat >> ~/.bashrc << _EOF

# Kafka
KAFKA_HOME="/usr/local/kafka"
export PATH="\${PATH}:\${KAFKA_HOME}/bin"

_EOF
[root@kfk-intN]# . ~/.bashrc
```

* Check that the setup is up und running with two nodes. From any node:
```bash
[root@kfk-intN]# zookeeper-shell.sh 10.30.2.194:2181 ls /brokers/ids
Connecting to 10.30.2.194:2181

WATCHER::

WatchedEvent state:SyncConnected type:None path:null
[1, 2]
```

* Create a `test` topic and check that it is there:
```bash
[root@kfk-intN]# kafka-topics.sh --create --zookeeper 10.30.2.194:2181 --replication-factor 2 --partitions 2 --topic test
Created topic test.
[root@kfk-intN]# kafka-topics.sh --list --zookeeper 10.30.2.194:2181 
test
```

* Send a few messages onto the `test` topic. From any node:
```bash
[root@kfk-intN]# kafka-console-producer.sh --broker-list 10.30.2.194:9092 --topic test
>Hello World!
>A second line
>^C
```

* Check that the messages are in the queue. From any node:
```bash
[root@kfk-intN]# kafka-console-consumer.sh --bootstrap-server 10.30.2.195:9092 --topic test --from-beginning
Hello World!
A second line
^CProcessed a total of 2 messages
```

## Access to Kafka and Zookeeper through proxy8 with SSH
* From Travis CI, list the Kafka node brokers:
```bash
build@travis-ci$ ssh root@tiproxy8 zookeeper-shell.sh 10.30.2.194:2181 ls /brokers/ids
Connecting to 10.30.2.194:2181

WATCHER::

WatchedEvent state:SyncConnected type:None path:null
[1, 2]
```

* From Travis CI, list the Kafka topics:
```bash
build@travis-ci$ ssh root@tiproxy8 kafka-topics.sh --list --zookeeper 10.30.2.194:2181
__consumer_offsets
test
```

* From Travis CI, send messages:
```bash
build@travis-ci$ ssh root@tiproxy8 kafka-console-producer.sh --broker-list 10.30.2.194:9092 --topic test
>Hello World, second test!
>From remote!
>^C
```

* From Travis CI, check the messages:
```bash
build@travis-ci$ ssh root@tiproxy8 kafka-console-consumer.sh --bootstrap-server 10.30.2.195:9092 --topic test --from-beginning
A second line
From remote!
Hello World!
Hello World, second test!
^C
```

