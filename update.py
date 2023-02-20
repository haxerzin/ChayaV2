import asyncio
from core.utils import *


# Function > Initialize
async def init() -> None:
	runtime = current_runtime()
	url = f"https://github.com/haxerzin/ChayaV2/archive/refs/heads/{runtime}.zip"
	await download_file(url, "wget")
	status(2, "Please replace the current archive with downloaded archive.")


# Main
if __name__ == "__main__":
	asyncio.run(init())
