from subprocess import Popen
from core.colors import status

def flif(opt, src, dst):
    if opt == 'e':
        flif_args = f"./flif -r0 {src} {dst}"
    elif opt == 'd':
        flif_args = f"./flif -d -r0 {dst} {src}"
    status(2, f"Executing: {flif_args}")
    try:
        proc = Popen([flif_args], stdout=subprocess.PIPE, shell=True)
        (output, err) = proc.communicate()
        proc_status = proc.wait()
        #status(2, f"Status: {output}\nError: {err}") # debugging
    except Exception as e:
        status(3, f"{e}")
