#!/bin/sh

#set global variable
set -e

USERNAME="admin"
PASSWD="123456"
#vsphere image template
#ip range
network_number=$1
ip_start=$2
ip_end=$3
gateway=$4
flag=$5
sub=$6



#init ip table
inject_ip(){
    echo "init ip table"
    for i in $(seq $ip_start $ip_end)
        do
        sleep 0.05
        ipaddress=$network_number.$i
        echo $ipaddress
        mysql -u $USERNAME -p$PASSWD -e "
            use apicloud;
            insert into iptable (ipaddress, vlan_id, gateway, is_alloc, flag) values (\"$ipaddress\", $sub, \"$gateway\", 0, \"$flag\")
        "
        # >/dev/null 2>&1
        done
    echo "inject completed"
}


main(){

    inject_ip
}


### CDS MAIN ###
if [ -z "$network_number" ];then
    echo "Usage: $0 network_number ip_start ip_end gateway flag vlan_id
        $0 '192.168.4' 4 20 '192.168.4.1' 'fixable' 5"
        exit 1
else
    main
fi
exit 0
