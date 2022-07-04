# Instagram DMs Scraper

This probably violates some ToS somewhere so use it at your own risk.

## Setup

```sh
git clone https://github.com/king-millez/igdm/
```

```sh
cd igdm
```

## Usage

```sh
python3 -m igdm 
```

The package will scroll through a given DM thread for as long as it can. You can limit the amount of times it does this by adding `-l <limit>` (each scroll gets 10 new messages).

```sh
python3 -m igdm -l 10
```
_Would get the last 110 messages **(10 + 10 * limit)**_
 