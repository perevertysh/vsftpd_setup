# import requests
# import pprint
# import re
import os
import argparse
import random


def set_parser():
    parser = argparse.ArgumentParser(description="program for grab files by links from webpage "
                                                 "by default used universal regexp")
    parser.add_argument('--group', type=str, help='group name')
    parser.add_argument('--add-group', default=False, type=bool, help='add new group [true/false]')
    parser.add_argument('--users', type=str, help='page address')
    parser.add_argument('--server-dir', type=str, help='path to target server\' directory')
    parser.add_argument('--add-server-dir', default=False, type=bool, help='add new server\' directory')
    return parser.parse_args()


def make_config(params):
    """
    :param params: [0] - target file
                   [1] - source file
                   [2] - type of writing in target file
    """
    with open(params[0], params[2]) as config:
        with open(params[1], "r") as template:
            config.write(template.read() + "\n")


def add_user_to_list(user):
    with open("users_list.conf", "a") as template:
        template.write(user + "\n")


def main():
    args = set_parser()
    os.system("touch user_list.conf")
    if args.add_group:
        os.system("sudo groupadd {}".format(args.group))
    if args.add_server_dir:
        os.system("sudo mkdir {0} && sudo chown -R ftp:ftp {0}".format(args.server_dir))
    for conf in [("/etc/vsftpd.conf", "main.conf", "w"),
                 ("/etc/vsftpd.userlist", "users_list.conf", "a")]:
        make_config(conf)
    usr_passwds = {}
    for usr in args.users.split(","):
        system_users = [item.split(":")[0] for item in os.popen("less /etc/passwd").read().split("\n")]
        if usr in system_users:
            print("user is already in the system: {}!".format(usr))
            break
        add_user_to_list(usr)
        usr_sign = {"user": usr,
                    "group": args.group,
                    "server_dir": args.server_dir,
                    "passwd": "some_pass"}
        usr_passwds[usr] = usr_sign["passwd"]
        usr_sign["encrypt_pass"] = os.popen("sudo openssl passwd -crypt {}".format(usr_sign["passwd"])).read()
        os.system("sudo mkdir {server_dir}/{user}".format(**usr_sign))
        os.system("sudo useradd {user} -g {group} -d {server_dir}/{user} -s /bin/false".format(**usr_sign))
        os.system("sudo usermod {user} -p {encrypt_pass}".format(**usr_sign))
        os.system("sudo chown -R {user}:{group} {server_dir}/{user}".format(**usr_sign))
        os.system("sudo systemctl restart vsftpd && sudo systemctl status vsftpd".format(**usr_sign))
    os.system("sudo touch passwd.txt")
    with open("passwd.txt", "a") as passwd_list:
        for usr, passwd in usr_passwds.items():
            passwd_list.write("{} : {} \n".format(usr, passwd))
    print(usr_passwds)


if __name__ == '__main__':
    main()
