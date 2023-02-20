#!/usr/bin/env python3

import asyncio
from argparse import ArgumentParser
from core.utils import run_cmd, clear, banner
from core.colors import status


# Function -> Main
async def main() -> None:
    clear()
    banner()
    # argument parsing
    parser = ArgumentParser(description="ChayaV2 Argument Parser", add_help=True)
    os_group = parser.add_mutually_exclusive_group()
    os_group.add_argument('-ubu','--ubuntu', action='store_true', help="Ubuntu / Ubuntu base")
    os_group.add_argument('-deb', '--debian', action='store_true', help="Debian / Debian base")
    args = parser.parse_args()

    if args.ubuntu:
        await run_cmd("sudo apt install python3-pip && sudo apt install git && pip3 install -r requirements.txt && sudo apt update && sudo apt-add-repository ppa:linuxuprising/libpng12 && sudo apt update && sudo apt install -y libpng12-0")
    elif args.debian:
        await run_cmd("sudo apt install python3-pip && sudo apt install git && pip3 install -r requirements.txt && sudo apt update && sudo apt install build-essential devscripts && cd ~/ && sudo touch /etc/apt/sources.list.d/libpng12.list && echo 'deb https://ppa.launchpadcontent.net/linuxuprising/libpng12/ubuntu hirsute main' | sudo tee -a /etc/apt/sources.list.d/libpng12.list && echo 'deb-src https://ppa.launchpadcontent.net/linuxuprising/libpng12/ubuntu hirsute main' | sudo tee -a /etc/apt/sources.list.d/libpng12.list && sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 1CC3D16E460A94EE17FE581CEA8CACC073C3DB2A && sudo apt update && sudo apt install -y libpng12-0")
    else:
        status(3, "Please select a GNU/Linux distribution! [--ubuntu / --debian]")


# Function -> Init
if __name__ == "__main__":
    asyncio.run(main())
