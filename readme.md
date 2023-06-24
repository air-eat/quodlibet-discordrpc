# a discord rich presence plugin for [quod libet](https://github.com/quodlibet/quodlibet)
![example](docs/example.gif)

this is a version of [quod libet's discord rpc plugin](https://github.com/quodlibet/quodlibet/blob/main/quodlibet/ext/events/discord_status.py) that i (heavily) modified to add time left, a slider using a button ~~and album art~~

i can agree that this is spaghetti code, i am not a great programmer


## disclaimers:
as far as i know, **this code only works on linux** (as the original plugin purposefully throws an error if it detects macos/windows), though i haven't tested it on windows as i am too lazy

i also haven't tested it well enough and it could crash; i know nobody will use this but if it does let me know by submitting an issue

## installation:
#### 1. install the plugin
install the pypresence library:
```shell
pip install pypresence
```

create an events folder in your plugins folder if you haven't already:
```shell
mkdir ~/.config/quodlibet/plugins/events
```

after this, cd into it and clone this repo:
```shell
cd ~/.config/quodlibet/plugins/events
git clone https://github.com/air-eat/quodlibet-discordrpc.git
```

optionally cd into the repo and delete everything but discordrp.py

restart or open quod libet, go to file > plugins and it should show up! 
now you can enable it - and hope it doesn't crash - and go to step 2
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
