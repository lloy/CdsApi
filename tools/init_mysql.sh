#!/bin/sh

#set global variable

USERNAME="admin"
PASSWD="q1w2e3"
#vsphere image template
VSPHERE="centos6.4 centos6.1 ubuntu12.04 ubuntu14.01 window7 windowxp"
#ip range
ip_prefix="10.55."
sub_number=3
ip_start=1
ip_end=252

init_template_table(){

    echo "init template table"
    # init vsphere image template 
    for template_name in $VSPHERE
    do
        mysql -u $USERNAME -p$PASSWD -e "
        use apicloud;
        insert into templatetype (name, iaas_type) values(\"$template_name\", \"vsphere\");
        " >/dev/null 2>&1
    done
    #init openstack image template
}

#init ip table
init_ip_table(){
    echo "init ip table"
    number=$(expr $sub_number - 1)
    for sub in $(seq 0 $number)
	do
	sub=$(expr $sub + 1)
    	gateway="$ip_prefix$sub.254"
    	for i in $(seq $ip_start $ip_end)
    		do
        	sleep 0.05
        	ipaddress=$ip_prefix$sub.$i
        	mysql -u $USERNAME -p$PASSWD -e "
            	use apicloud;
            	insert into iptable (ipaddress, vlan_id, gateway, is_alloc) values (\"$ipaddress\", $sub, \"$gateway\", 0)
        	" >/dev/null 2>&1
    		done
   	done
}

init_instancetype(){
    echo "init instances type"
    mysql -u $USERNAME -p$PASSWD -e "
        use apicloud;
        insert into instancetype (name, core_num, ram, disk, extend_disk) values (\"8-8-120\", 8, 8, 120, 0)
    "
    sleep 0.05
    mysql -u $USERNAME -p$PASSWD -e "
        use apicloud;
        insert into instancetype (name, core_num, ram, disk, extend_disk) values (\"8-64-300\", 8, 64, 300, 0)
    " >/dev/null 2>&1
}

#drop database if exists apicloud;
#create database apicloud;

create_db(){

    echo "Create apicloud database..."
    mysql -u $USERNAME -p$PASSWD -e "

        use apicloud;
        drop table if exists tasks; 
        create table tasks(
            task_id varchar(40) NOT NULL,
            create_time DATETIME NOT NULL,
            template_type varchar(16) NOT NULL,
            model_type varchar(16) NOT NULL,
            status varchar(16) NOT NULL,
            is_run TINYINT(1) NOT NULL,
            instances_num INT UNSIGNED NOT NULL,
            PRIMARY KEY (task_id)
        );

        drop table if exists instances; 
        create table instances(
            instance_uuid varchar(40) NOT NULL,
            task_id varchar(40),
            name varchar(64) NOT NULL,
            ip varchar(40) NOT NULL,
            status varchar(40) NOT NULL,
            os_type varchar(40) NOT NULL,
            username varchar(40) NOT NULL,
            passwd varchar(40) NOT NULL,
            template_type varchar(16) NOT NULL,
            instance_type varchar(16) NOT NULL,
            iaas_type varchar(16) NOT NULL,
            customers varchar(16),
            create_time DATETIME,
            online_time DATETIME,
            off_time DATETIME,
            is_alloc TINYINT(1) NOT NULL,
            PRIMARY KEY (instance_uuid)
        );

        drop table if exists instancetype; 
        create table instancetype(
            name varchar(24) NOT NULL,
            core_num INT UNSIGNED NOT NULL,
            ram INT UNSIGNED NOT NULL,
            disk INT UNSIGNED NOT NULL,
            extend_disk INT UNSIGNED NOT NULL,
            PRIMARY KEY (name)
        );

        drop table if exists templatetype; 
        create table templatetype(
            name varchar(24) NOT NULL,
            iaas_type varchar(24) NOT NULL,
            PRIMARY KEY (name)
        );


        drop table if exists iptable; 
        create table iptable(
            ipaddress varchar(24) NOT NULL,
            vlan_id INT UNSIGNED,
	    gateway varchar(24) NOT NULL,
            is_alloc TINYINT(1) NOT NULL,
            PRIMARY KEY(ipaddress)
        );
        show tables;
    "
}

main(){

    create_db
    init_template_table
    init_instancetype
    init_ip_table
}


### CDS MAIN ###
main
exit 0
