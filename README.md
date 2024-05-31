# Python bruteforce pass

troll brimmy websites with dictionary attacks or brute force

## Usage

before running, create a virutal environment with dependencies

```
python -m venv venv
source venv/bin/activate
pip install aiohttp asyncio
```

To run the program.
```
python pybrute.py target https://example.com [ dictionary.txt ]
```
optionally use a dictionary attack by specifying a path to a dictinary text file.

the current bad_passwords.txt file is for user "tlb"

