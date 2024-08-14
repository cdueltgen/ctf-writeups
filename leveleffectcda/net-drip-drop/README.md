# Drip Drop

Category: Networking<br>
Difficulty: Hard (Hardest? It was one of the 350 point questions)

I didn't actually finish this one, but once I saw the solution I knew I needed to write up at least what I did make it through so you could see where I was going. I was on the right path, I just didn't manage to make the final leap.

We were given a pcap file and asked to see if we could find if any data was exfiltrated.

### Recon
First step was to pull the pcap into Wireshark and have a look around.

First clue: There are a *lot* of ICMP packets. Like, an unusual amount. This probably means something. All of the ICMP packets are between the same two IPs. I spent a bunch of time searching for data exfil via ICMP and didn't find anything that screamed **this is the answer**, so I filed that for later and moved on. 

Second clue: I like to take a look at full traces in Wireshark to see what's there before I start filtering things. So I just right-clicked on the first TCP packet and hit Follow-> TCP Stream. Once you're in that box, you can just click the up arrow in the Stream box to march through. I am endlessly fascinated by network traces, so I could literally look at these all day. All but one of them are just noise, I'm pretty sure, but it didn't take long to stumble across stream 13, which had the following opening line:

`POST /login?hint=you%27ll%20probably%20need%20these HTTP/1.1`

And in the payload:

`{"username": "3e1d1f4c8a7b456a9f4d5b3f2c6e8a1d", "password": "5b8e2a27dc43bc967c435a7c8c3ab0fc5294b4c0a27c68719a621f0348be5c1a"}`

Seems like something we should write down and hang on to, right? Looks like an iv and an encryption key, doesn't it?

There is nothing else interesting about the TCP packet traces that I could glean, so I went back to looking deeper at the ICMP packets to see if I could figure out what they were trying to tell me.

### Solve it
My first instinct here was to try to find a pattern or see if the grouping of ICMP packets was significant. Viewing the pcap in wireshark it looks like there are clusters of them, so I went through and gathered the clusters, turning the count of each cluster into hex and then I fed that into cyberchef to see if I could make anything of it. I could not. So that wasn't it.

My second instinct was something to do with the timing of the packets. I went down a few rabbit holes here, but couldn't quite get there. This is where I got stuck. I felt I was close, but I just couldn't quite get it over the finish line.

### The actual solution

Hat tip to my fellow game players for introducing me to the solution. I took a description of the answer that I saw in the Discord and tried to implement it myself. Here's what I came up with.

The real answer lives in the interval between each timestamp of the ICMP ping request. First we need to grab the timestamps of the ICMP requests (not the replies).

`tshark -r exfil.pcap -Y "icmp.type==8" -T fields -e frame.time > timestamps.txt`

will pull out the full timestamp of each packet. Then we need to get just the time data out, let's use cut for that.

`cut -d " " -f 4 timestamps.txt > time_only.txt`

It honestly might have been simpler to leave the whole thing in place and parse it as a full datetime object, but with some back and forth with Python, I managed to digest this file into something usable.

Now what we need to do is take those time intervals and turn them into a binary string. If the interval is less than one second, put a 0 in the binary string, if it's more than one second, put a 1.

ChatGPT got me started, but it's absolute pants at debugging its own code when there are problems, so I ended up taking some of what it wrote and just hacking this together myself. Python was barfing on the precision of the fractional seconds, so I had to truncate those values in order to get it to behave.

```from datetime import datetime

def read_timestamps(file_path):
    with open(file_path, 'r') as file:
        timestamps = []
        for line in file:
            line = line.strip()
            # Truncate the microseconds to 6 digits to fit %f format
            truncated_line = line[:15]  # The first 15 characters should fit the format
            timestamps.append(datetime.strptime(truncated_line, "%H:%M:%S.%f"))
        return timestamps

def main():
    file_path = '/mnt/data/time_only.txt'
    timestamps = read_timestamps(file_path)
    
    binary_string = ""
    
    for i in range(1, len(timestamps)):
        interval = (timestamps[i] - timestamps[i - 1]).total_seconds()
        if interval < 1:
            binary_string += "0"
        else:
            binary_string += "1"
    
    print("Binary string:", binary_string)

if __name__ == "__main__":
    main()

```
It's ugly but it works and gets us the binary string.

```
011000110110010101100101001101100011001100110000011001010011000001100011011000010011001101100101001100010011001001100100011000010011011001100101001100000110001100111001001101000011001100110000001101000011001000110010001100010110001100110111011001010110001100110110001100010011011100110010001100100110010001100101001100010011011000110111011000110011001101100010001101000110010100110001001101100011001000111000001101010011011001100011011000100011100100110001001100010110001101100110001101100110010001100011001101100011001100110010001100110011000100110100001100110011010101100001001100010011001001100011001101110011001100110011001101010011001001100010011001100110000100111000001101100110010100110110001110000011011000110110001100010011010100110111001100110110000101100010
```

which we can then feed into cyberchef. The recipe is From Binary, AES decrypt with the iv and key we found in our recon.

And that's it! It's a really cool problem and I really wish I'd figured the last step out during the competition.
