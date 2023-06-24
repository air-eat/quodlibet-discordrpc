# a discord rich presence plugin for [quod libet](https://github.com/quodlibet/quodlibet)
![example](docs/example.gif)

this is a version of [quod libet's discord rpc plugin](https://github.com/quodlibet/quodlibet/blob/main/quodlibet/ext/events/discord_status.py) that i (heavily) modified to add time left, a slider using a button ~~and album art~~

i can agree that this is spaghetti code, i am not a great programmer


## disclaimers:
as far as i know, **this code only works on linux** (as the original plugin purposefully throws an error if it detects macos/windows), though i haven't tested it on windows as i am too lazy

i also haven't tested it well enough and it could crash; i know nobody will use this but if it does let me know by submitting an issue

## faq:
#### how do i use the album cover instead?
working on it right now; i'll release it when i'm finished
#### can you change the "Playing" to "Listening to"?
this is a limitation of discord's rich presence; afaik there is nothing i can do about it
#### how can i use my own play/pause icon?
paste the image links into the play/pause image fields in the plugin's preferences

if you have them on your computer, upload your icons online first (using services like [imgur](https://imgur.com/upload) or [catbox.moe](https://catbox.moe/))

## installation:
#### 1. install the plugin
install the pypresence library (in this case using pip):
```shell
pip install pypresence
```

create a plugins folder if one doesn't exist and create an events folder inside it:
```shell
mkdir ~/.config/quodlibet/plugins
mkdir ~/.config/quodlibet/plugins/events
```

after this, cd into it and download discordrp.py (in this case using wget):
```shell
cd ~/.config/quodlibet/plugins/events
wget https://raw.githubusercontent.com/air-eat/quodlibet-discordrpc/main/discordrp.py
```

restart or open quod libet, go to file > plugins and it should show up!  
now you can enable it - and hope it doesn't crash - and go to step 2 below
#### 2. creating an app for rich presence:
go to the [discord developer webportal](https://discord.com/developers/applications) and create a new application:

![press this button!](docs/appcreation1.png)

type in whatever name you want to display in discord (preferably quod libet), agree to the tos and press create:

![like this](docs/appcreation2.png)

copy the "application id" from your newly created app:

![this one!!!](docs/appcreation3.png)

go to file > plugins, click on the plugin and paste it into the "app id" field:

![who will actually see these tooltips](docs/appcreation4.png)

and you should be done!

## todo:
- implement album art
    - see [foobar2000's solution for uploading](https://github.com/s0hv/rust-imgur-upload)
- clear everything when nothing is playing

---
![kitty](http://placekitten.com/1001/200)
