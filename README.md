# PyMcBot

> A Discord <-> Minecraft bot built in python utilising pyCraft.

> Use master branch, all other branches are outdated and no longer actively worked on!
> Outdated and bad implementation of Pycraft is used within this repo, it will be changed once finished! (Coming very soon)

[![Build Status](http://img.shields.io/travis/badges/badgerbadgerbadger.svg?style=flat-square)](https://travis-ci.org/badges/badgerbadgerbadger)


[![GRAPHIC](https://i.imgur.com/7QNghpb.png)]()

## Table of Contents


- [Installation](#installation)
- [Features](#features)
- [Contributing](#contributing)
- [Team](#team)
- [FAQ](#faq)
- [Support](#support)
- [License](#license)


---

## Example 

```
You will need to clone this repo, it is how you work with minecraft in python. Short of doing everything yourself I dont see a way of doing it easier
https://github.com/ammaraskar/pyCraft

And I said 'easier' not easy, Pycraft is remarkably hard to grasp for what it is. Out of the box Pycraft only supports the minimum required packets to establish and maintain a connection to a server. If you want more, you have to code them yourself. On there github, they do have a headless client under `start.py`, its not built for usage with Discord.Py but serves as a way to understand how Pycraft works.

A note, PyCraft **IS** blocking. To use it in a bot you need to run it separately, I recommend using `asyncio's` `run_in_executor` method on a ThreadPoolExecutor(), see my code for examples. You could do it a different way if you really wanted.

I recommend making you own account class which can be used to create, establish and maintain new connections. You could modify the headless client they provide as can be seen in a somewhat outdated fashion on the other branch of my repo. But making your own class is simpler and easier to bug fix etc etc

bUt I wanna send a message to discord? Well, meet the `asyncio event loop`, its where our async function bois chill waiting to be run. Check the following links for that
<https://github.com/Skelmis/PyMcBot/blob/master/cogs/ingame.py#L219>
<https://github.com/Skelmis/PyMcBot/blob/master/cogs/ingame.py#L123>

Thats about a general guide, you will have more questions but feel free to ask them
```

---

## Installation 

- All the `code` required to get started
- Download this repo and follow the setup section

### Clone

- Clone this repo to your local machine using `https://github.com/Skelmis/PyMcBot`

### Setup

- Simply follow these to get going in no time.

> Install all the required packages from requirements.txt

```shell
$ pip install -r requirements.txt
```

> Modify config.json and token.json to contain your correct information

> Invite the bot to your discord and run bot.py

---

## Features

---

## Contributing

> To get started...

### Step 1

- **Option 1**
    - 🍴 Fork this repo!

- **Option 2**
    - 👯 Clone this repo to your local machine using `https://github.com/Skelmis/PyMcBot.git`

### Step 2

- **HACK AWAY!** 🔨🔨🔨

### Step 3

- 🔃 Create a new pull request using <a href="https://github.com/Skelmis/PyMcBot/compare" target="_blank">`https://github.com/Skelmis/PyMcBot/compare`</a>.

---

## Team


| <a href="https://koldfusion.xyz/" target="_blank">**Skelmis**</a>
| <a href="http://github.com/Skelmis" target="_blank">`github.com/Skelmis`</a> |

- Core Developer -> Skelmis

- pyCraft repo -> <a href='https://github.com/ammaraskar/pyCraft'>`pyCraft`</a>

---

## FAQ

- **This section hasn't been made yet!**
    - So ask me on discord!

---

## Support

Reach out to me at one of the following places!

- Discord : Skelmis#9135
- Discord I reside in <a href="https://discord.gg/MgVaazZ" target="_blank">`Menudocs`</a>
- Email <a href="mailto:<nowiki>ethan@koldfusion.xyz?subject='PyMcBot Github'">`ethan@koldfusion.xyz`</a>

---

## License

- **[Apache License](http://www.apache.org/licenses/LICENSE-2.0)**
- Copyright 2020 © <a href="https://koldfusion.xyz/" target="_blank">Skelmis</a>.
