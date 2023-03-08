import os
from random import randint
import hashlib
import wget
import requests
from datetime import datetime
from PIL import Image
from pathlib import Path
import asyncio

from core.colors import status
from core.colors import c_white, c_green, c_red, c_yellow, c_blue, c_bold, c_clean

# - Utilities - #

# yield successive n-sized chunks of text
def text_chunker(msg: str, n: int) -> []:
	new_msg = []
	len_str = len(msg)
	k = len_str//n
	if (len_str % n != 0):
		msg += "X"
		len_str = len(msg)
	for i in range(0, len_str, k):
		new_msg.append(msg[i:i+k])
	return new_msg


# check internet connection
async def internet_on():
    try:
        response = requests.get('https://www.google.com/favicon.ico', timeout=0.5)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.Timeout:
        return False


# current runtime
def current_runtime() -> str:
	runtime_path = str(Path.cwd()) + "/RUNTIME.txt"
	runtime_path = convert_to_path(runtime_path)
	runtime = ""
	with open(runtime_path, 'r') as f:
		runtime = f.readline()
	if runtime != None:
		return runtime
	else:
		return "main"


# get os name
def get_os_name() -> str:
	import platform
	return platform.system()


# convert names to path
def convert_to_path(dirpath: str):
	dirpath.encode('unicode escape')
	p = Path(dirpath)
	return p


# Function > Clear Screen
def clear() -> None:
	os.system('cls' if os.name == 'nt' else 'clear')


# Function > Banner
async def banner() -> None:
	version_number = 0
	print(f'''{c_red}
   ___ _                 __   _____ 
  / __| |_  __ _ _  _ __ \ \ / |_  )
 | (__| ' \/ _` | || / _` \ V / / / 
  \___|_||_\__,_|\_, \__,_|\_/ /___|
                 |__/               
		{c_clean}'''
		)
	print(f" {c_green}{c_bold} [ Advance Image Steganography ]{c_clean}")
	vpath = convert_to_path(str(Path.cwd()) + '/VERSION.txt')    
	try:
		with open(vpath) as f:
			version_number = f.readline()
			print(f" {c_bold}{c_yellow} [ v{version_number} ] {c_red} [ 2023 ]{c_clean}")
	except Exception as e:
		print(f" {c_bold}{c_yellow}[ v2 ] {c_red} [ 2023 ]{c_clean}")
	print(f" {c_blue}{c_bold} [ https://github.com/haxerzin/ ]{c_clean}")


# Function > Run command line
async def run_cmd(cmd: str) -> None:
	try:
		os.system(cmd)
	except Exception as e:
		status(3, f"Unable to run command: {cmd}")


# Function > Get List of Files In Directory
async def get_files_in_dir(dir_path: str) -> []:
	files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
	return files


# Function > Generate random number
def generate_random_id() -> int:
	random_id = randint(1,10001)
	return random_id


# Function > Generate SHA-256 hash for file
def generate_sha256_signature(file_path):
  with open(file_path, 'rb') as f:
    sha256_hash = hashlib.sha256()
    # read the file in blocks of 4KB
    for byte_block in iter(lambda: f.read(4096), b""):
      sha256_hash.update(byte_block)
    return str(sha256_hash.hexdigest())


# Function > Get current time in Hour:Minute:Second format
def get_current_time():
	now = datetime.now()
	current_time = now.strftime("%H:%M:%S")
	return current_time


# Function -> Convert JPG to PNG
async def convert_jpg_to_png(image_path: str) -> None:
	ximg = Image.open(image_path)
	new_image_path = f"{image_path[:-5]}.png"
	ximg.save(new_image_path)
	os.remove(image_path)


# Function -> Get string length
def utf8len(s):
	return len(s.encode('utf-8'))


# Function -> File downloader
async def download_file(url: str, download_with: str, dest=None) -> None:
	filename = url.split('/')[-1]
	filepath = str(Path.cwd()) + filename
	filepath = convert_to_path(filepath)
	if download_with == "wget":
		try:
			status(0, f"Downloading: {url}")
			wget.download(url)
			status(1, f"Download Complete: {url}")
		except Exception as e:
			status(3, f"{e}")
	else:
		status(0, f"Downloading: {url}")
		try:
			req = requests.get(url)
			status(1, f"Download Complete: {url}")
			try:
				with open(filepath,'wb') as output_file:
					output_file.write(req.content)
				status(1, f"Download File Created")
			except Exception as e:
				status(3, f"Unable to create file: {e}")
		except Exception as e:
			status(3, f"{e}")


# Function -> Clean appdata
async def clear_appdata() -> None:
	# get all the files from appdata folder
	data_files = await get_files_in_dir("appdata/")
	status(2, "Safe Cleaning Appdata")
	# for each file in list of files in appdata folder
	for df in data_files:
		# if file is CSV
		if df[-4:] == ".csv":
			# delete the file
			os.remove(f"appdata/{df}")
			status(1, f"Deleted: appdata/{df}")
		if df[-5:] == ".json":
			# if file is JSON, empty the file
			with open(f"appdata/{df}", "w") as f:
				f.write("")
			status(1, f"Cleaned Contents: appdata/{df}")
	# delete all images in autoexp
	image_raw_files = await get_files_in_dir("autoexp/image_raw/")
	image_steg_files = await get_files_in_dir("autoexp/image_steg/")
	image_steg_comp_files = await get_files_in_dir("autoexp/image_steg_comp/")
	status(1, f"Deleted: appdata/{df}")
	for imgfilex in image_raw_files:
		os.remove(f"autoexp/image_raw/{imgfilex}")
		status(1, f"Deleted: autoexp/image_raw/{imgfilex}")
	status(0, f"Deleting steg images")
	for imgfiley in image_steg_files:
		os.remove(f"autoexp/image_steg/{imgfiley}")
		status(1, f"Deleted: autoexp/image_steg/{imgfiley}")
	status(0, f"Deleting compressed images")
	for imgfilez in image_steg_comp_files:
		os.remove(f"autoexp/image_steg_comp/{imgfilez}")
		status(1, f"Deleted: autoexp/image_raw_comp/{imgfilez}")
	status(1, f"Cleaning Completed")
