""""This script creat config file, and u must run this script first of all"""
import sys
import configparser
from os import path


def create_config(path):
    """Using parser to output parameters from console"""
    config = configparser.ConfigParser()

    config.add_section('TG')
    config["TG"]["token"] = input("TG token: ")

    config.add_section('Mongo')
    config["Mongo"]["host"] = input('Mongo host: ')

    config.add_section('Redis')
    config["Redis"]["host"] = input('Redis host:')
    config["Redis"]["password"] = input('Redis password: ')

    with open(path, "w") as config_file:
        config.write(config_file)


if __name__ == '__main__':
    if path.isfile('config.ini'):
        key = input("Do you really wanna change your settings?(y/n) ")
        if key == "y":
            create_config('config.ini')
        else:
            sys.exit("Script is terminated")
    else:
        create_config('config.ini')
