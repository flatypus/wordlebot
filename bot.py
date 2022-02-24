import discord,random
from PIL import Image, ImageDraw, ImageFont
client = discord.Client()

@client.event
async def on_ready():
    global isrunning, wordle, allwords
    isrunning = wordle = False
    allwords = {}
    print(f'{client.user} has connected to Discord!')

def concath(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

def concatv(im1, im2):
    dst = Image.new('RGB', (min(im1.width, im2.width), im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

def makeGame(gamestate):
    global parsed
    w1 = Image.open('wordle1.png')
    w2 = Image.open('wordle2.png')
    w3 = Image.open('wordle3.png')
    images = {'1':w1,'2':w2,'3':w3}
    base = images[gamestate[0]]
    for i in range(1,5):
        base = concath(base,images[gamestate[i]])
    font = ImageFont.truetype('HelveticaNeue Bold.ttf', 64)
    for i in range(5):
        draw = ImageDraw.Draw(base)
        draw.text(((i*100)+27,8),parsed[i].upper(),(255,255,255),font=font)
    wpercent = 1481/500
    hsize = int((float(base.size[1])*float(wpercent)))
    base = base.resize((1481,hsize), Image.ANTIALIAS)
    return base

def makeImage(keyboard):
    font = ImageFont.truetype('HelveticaNeue Bold.ttf', 64)
    img = Image.open(R"wordlekeyboard.png")
    img1 = ImageDraw.Draw(img)  
    rows = [[17,7],[82,205],[231,403]]
    nums = [10,9,7]
    gap = [147,148,148]
    cols = [[129,131,132],[58,58,60],[181,159,59],[83,141,78]]
    letters = ["QWERTYUIOP","ASDFGHJKL","ZXCVBNM"]
    for n in range(3):
        x,y = rows[n]
        t = nums[n]
        g = gap[n]
        for i in range(t):
            shape = [(x+(g*i),y), (x+(g*i+138),y+174)]
            img1.rectangle(shape, fill=tuple(cols[keyboard[n][i]]))
            draw = ImageDraw.Draw(img)
            draw.text((x+(g*i)+48,y+43),letters[n][i],(255,255,255),font=font)
    return img

@client.event
async def on_message(message):
    global isrunning, wordle,word,accepted,guesses,keyboarddata,parsed,allwords
    if message.content == '!wordle':
        guesses = 0
        wordle=True
        with open('wordlewords.txt','r') as words:
            word = random.choice(words.read().strip().split())
            allwords[message.channel] = word
        with open('wordleguesses.txt','r') as accepted:
            accepted = accepted.read().strip().split()
        print(word)
        keyboarddata = {}
        for i in "qwertyuiopasdfghjklzxcvbnm":
            keyboarddata[i] = 0
        await message.channel.send("A five letter word has been generated. User !g [word] to guess")
    if '!g 'in message.content:
        if wordle:
            parsed = message.content.strip()[3:].lower()
            if parsed in accepted:
                guesses+=1
                letterin = []
                gamestate = ['','','','','']
                win=True
                for i in range(len(parsed)):
                    if parsed[i] == word[i]:
                        gamestate[i] = '3'
                        keyboarddata[parsed[i]] = 3
                        letterin.append(parsed[i])
                    else:
                        win=False
                for i in range(len(parsed)):
                    if parsed[i] not in letterin:
                        if parsed[i] in word:
                            gamestate[i] = '2'
                            if keyboarddata[parsed[i]]<2:
                                keyboarddata[parsed[i]] = 2
                            letterin.append(parsed[i])
                        else:
                            gamestate[i] = '1'
                            if keyboarddata[parsed[i]]<1:
                                keyboarddata[parsed[i]] = 1
                    else:
                        if parsed[i] in allwords[message.channel] and not parsed[i] == allwords[message.channel][i]:
                            gamestate[i] = '1'
                            if keyboarddata[parsed[i]]<1:
                                keyboarddata[parsed[i]] = 1
                keyboard = [[],[],[]]
                letters = "qwertyuiopasdfghjklzxcvbnm"
                for i in range(10):keyboard[0].append(keyboarddata[letters[i]])
                for i in range(10,19):keyboard[1].append(keyboarddata[letters[i]])
                for i in range(19,26):keyboard[2].append(keyboarddata[letters[i]])
                game = makeGame(gamestate)
                keyboardImg = makeImage(keyboard)
                concatv(game,keyboardImg).save('tmp.png')
                embed = discord.Embed() #creates embed
                file = discord.File("tmp.png", filename="image.png")
                embed.set_image(url="attachment://image.png")
                await message.channel.send(file=file, embed=embed)
                if win:
                    await message.channel.send(f'{allwords[message.channel]} was the right word. Guess counter: {guesses}')
                    wordle = False
            else:
                await message.channel.send(f"{parsed} is not in word list.")
        else:
            await message.channel.send("Use !wordle to start a new game!")
    if message.content == '!giveup':
        await message.channel.send(f"The word was {allwords[message.channel]}")
        wordle = False
client.run('YOUR CLIENT ID HERE')
